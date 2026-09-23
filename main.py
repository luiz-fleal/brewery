import argparse
import logging

from client import APIClient
from config import BASE_URL


def main() -> None:
	# arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--country", type=str)
	parser.add_argument("-ps", "--page_size", type=int, default=50)
	args = parser.parse_args()

	# logging and client setup
	logging.basicConfig(filename="brewery.log", level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	client = APIClient(BASE_URL)

if __name__ == "__main__":
	main()
