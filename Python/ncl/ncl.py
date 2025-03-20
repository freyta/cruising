import requests
from time import sleep
from datetime import datetime
import os
import json


def fetch_all_cruises():
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"
    }

    response = requests.get("https://www.ncl.com/au/en/api/vacations/v2/itineraries?guests=2", headers=HEADERS)

    scraped_cruises = []
    counter = 0

    if response.status_code == 200:
        response_json = response.json()
        sailing_codes = []
        for i in response_json:
            sailing_codes.append(i["code"])
        print(len(sailing_codes))
            
        for sailing in sailing_codes:
            try:
                sail_response = requests.get(f"https://www.ncl.com/au/en/api/vacations/v2/search-result-itinerary/{sailing}", headers=HEADERS).json()
            except:
                print(sailing)
            dep = sail_response['embarkationPort']['title']
            title = sail_response['shortTitle']
            ship = sail_response['ship']['title']
            nights = sail_response['duration']['days']

            for i in sail_response['sailings']:
                departure_date = i['departureDate'] / 1000
                departure_date = datetime.fromtimestamp(departure_date)
                # Format the datetime object as DD/MM/YYYY
                departure_date = departure_date.strftime("%d/%m/%Y")
                
                for sails in i['staterooms']:
                    if sails['status'] == "AVAILABLE":
                        room_type = sails['title']
                        price = sails['combinedPrice']
                        break
                price_per_night = round(price / nights, 2)
                scraped_cruises.append({
                    "date": departure_date,
                    "dep": dep,
                    "title": title,
                    "ship": ship,
                    "price": price,
                    "nights": nights,
                    "price_per_night": price_per_night,
                    "room_type": room_type
                })
            counter += 1
            if (counter % 50) == 0:
                sleep(5)
                
    else:
        print(response.status_code)

    
    return sorted(scraped_cruises, key=lambda x: x['price_per_night'])

if __name__ == "__main__":
    cruises = fetch_all_cruises()
    print(f"Fetched {len(cruises)} cruises.")
    
    DIR = os.path.dirname(os.path.realpath(__file__))

    date = datetime.now().strftime("%Y_%m_%d")

    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)