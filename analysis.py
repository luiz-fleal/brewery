import os
from collections.abc import Iterator

import polars as pl


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
    return pl.from_dicts([d for batch in data for d in batch], schema=schema).sort(by=["state_province", "city", "name"], descending=[False, False, False])


def create_census_dataframe(file_path: str, year: int) -> pl.DataFrame:
    df = pl.read_csv(
        os.path.abspath(file_path),
        encoding="utf-8-lossy",
        columns=["NAME", "STNAME", f"POPESTIMATE{year}"],
    )
    return df
