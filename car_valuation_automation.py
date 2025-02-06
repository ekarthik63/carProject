import re
import logging
import pandas as pd
import html
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Tuple, List, Dict
from retry import retry

# Website Configurations
WEBSITE_CONFIGS = {
    "motorway": {
        "base_url": "https://motorway.co.uk/",
        "search_flow": [
            {
                "action": "input",
                "locator": (By.CSS_SELECTOR, "input#vrm-input"),
                "keys": "{registration}\n"
            },
            {
                "wait_for": (By.CSS_SELECTOR, "h1.HeroVehicle__title")
            }
        ],
        "details": {
            "model": (By.CSS_SELECTOR, "h1.HeroVehicle__title"),
            "year": (By.CSS_SELECTOR, "ul.HeroVehicle__details li:first-child")
        }
    },
    "autotrader": {
        "base_url": "https://www.autotrader.co.uk/",
        "search_flow": [
            {
                "action": "click",
                "locator": (By.CSS_SELECTOR, "button[data-testid='toggle-button']"),
            },
            {
                "action": "input",
                "locator": (By.ID, "registration"),
                "keys": "{registration}"
            },
            {
                "action": "click",
                "locator": (By.CSS_SELECTOR, "button[data-testid='search-button']")
            },
            {
                "wait_for": (By.CSS_SELECTOR, "h1[data-testid='search-title']")
            }
        ],
        "details": {
            "model": (By.CSS_SELECTOR, "h1[data-testid='search-title']"),
            "year": (By.CSS_SELECTOR, "li[data-testid='spec-year']")
        }
    },
    "confused": {
        "base_url": "https://www.confused.com/car-insurance/your-car",
        "search_flow": [
            {
                "action": "input",
                "locator": (By.ID, "Auto_Reg"),
                "keys": "{registration}"
            },
            {
                "action": "click",
                "locator": (By.ID, "btnGetCarDetails")
            },
            {
                "wait_for": (By.CSS_SELECTOR, "div.vehicle-details")
            }
        ],
        "details": {
            "model": (By.CSS_SELECTOR, "span.vehicle-model"),
            "year": (By.CSS_SELECTOR, "span.vehicle-year")
        }
    }
}

