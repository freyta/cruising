import requests
from .mappings import SHIP_MAPPING, PORT_MAPPING
import os
import uuid



def get_cheapest_price(cruise_code, cruise_codes):
    """Get the cheapest price for a given cruise code from cruise_codes data."""
    relevant_prices = []

    # Loop through each product in cruise_codes
    for product in cruise_codes['products']:
        # Check if the 'cruises' key exists in the product
        if 'cruises' in product:
            # Loop through each cruise in the 'cruises' list
            for cruise in product['cruises']:
                # Check if the cruise ID matches the provided cruise_code
                if cruise.get('id') == cruise_code:
                    # If we find the cruise, process the pricing
                    pricing = cruise.get('pricing', {})
                    if 'fares' in pricing:
                        # Loop through each fare in the 'fares' list
                        for fare in pricing['fares']:
                            # Loop through each category within fares
                            for category in fare['categories']:
                                for guests in category['guests']:
                                    if guests['id'] == 1:
                                        obc = guests.get('obc', 0)
                                        relevant_prices.append([guests['fare'], f"${obc} per person"])
        else:
            print(f"Skipping invalid product: {product}")
    
    # Sort relevant_prices by the fare (first element in each sublist)
    relevant_prices.sort(key=lambda x: x[0])

    # Return the cheapest price or None if no prices were found
    return relevant_prices[0] if relevant_prices else None



def process_cruises(princess_products, cruise_codes):
    # Prepare a dictionary to store the results
    cruises_dict = {}

    # Iterate through princess_products to extract cruise IDs and details
    for product in princess_products['products']:
        # Iterate through the cruises in the product
        for cruise in product.get('cruises', []):
            cruise_id = cruise['voyage']['id']  # Access voyage code
            cruise_details = {
                'name': product['name'],
                'voyage_details': cruise['voyage']
            }

            # Find the cheapest price for this cruise ID
            cheapest_price = get_cheapest_price(cruise_id, cruise_codes)
            cruise_details['cheapest_price'] = cheapest_price

            # Add to the dictionary
            cruises_dict[cruise_id] = cruise_details

    # Print the result
    
    scraped_cruises = []
    for cruise_id, details in cruises_dict.items():
        if details['cheapest_price']:
            ship = SHIP_MAPPING.get(details['voyage_details']['ship']['id'])
            dep = PORT_MAPPING.get(details['voyage_details']['startPortId'])
            scraped_cruises.append({
                    "date": details['voyage_details']['sailDate'],
                    "dep": dep,
                    "title": details['name'],
                    "ship": ship,
                    "price": details['cheapest_price'][0],
                    "nights": details['voyage_details']['duration'],
                    "price_per_night": round(details['cheapest_price'][0] / details['voyage_details']['duration'], 2),
                    "obc": details['cheapest_price'][1]
                    })

    return sorted(scraped_cruises, key=lambda x: x['price_per_night'], reverse=True)


def get_cruises():
    # Specify the paths to the JSON files
    DIR = os.path.dirname(os.path.realpath(__file__))
    
    # Set up some headers
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.princess.com/',
    'AppId': f'{{"agencyId":"DIRECTAU","cruiseLineCode":"PCL","sessionId":{uuid.uuid4()},"systemId":"PB","gdsCookie":"CO=AU"}}',
    'ProductCompany': 'PC',
    'BookingCompany': 'PA',
    'ReqSrc': 'W',
    'pcl-client-id': '32e7224ac6cc41302f673c5f5d27b4ba',
    'Origin': 'https://www.princess.com',
    'DNT': '1',
    }

    params = {
    'agencyCountry': 'AU',
    'cruiseType': 'C',
    'voyageStatus': 'A',
    'webDisplay': 'Y',
    'promoFilter': 'all',
    'light': 'false',
    }

    princess_products = requests.get(
    'https://gw.api.princess.com/pcl-web/internal/resdb/p1.0/products',
    params=params,
    headers=headers,
    ).json()

    params = {
  "booking": {
    "bookingAgency": {
      "id": "DIRECTAU",
      "address": {
        "stateId": "NSW",
        "countryId": "AU"
      },
      "phones": [
        {
          "phoneTypeId": "W",
          "number": "9200000001"
        },
        {
          "phoneTypeId": "F",
          "number": "9200000001"
        }
      ],
      "gsaInd": "Y",
      "gsaDefaultHomeCity": "SYD",
      "creditCardChargeFeesFlag": "Y",
      "borderCountries": [
        "AU",
        "NC"
      ],
      "currencies": [
        {
          "id": "AUD"
        }
      ],
      "collectDirectInfoFlag": "N",
      "dsms": [
        {
          "year": "2022",
          "region": "90",
          "district": "1Z",
          "dsmManager": "DIRECT"
        },
        {
          "year": "2023",
          "region": "90",
          "district": "1Z",
          "dsmManager": "DIRECT"
        }
      ],
      "gdsName": "VIEWDATA SUBSCRIBER",
      "commissions": [
        {
          "year": "2022",
          "associationCode": "DIRT",
          "association": "DIRECTS",
          "salesProgram": "P0",
          "typeFlag": "DIR"
        },
        {
          "year": "2023",
          "associationCode": "DIRT",
          "association": "DIRECTS",
          "salesProgram": "P0",
          "typeFlag": "DIR"
        },
        {
          "year": "2024",
          "associationCode": "DIRT",
          "association": "DIRECTS",
          "salesProgram": "P0",
          "typeFlag": "DIR"
        }
      ],
      "poh": "Y",
      "confirmationMethod": "F",
      "edocsFlag": "N"
    },
    "currencyCode": "AUD",
    "guests": [
      {
        "country": "AU",
        "homeCity": "MEL",
        "passengerStatus": "Past Passenger"
      },
      {
        "country": "AU",
        "homeCity": "MEL"
      }
    ],
    "couponCodes": []
  },
  "filters": {
    "availabilities": [
      "Y",
      "G",
      "B"
    ],
    "cruiseType": "C",
    "cruises": [],
    "meta": "I",
    "itinPorts": [],
    "subTrades": []
  },
  "leadInBy": "itins",
  "retrieveFlags": {
    "additionalGuestFare": True,
    "averageFare": False,
    "includeMisc": False,
    "includeTfpe": True,
    "fareType": "BESTFARE",
    "roundUpFare": True
  }
}
    cruise_codes = requests.post(
    'https://gw.api.princess.com/pcl-web/internal/caps/pc/pricing/v1/cruises',
    json=params,
    headers=headers
    ).json()


    # Process the files
    cruises = process_cruises(princess_products, cruise_codes)
    return cruises

if __name__ == "__main__":
    get_cruises()