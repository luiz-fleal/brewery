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

Get updated US population data from [here](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) in the Datasets -> United States subsections. It must be a .csv file and the relative file path must be passed as an argument when calling the function, as well as the desired year to analyze. Data for the year 2020 - 2025 is already provided in data/population-census.

# Usage

Run the project with:

```bash
uv run main.py
```

Run the test suite with:

```bash
uv run pytest
```

The analysis will be output to data/merged_brewery_census.csv (an abridged version will also be printed to stdout for quick visualization)

# Data Quality Findings

During analysis, I identified significant quality issues in both source datasets that undermine confidence in the final results:

- **Population census data:** 49664 out 83153 of city records were found as duplicates after cleaning to match BrewerDB's data
- **Brewery API data:** incomplete coverage, with many breweries missing from the dataset, e.g. only 13 breweries being reported across New York City
- **Brewery API data:** inconsistent and incorrect city/state name formatting, making reliable joins against census data difficult, e.g. some entries having city as Florida and state province as New York

Because of this, the resulting density metrics aren't reliable enough to support the prospecting use case described above.

**Lesson learned:** I moved into the analysis pipeline before validating the source data. In future projects, I'd run explicit data quality checks first — duplicate detection, completeness checks, and referential integrity between join keys (like city/state names) before building any downstream analysis on top of the data.

# What Worked Well

Despite the data issues, the client layer responsible for fetching data from the Brewery API turned out solid:

- **Robust retry logic:** requests handle failures on a case-by-case basis, with automatic retries and backoff (via Tenacity) tailored to the specific error encountered, rather than a one-size-fits-all retry policy.
- **Current limitation:** the client is currently synchronous due to pagination limitations of the API. Moving to an async implementation (HTTPX already supports it) would be a natural next step to improve throughput when paginating through large result sets.

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

The following frameworks and packages will be used for code development:
1. Pytest:
	- Code maintenance and testability
2. Ruff:
	- Bug catching and code consistency
3. Respx:
	- HTTP transport layer mocking for testing functions that make requests