# Global Constants
CONFIG = {
    "INPUT_PATTERN": r'\b[A-Z]{2}\d{2} [A-Z]{3}\b',
    "TIMEOUT": 30,
    "RETRIES": 2,
    "BROWSER_OPTIONS": [
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1920,1080",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled"
    ]
}

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('car_valuation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BrowserManager:
    """Context manager for WebDriver handling"""
    def __init__(self):
        self.driver = None
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        for opt in CONFIG["BROWSER_OPTIONS"]:
            self.options.add_argument(opt)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

    def __enter__(self):
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
            self.driver.implicitly_wait(10)
            return self.driver
        except WebDriverException as e:
            logging.error(f"Browser initialization failed: {str(e)}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

class WebsiteValidator:
    """Handles validation for different car valuation websites"""
    def __init__(self, driver, website_config):
        self.driver = driver
        self.config = website_config
        self.wait = WebDriverWait(driver, CONFIG["TIMEOUT"])

    def _execute_action(self, step, registration):
        if step["action"] == "input":
            element = self.wait.until(EC.element_to_be_clickable(step["locator"]))
            element.clear()
            element.send_keys(step["keys"].format(registration=registration))
        elif step["action"] == "click":
            element = self.wait.until(EC.element_to_be_clickable(step["locator"]))
            element.click()
        elif "wait_for" in step:
            self.wait.until(EC.presence_of_element_located(step["wait_for"]))

    @retry(WebDriverException, tries=CONFIG["RETRIES"], delay=2, backoff=2)
    def search_registration(self, registration):
        """Execute search flow for the website"""
        try:
            self.driver.get(self.config["base_url"])
            for step in self.config["search_flow"]:
                self._execute_action(step, registration)
            return True
        except WebDriverException as e:
            logging.error(f"Search failed on {self.config['base_url']}: {str(e)}")
            return False

    def get_vehicle_details(self):
        """Extract vehicle details from results page"""
        try:
            model = self.wait.until(
                EC.visibility_of_element_located(self.config["details"]["model"])
            ).text.strip()

            year = self.wait.until(
                EC.visibility_of_element_located(self.config["details"]["year"])
            ).text.strip()

            return model, year
        except WebDriverException:
            logging.warning("Failed to extract vehicle details")
            return "Not Found", "N/A"

class DataHandler:
    """Handles data loading and processing"""
    @staticmethod
    def load_registrations(file_path: str) -> List[str]:
        with open(file_path, 'r') as f:
            content = f.read()
        return re.findall(CONFIG["INPUT_PATTERN"], content)

    @staticmethod
    def load_expected_data(file_path: str) -> Dict[str, Tuple[str, str]]:
        df = pd.read_csv(file_path)
        return {row['VARIANT_REG']: (row['MAKE_MODEL'], str(row['YEAR'])) for _, row in df.iterrows()}

class TestReporter:
    """Generates test reports"""
    @staticmethod
    def generate_html_report(results: List[Dict], filename: str = "report.html"):
        html_content = """<html><head><title>Car Valuation Test Report</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .pass {{ background-color: #dfffdf; }}
                .fail {{ background-color: #ffe5e5; }}
                .warning {{ background-color: #fff3cd; }}
            </style>
            </head><body>
            <h1>Car Valuation Test Report</h1>
            <p>Generated at: {timestamp}</p>
            <table>
                <tr>
                    <th>Website</th>
                    <th>Registration</th>
                    <th>Expected Model</th>
                    <th>Actual Model</th>
                    <th>Expected Year</th>
                    <th>Actual Year</th>
                    <th>Status</th>
                </tr>
                {rows}
            </table></body></html>"""

        rows = []
        for res in results:
            row_class = "pass" if res['status'] == "Pass" else "fail" if res['status'] == "Fail" else "warning"
            rows.append(f"""
            <tr class="{row_class}">
                <td>{html.escape(res['website'])}</td>
                <td>{html.escape(res['reg'])}</td>
                <td>{html.escape(res['exp_model'])}</td>
                <td>{html.escape(res['act_model'])}</td>
                <td>{html.escape(res['exp_year'])}</td>
                <td>{html.escape(res['act_year'])}</td>
                <td>{res['status']}</td>
            </tr>""")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content.format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                rows="\n".join(rows)
            ))
        logging.info(f"HTML report generated: {filename}")

def validate_registration(driver, website_name, reg, expected_data):
    """Validate registration against a specific website"""
    result = {
        'website': website_name,
        'reg': reg,
        'exp_model': "N/A",
        'exp_year': "N/A",
        'act_model': "N/A",
        'act_year': "N/A",
        'status': "Error"
    }

    try:
        config = WEBSITE_CONFIGS[website_name]
        validator = WebsiteValidator(driver, config)

        # Get expected values
        exp_data = expected_data.get(reg, ("Not Found", "N/A"))
        result['exp_model'], result['exp_year'] = exp_data

        if validator.search_registration(reg):
            act_model, act_year = validator.get_vehicle_details()
            result.update({
                'act_model': act_model,
                'act_year': act_year,
                'status': "Pass" if (act_model == exp_data[0] and act_year == exp_data[1]) else "Fail"
            })
        else:
            result['status'] = "Search Failed"

    except Exception as e:
        logging.error(f"Validation error on {website_name}: {str(e)}")
        try:
            if driver.service.is_connectable():
                filename = f"error_{website_name}_{reg.replace(' ', '_')}.png"
                driver.save_screenshot(filename)
        except Exception as screenshot_error:
            logging.warning(f"Failed screenshot: {screenshot_error}")

    return result

def main():
    input_regs = DataHandler.load_registrations("car_input - V5.txt")
    expected_data = DataHandler.load_expected_data("car_output - V5.txt")
    results = []

    with BrowserManager() as driver:
        for website in WEBSITE_CONFIGS:
            for reg in input_regs:
                result = validate_registration(driver, website, reg, expected_data)
                results.append(result)
                logging.info(f"Completed {website} - {reg}: {result['status']}")

    TestReporter.generate_html_report(results)
    pd.DataFrame(results).to_csv("validation_results.csv", index=False)
    logging.info("Test execution completed")

if __name__ == "__main__":
    main()