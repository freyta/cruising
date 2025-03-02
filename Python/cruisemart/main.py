import os
import json
import random
import string
from time import time
from uuid import uuid4
import requests

DIR = os.path.dirname(os.path.realpath(__file__))

def generate_random_string(length):
    """
    Generates a random string of the specified length using uppercase letters,
    lowercase letters, and digits.

    Args:
        length (int): The length of the random string to generate.
    
    Returns:
        str: A randomly generated string.
    """
    
    # Define the character set: uppercase letters, lowercase letters, and digits
    chars = string.ascii_letters + string.digits
    
    # Return the randomly generated string by selecting random characters from 'chars'
    return ''.join(random.choice(chars) for _ in range(length))


def encode_timestamp(num) -> str:
    """
    Encodes a given timestamp (epoch time).

    Encoding Logic:
    - Converts each digit of the number to a character.
    - If the digit is at an even index, it is shifted by `66` in ASCII.
    - If the digit is at an odd index, it is shifted by `67` in ASCII.

    Args:
        num (int): The timestamp in epoch.
    Returns:
        str: The encoded timestamp as a string.
    """
    
    result = ""
    # Convert the number to a string to iterate over each digit
    num_str = str(num)

    # Loop over each character in the string representation of num
    for i, digit in enumerate(num_str):
        # Convert the digit character to an integer
        digit_int = int(digit)
        # Determine ASCII shift based on index position
        ascii_shift = 66 if i % 2 == 0 else 67
        # Convert to ASCII character by shifting the digit
        encoded_char = chr(digit_int + ascii_shift)
        # Append the encoded character to the result string
        result += encoded_char

    # Return the final encoded string
    return result

def generate_unique_tid():
    """
    Generate a unique TID from a given timestamp.

    Returns:
        str: Generated unique TID
    """

    # Get the timestamp
    timestamp = int(time() * 1000)
    # Generate 5 random characters
    random_str = generate_random_string(5)
    # Encode our timestamp
    encoded_timestamp = encode_timestamp(timestamp)

    return (
        random_str +
        encoded_timestamp[1] +
        encoded_timestamp +
        random_str[2] +
        encoded_timestamp[4]
    )

import requests

def fetch_cruise_data(headers, json_data, page_size=50):
    """
    Fetch cruise data from the API with pagination.

    Args:
        headers (dict): HTTP headers for the request.
        json_data (dict): JSON payload for the request.
        page_size (int): Number of results per page.

    Returns:
        list: List of cruises.
    """
    # Create an empty list to store the retrieved cruise data
    cruise_list = []
    # Start from the first page (page index 0)
    page = 0
    total_results = None

    # Continue fetching data until all cruises are retrieved
    while True:
        # If total_results is known, adjust the page_size to avoid unnecessary requests
        if total_results is not None:
            remaining = total_results - len(cruise_list)
            
            if remaining <= 0:
                # Stop fetching if we have all available results
                break
            # Ensure we don't request more than needed
            page_size = min(page_size, remaining)

        # Construct the API URL with necessary query parameters
        url = (
            f"https://cruisesearch.cruisemart.com.au/nitroapi/v2/cruise?"
            f"&sortColumn=departureDateTime&sortOrder=asc&includeFacets=uniqueId"
            f"&pageSize={page_size}&pageStart={page}&fetchFacets=true"
            f"&groupByItineraryId=true&applyExchangeRates=true"
            f"&ignoreCruiseTaxInclusivePref=true&requestSource=1"
        )

        try:
            # Send a POST request to the API
            response = requests.post(url, headers=headers, json=json_data)
            # Raise an HTTPError if the response contains an error status code
            response.raise_for_status()
            # Parse the JSON response
            data = response.json()

            # Set total_results on the first API call.
            if total_results is None:
                total_results = data['data']['total']
                print(f"Found {total_results} total results")

            # If the API request is successful, process and store the cruise data
            if data['isSucceed']:
                # Process the cruise list
                cruises = process_cruise_data(data['data']['list'])
                # Append new cruises to the main list
                cruise_list.extend(cruises)

                # If we haven't retrieved all the data, fetch the next page
                if len(cruise_list) < total_results:
                    # Increment page number for the next request
                    page += 1
                    print(f"Fetching page {page}...")
                else:
                    # Stop fetching once all cruises are retrieved
                    break
            else:
                # Break if there's an error in our request
                break

        except requests.RequestException as e:
            # Print the error message if we get one, and what page we are on
            print(f"Error fetching page {page}: {e}")
            break 

    # Return the full list of cruises
    return cruise_list

