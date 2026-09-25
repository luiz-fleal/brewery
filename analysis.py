import logging
import os
from collections.abc import Iterator

import polars as pl

logger = logging.getLogger(__name__)


def create_brewery_dataframe(data: Iterator[list[dict]]) -> pl.DataFrame:
    schema = {
        "id": pl.Utf8,
        "name": pl.Utf8,
        "brewery_type": pl.Utf8,
        "city": pl.Utf8,
        "state_province": pl.Utf8,
        "phone": pl.Utf8,
        "website_url": pl.Utf8,
    }
    df = pl.from_dicts([d for batch in data for d in batch], schema=schema)
    return df


def create_census_dataframe(file_path: str, year: int) -> pl.DataFrame:
    df = (
        pl.read_csv(
            os.path.abspath(file_path),
            encoding="utf-8-lossy",
            columns=["NAME", "STNAME", f"POPESTIMATE{year}"],
        )
        .rename(
            {
                "NAME": "city",
                "STNAME": "state_province",
                f"POPESTIMATE{year}": "population",
            }
        )
        .with_columns(
            pl.col("city").str.replace(pattern="(city|town|village|County)$", value="")
        )
    )

    # validation with log warnings
    null_population = df.filter(pl.col("population").is_null())
    if len(null_population) > 0:
        logger.warning(
            f"Found {len(null_population)} rows with null population in census data for year {year}."
        )
    nan_population = df.filter(pl.col("population").is_nan())
    if len(nan_population) > 0:
        logger.warning(
            f"Found {len(nan_population)} rows with NaN population in census data for year {year}."
        )
    duplicates = df.is_duplicated()
    if duplicates.sum() > 0:
        logger.warning(
            f"Found {duplicates.sum()} duplicate rows in census data for year {year}."
        )
    return df.filter(~duplicates)


def merge_brewery_and_census_data(
    brewery_df: pl.DataFrame, census_df: pl.DataFrame
) -> pl.DataFrame:
    merged_df = (
        brewery_df.lazy()
        .group_by(["city", "state_province"])
        .len("brewery_count")
        .join(census_df.lazy(), on=["city"], how="inner")
        .with_columns(
            (pl.col("population") / pl.col("brewery_count")).alias(
                "population_per_brewery"
            )
        )
        .select(
            [
                "city",
                "state_province",
                "brewery_count",
                "population",
                "population_per_brewery",
            ]
        )
        .collect()
    )
    merged_df.write_csv("data/merged_brewery_census.csv")
    return merged_df
