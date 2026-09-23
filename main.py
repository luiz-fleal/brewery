import argparse
import logging
import sys

from analysis import create_dataframe
from client import APIClient
from config import AVAILABLE_COUNTRIES, BASE_URL
from fetch import fetch_all
from fetcherror import FetchError

logger = logging.getLogger(__name__)

def main(args: argparse.Namespace) -> None:
    print(f"starting requests for breweries in {args.country}")
    with APIClient(BASE_URL) as client:
        data = fetch_all(
            client=client, 
            country=args.country, 
            page_size=args.page_size
        )
        df = create_dataframe(data)
    print(df)

def run () -> int:
    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--country", type=str, choices=AVAILABLE_COUNTRIES, required=True)
    parser.add_argument("-ps", "--page_size", type=int, default=200)
    args = parser.parse_args()

    # logging and client setup
    logging.basicConfig(
        filename="brewery.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filemode="w",
    )

    try:
        main(args)
    except KeyboardInterrupt:
        return 130
    except FetchError as e:
        logger.error("fetch error: %s", e)
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(run())