def process_cruise_data(cruise_list):
    """
    Extract and process cruise data from the API response, including all cabin types.
    Handles cases where price data might be missing or empty.

    Args:
        cruise_list (List[Dict[str, Any]]): A list of cruise data dictionaries from the API.

    Returns:
        List[Dict[str, Any]]: A sorted list of processed cruises with their cabin options, sorted by price per night.
    """
    processed_cruises = []
    
    for cruise in cruise_list:
        try:
            # First, verify that we have the basic required data
            code = cruise['code']
            name = cruise['cruiseTourName']
            
            # Check if prices exist and are not empty
            if not cruise.get('prices') or not cruise['prices']:
                # Skip this cruise if no prices are available
                continue
                
            # Check if packages exist and have required data
            if not cruise.get('packages') or not cruise['packages']:
                continue
                
            currency = cruise['prices'][0]['currencyCode']
            dep_date = cruise['packages'][0]['startDateTime']
            nights = cruise['packages'][0]['cruiseDuration']
            
            # Verify we have price items to process
            if not cruise['packages'][0].get('prices') or \
               not cruise['packages'][0]['prices'] or \
               not cruise['packages'][0]['prices'][0].get('items'):
                continue
            
            # Find tax and port charges
            additional_charges = 0
            for item in cruise['packages'][0]['prices'][0]['items']:
                if item.get('code') == 'CruiseTax':
                    additional_charges += item.get('value', 0)
            
            # Process each cabin type
            for item in cruise['packages'][0]['prices'][0]['items']:
                # Skip non-cabin items (tax and port charges)
                if item.get('code') in ['CruiseTax', 'PortCharge']:
                    continue
                
                # Ensure we have a valid price value
                if not item.get('value'):
                    continue
                
                # Calculate total price including charges for this cabin
                cabin_price = item['value'] + additional_charges
                ppn = round(cabin_price / nights, 2)
                
                if item.get('code') != 'IncludedFeesInFare':
                    processed_cruises.append({
                        "code": code,
                        "name": name,
                        "cabin": item.get('name', 'Unknown Cabin Type'),
                        "price": cabin_price,
                        "currency": currency,
                        "dep_date": dep_date,
                        "nights": nights,
                        "ppn": ppn
                    })
                
        except (IndexError, KeyError) as e:
            # If any error occurs while processing this cruise, skip it
            continue
    
    # Sort the processed cruises by price per night
    return sorted(processed_cruises, key=lambda x: x['ppn'])

def display_cruise_results(cruise_list):
    """
    Display the sorted cruise results.

    Args:
        cruise_list (List[Dict[str, str]]): A list of cruise data dictionaries.

    Returns:
        None
    """
    # Sort the cruises by currency and cheapest price per night
    sorted_cruises = sorted(cruise_list, key=lambda x: (x['currency'], x['ppn']), reverse=False)
    for cruise in sorted_cruises:
        # Print it out
        print(
            f"[{cruise['name']}] ({cruise['code']} - {cruise['nights']} nights) = "
            f"${cruise['price']}{cruise['currency']} (${cruise['ppn']}) for {cruise['cabin']} -------- {cruise['dep_date']}"
        )
    
    # And save it as a JSON file
    with open(f"{DIR}/cruises.json", "w") as f:
        json.dump(sorted_cruises, f, indent=2)

    print(f"\nTotal cruises processed: {len(cruise_list)}")

if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://cruisesearch.cruisemart.com.au/swift/cruise',
        'Origin': 'https://cruisesearch.cruisemart.com.au',
        'DNT': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'siteItemId': '126818',
        'DeviceType': 'Desktop',
        'languageId': '7',
        'UniqueTId': generate_unique_tid(),
        'Priority': 'u=4',
    }

    json_data = {
        'filters': [
            {
                'key': 'departurePortCode',
                'values': ['SYD'],
            },
            {},
        ],
    }

    cruises = fetch_cruise_data(headers, json_data)
    display_cruise_results(cruises)
