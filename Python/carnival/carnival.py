import requests
import json
import os
from datetime import datetime

def get_cruises(page_number):
    """Fetches cruise data from the Carnival API for a given page number."""
    url = f"https://www.carnival.com.au/cruisesearch/api/search?pageNumber={page_number}&numadults=2&pagesize=100&sort=fromprice&showBest=true&async=true&currency=AUD&locality=7&client=cruisesearch2021&pastGuest=true&vifp=9021344442"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for failed requests

    return response.json()

def fetch_all_cruises():
    """Fetches all cruise data from the API and organizes results by cheapest price per night."""
    counter, page = 0, 1
    cruise_list = []

    cruises = get_cruises(page)
    total_cruises = cruises.get('results', {}).get('totalResults', 0)

    while counter <= total_cruises:
        for itinerary in cruises['results']['itineraries']:
            title = itinerary['itineraryTitle']
            ship = itinerary['shipName']
            nights = itinerary['dur']
            dep = itinerary['departurePortName']

            for sailing in itinerary['sailings']:
                departure_date = sailing['departureDate'].split("T")[0]
                price = sailing['rooms']['interior']['price']
                price_per_night = round(price / nights, 2)
                cruise_list.append({
                    "date": departure_date,
                    "dep": dep,
                    "title": title,
                    "ship": ship,
                    "price": price,
                    "nights": nights,
                    "price_per_night": price_per_night
                })
        counter += len(cruises['results']['itineraries'])
        page += 1
        print(f"{total_cruises - counter} left.")
        cruises = get_cruises(page)

        if len(cruises['results']['itineraries']) == 0:
            break

    return sorted(cruise_list, key=lambda x: x['price_per_night'])

if __name__ == "__main__":
    cruises = fetch_all_cruises()
    
    DIR = os.path.dirname(os.path.realpath(__file__))

    date = datetime.now().strftime("%Y_%m_%d")

    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)