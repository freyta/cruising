import requests
from datetime import datetime
import os
import json

DIR = os.path.dirname(os.path.realpath(__file__))

def fetch_url(offset):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://www.cruise1st.com.au',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    json_data = {
        'limit': 50,
        'offset': offset,
        'sortString': 'price',
        'filterParams': {
            'zone': [ # You can add a zone here if you want. We will just search every cruise
            ],
            'priceMin': 0,
        },
    }

    response = requests.post('https://backend.dreamlines.com/c1au/cruises/search-with-aggregation', headers=headers, json=json_data)

    print(offset)
    return response.json()

def get_cruises():

    # How many cruises we want to increment by
    increment_by = 50
    # Our starting offset
    offset = 0
    scraped_cruises = []

    while True:
        # Fetch the cruise JSON file
        cruise_json = fetch_url(offset)

        # If our offset is more than the number of results we'll exit
        if offset >= cruise_json['numResults']:
            break

        # Increment the offset
        offset += increment_by

        # Add cruises to our JSON file
    
        for i in cruise_json['cruises']:

            title = i['routeTitle'].split(" from")[0]
            cruise_line = i['companyTitle']
            ship = i['shipTitle']
            price = i['cheapestSail']['price']
            start= i['startHarbourName']
            dest = i['endHarbourName']
            dep = i['cheapestSail']['departure']
            nights = i['nights']
            obc = i['obc']


            for sailing in i['sails']:
                price = sailing['price']
                price_per_night = round(price/nights, 2)

                date_object = datetime.fromtimestamp(int(sailing['departure']))

                # Format the date as DD/MM/YYYY
                dep = date_object.strftime("%d/%m/%Y")

                scraped_cruises.append({
                        "title": title,
                        "cruise_line": cruise_line,
                        "ship": ship,
                        "start": start,
                        "dest": dest,
                        "date": dep,
                        "price": price,
                        "obc": obc,
                        "nights": nights,
                        "price_per_night": price_per_night
                        })
    return sorted(scraped_cruises, key=lambda x: x['price_per_night'])

if __name__ == "__main__":
    cruises = get_cruises()

    # Dump to a file
    with open(f"{DIR}/cruises.json", "w", encoding="utf-8") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises.json")
        json.dump(cruises, f, indent=2)