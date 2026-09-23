![CI](https://github.com/luiz-fleal/api-analysis-template/actions/workflows/ci.yml/badge.svg)

# Brewery Data Analysis

This is a personal project to enhance my data analysis skills.

The repository consists on an analysis of [Open Brewery DB's](https://www.openbrewerydb.org/) API data and governmental population census data to create a report showing cities with a low density of breweries/hab. Therefore, the data generated can be utilized by companies in the brewery industry to prospect for profitable cities to invest in new facilities.

# Cloning and Setup

Prerequisites:

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [US Population Data](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html)

Clone the repository and install the project dependencies, including the development dependencies:

```bash
git clone https://github.com/luiz-fleal/brewery.git
cd brewery
uv sync --dev
```

Run the project with:

```bash
uv run main.py
```

Run the test suite with:

```bash
uv run pytest
```

Get updated US population data from the above link in the Datasets -> United States subsections. It must be a .csv file and the relative file path must be passed as an argument when calling the function, as well as the desired year to analyze. Data for the year 2020 - 2025 is already provided in data/population-census.

# Usage

# Frameworks and Packages

The following frameworks and packages will be used for code function:
1. Polars:
	- Newer and more performant alternative to Pandas, written in Rust
	- Used for the data manipulation and analysis
2. HTTPX:
	- HTTP Client life cycle
	- Supports both synchronous and asynchronous execution
3. Tenacity:
	- Request retry logic with backoff to respect rate limits
4. Python Dotenv
	- Environment variable management

The following frameworks and packages will be used for code development:
1. Pytest:
	- Code maintenance and testability
2. Ruff:
	- Bug catching and code consistency
3. Respx:
	- HTTP transport layer mocking for testing functions that make requests