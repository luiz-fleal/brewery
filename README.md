![CI](https://github.com/luiz-fleal/api-analysis-template/actions/workflows/ci.yml/badge.svg)

# Brewery Data Analysis

This is a personal project to enhance my data analysis skills.

This project consists on an analysis of [Open Brewery DB's](https://www.openbrewerydb.org/) API data and governmental population census data to create a report showing cities with a low density of breweries/hab. Therefore, the data generated can be utilized by companies in the brewery industry to prospect for profitable cities to invest in new facilities.

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