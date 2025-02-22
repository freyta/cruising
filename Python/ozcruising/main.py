#!/usr/bin/python3

import requests
import os
import json
import argparse
from mappings import SHIPS, CRUISE_LINES, PORTS, REGIONS
from row_extractor import fetch_cruises_in_batches
import re 

DIR = os.path.dirname(os.path.realpath(__file__))

def validate_range(value):
    """Validate that the range input is in the correct format (e.g., '2-5')."""
    if not re.match(r'^\d+-\d+$', value):
        raise argparse.ArgumentTypeError("Range must be in the format 'min-max' (e.g., 2-5)")
    
    min_val, max_val = map(int, value.split('-'))
    if min_val >= max_val:
        raise argparse.ArgumentTypeError("The first number must be smaller than the second number in the range.")

    return value


def get_mapped_value(arg_value, mapping_dict, name):
    """Helper function to process and validate mapped values."""
    if arg_value == "-111":
        return "-111"
    if arg_value == "0":
        return "0"
    
    if isinstance(arg_value, list):
        arg_value = " ".join(arg_value)  # Join if it's a list

    # Lookup mapped value
    lower_mapping_dict = {k.lower(): v for k, v in mapping_dict.items()}
    mapped_value = lower_mapping_dict.get(arg_value.lower())

    if mapped_value is None:
        print(f"Invalid {name}: {arg_value}. Please try again.")
        exit(1)

    return mapped_value

if __name__ == "__main__":
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        prog='OzCruising Searcher',
        description='A script to search OzCruising.com.au with refined parameters. '
                    'Results are output as a JSON file.'
    )

    # General arguments
    parser.add_argument('--origin', nargs="+", default="-111", help="Port where the cruise originates.")
    parser.add_argument('--arrival', nargs="+", default="-111", help="Port where the cruise ends.")
    parser.add_argument('--region', nargs="+", default="-111", help="The region you want to sail.")
    parser.add_argument('--cruise_line', nargs="+", default="0", help="The cruise line you want to sail on.")
    parser.add_argument('--ship', nargs="+", default="-111", help="The cruise ship you want to sail on.")

    # Month & Year must be provided together
    arg_group = parser.add_argument_group('Required Together')
    arg_group.add_argument('--month', type=int, default=-111, help="The month you want to sail. Jan is 1, Feb is 2, etc.")
    arg_group.add_argument('--year', type=int, default=-111, help="The year you want to sail on (e.g., 2025, 2026).")

    # Create a mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--days', type=int, help="The number of single days you want to cruise.")
    group.add_argument('-r', '--range', type=validate_range, help="The range of days you want to travel (e.g., 3-7).")

    # Parse arguments
    args = parser.parse_args()

    # Validate month and year requirement
    if (args.month == -111) != (args.year == -111):  # Only one provided
        parser.error("Both --month and --year must be provided together.")

    # Extract argument values
    origin, arrival, region, cruise_line, ship, month, year = (
        args.origin, args.arrival, args.region, args.cruise_line, args.ship, args.month, args.year
    )

    cruise_line = get_mapped_value(args.cruise_line, CRUISE_LINES, "cruise line")
    ship = get_mapped_value(args.ship, SHIPS, "ship")
    origin = get_mapped_value(args.origin, PORTS, "origin")
    arrival = get_mapped_value(args.arrival, PORTS, "arrival")
    mapped_region = get_mapped_value(args.region, REGIONS, "region")

    # If we have chosen specific days or a day range
    if args.days:
        days = f"{args.days}/{args.days}"
    elif args.range:
        min_days, max_days = map(int, args.range.split("-"))
        # We can't have 0 as the minimum amount of days because we get no results.
        if min_days == 0:
            min_days = 1
            
        days = f"{max_days}/{min_days}"
        


    # Build the URL
    ozcruising_url = f"https://www.ozcruising.com.au/searchcruise/bysearchbar/{cruise_line}/{month}/{year}/{origin}/true/{days}/{mapped_region}/{ship}/{region.title()}/{arrival}"

    # Setup request session
    POST_URL = "https://www.ozcruising.com.au/cruisecardapi/renderforpage"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referrer": ozcruising_url,
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.session()
    session.headers.update(HEADERS)
    response = session.get(ozcruising_url)

    # Check response validity
    if "data-oz-cruise-codes=" not in response.text:
        print("No cruises found or unexpected response format.")
        exit(1)

    # Extract cruise codes
    cruise_codes = response.text.split("data-oz-cruise-codes=")[1].split("\"")[1].split(",")
    print(f"Found {len(cruise_codes)} cruises")

    # Fetch cruise details
    cruises = fetch_cruises_in_batches(cruise_codes, session, POST_URL, HEADERS)

    # Format output data
    formatted_data = [
        {
            "date": item[6],  # Departure date
            "dep": item[5].replace("Departing ", ""),  # Extract departure location
            "title": item[1],  # Cruise title/destination
            "ship": item[8],  # Ship name
            "price": item[2],  # Total price
            "nights": item[0],  # Number of nights
            "price_per_night": item[3],  # Price per night
        }
        for item in cruises
    ]
    
    with open(f"{DIR}/cruises.json", "w") as f:
        json.dump(formatted_data, f, indent=2)