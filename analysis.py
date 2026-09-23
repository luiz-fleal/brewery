from collections.abc import Iterator

import polars as pl


async def create_dataframe(data: Iterator[list[dict]]) -> pl.DataFrame:
    schema = {
        "id": pl.Utf8,
        "name": pl.Utf8,
        "brewery_type": pl.Utf8,
        "address_1": pl.Utf8,
        "address_2": pl.Utf8,
        "address_3": pl.Utf8,
        "city": pl.Utf8,
        "state_province": pl.Utf8,
        "postal_code": pl.Utf8,
        "country": pl.Utf8,
        "longitude": pl.Float64,
        "latitude": pl.Float64,
        "phone": pl.Utf8,
        "website_url": pl.Utf8,
        "state": pl.Utf8,
        "street": pl.Utf8,
    }
    return pl.from_dicts([d for batch in data for d in batch], schema=schema)
