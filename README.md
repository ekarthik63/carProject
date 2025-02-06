

## Overview

This project is a Python-based automation framework that extracts car registration numbers from an input file, fetches their valuation from a third-party website, and compares the results with a predefined expected output. The framework is designed to be modular and extendable for future enhancements.

## Features

- Reads vehicle registration numbers from an input file (`car_input.txt`).
- Uses browser automation to fetch valuation details from a car valuation website (e.g., [Motorway](https://motorway.co.uk/)).
- Compares the retrieved data against the expected results stored in `car_output.txt`.
- Highlights discrepancies between actual and expected valuations.
- Designed for easy expansion, supporting additional input files and multiple valuation sources.

---

## Project Structure

```
CarProject/
│── automation/
│   ├── car_scraper.py         # Automates car valuation extraction
│   ├── comparator.py          # Compares extracted results with expected output
│   ├── config.py              # Configurations and settings
│   ├── utils.py               # Utility functions
│── data/
│   ├── car_input.txt          # Contains vehicle registration numbers
│   ├── car_output.txt         # Expected results for validation
│── tests/
│   ├── test_automation.py     # Unit tests for automation components
│── requirements.txt           # Dependencies
│── README.md                  # This documentation
│── run.py                      # Main script to execute the automation
```

---

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- pip (Python package manager)
- Google Chrome or Mozilla Firefox (for browser automation)
- ChromeDriver or GeckoDriver (depending on the browser)

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/CarProject.git
   cd CarProject
   ```

2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

---

## Usage

### Running the Automation

To execute the automation process:

```sh
python run.py
```

The script will:
- Read car registration numbers from `car_input.txt`.
- Fetch car valuation details from [Motorway](https://motorway.co.uk).
- Compare results with `car_output.txt`.
- Display a summary of mismatches, if any.

### Expected Input and Output

#### Input (`car_input.txt`)

Example content:

```
There are multiple websites available to check current car value in United Kingdom.
The best of all is motorway.co.uk for instant valuation.
Checking example BMW with registration AD58 VNF the value of the car is roughly around £3000.
However car with registration BW57 BOW is not worth much in the current market.
There are multiple cars available higher than £10k with registrations KT17DLX and SG18 HTN.
```

#### Output (`car_output.txt`)

Expected format:

```
VARIANT_REG,MAKE_MODEL,YEAR
SG18 HTN,Volkswagen Golf SE Navigation TSI EVO,2018
AD58 VNF,BMW 120D M Sport,2008
BW57 BOF,Toyota Yaris T2,2008
KT17 DLX,Skoda Superb Sportline TDI S-A,2017
```

---

## Detailed Steps

### 1. Extract Vehicle Registration Numbers

- The script scans `car_input.txt` to identify valid UK vehicle registration numbers.
- It uses regular expressions to extract patterns that match standard UK registration formats.

### 2. Fetch Car Valuation Data

- Using **Selenium WebDriver**, the script:
  - Navigates to [Motorway](https://motorway.co.uk/).
  - Enters each registration number.
  - Extracts the displayed valuation and vehicle details.

### 3. Compare Results

- The extracted data is compared against `car_output.txt`.
- If there’s a mismatch in the car model, year, or valuation, the test is marked as failed.
- A summary of mismatches is displayed in the console.

---

## Customization

### Adding More Input Files

- Place additional input files in the `data/` folder.
- Modify `config.py` to specify which file to use.

### Changing the Valuation Website

- Update `car_scraper.py` to use a different website.
- Ensure the correct HTML elements are targeted for data extraction.

---

## Error Handling

- **Missing Registration Numbers**: If an input file does not contain valid registration numbers, an error is logged.
- **Website Downtime**: If the valuation site is unreachable, the script retries up to 3 times before failing.
- **Unexpected HTML Changes**: If the structure of the valuation website changes, the scraper may break and need updating.

---

## Running Tests

Run the unit tests with:

```sh
pytest tests/
```

Tests include:
- Extraction of registration numbers.
- Web scraping logic.
- Comparison functionality.

---

## Future Improvements

- **Support for More Valuation Websites**: Expand to include [AutoTrader](https://www.autotrader.co.uk/) and [Confused.com](https://www.confused.com/).
- **Database Storage**: Store past valuations in a database for historical analysis.
- **GUI Interface**: Build a simple web-based or desktop UI for ease of use.
- **Logging & Reporting**: Generate detailed reports in HTML or CSV format.

---

## Author

- **Your Name**
- Email: your.email@example.com
- GitHub: [your-github](https://github.com/your-github)

---

This README provides a clear guide on setting up, running, and maintaining the car valuation automation project. Let me know if you need modifications or additional details! 🚀