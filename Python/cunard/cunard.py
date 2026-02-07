import requests
import json
import os
from datetime import datetime

def get_promos(promo_id, promo_json):
    promo = []
    if promo_id == "OBC":
        return "None"
    
    if promo_id in promo_json['specialOffers']:
        promo.append(promo_json['specialOffers'][promo_id]['name'])
        return promo  # Return the data if needed
    else:
        return None  # Return None if not found

def fetch_all_cruises():
    count = 0
    scraped_cruises = []

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.cunard.com/',
    'Content-Type': 'application/json',
    'brand': 'cunard',
    'locale': 'en_AU',
    'country': 'AU',
    'currencyCode': 'AUD',
    'DNT': '1',
}
    
    promo_json = requests.get("https://www.cunard.com/en-au/promos.promosDetails.json", headers=headers).json()
    

    while True:
        data = requests.get(f"https://www.cunard.com/search/cunard_en_AU/cruisesearch?&fq=(soldOut:(false) AND price_AUD_anonymous:[1 TO *] AND embargoDateTime:[1999-12-01T00:00:00Z TO NOW])&start={count}&rows=99&",headers=headers).json()

        try:
            cruises = data.get('searchResults', {})
        except:
            return sorted(scraped_cruises, key=lambda x: x['price_per_night'], reverse=False)
    
        for i in cruises:
                departure_date = i['departureDate'].split("T")[0]
                dep = i['departurePortName']
                title = i['cruiseShortName']
                ship = i['shipName']
                price = float(i['price_AUD_anonymous'])
                room_type = i['roomTypeName_AUD_anonymous']
                nights = int(i['duration'])
                price_per_night = round((price / nights), 2)
            
                for j in i['cruiseOfferNames']:
                    promos = get_promos(j['id'], promo_json)
            
                scraped_cruises.append({
                "date": departure_date,
                "dep": dep,
                "title": title,
                "ship": ship,
                "price": price,
                "nights": nights,
                "price_per_night": price_per_night,
                "promos": promos,
                "room_type": room_type
            })
        if not cruises:
            break

        count += 99

    return sorted(scraped_cruises, key=lambda x: x['price_per_night'])


if __name__ == "__main__":
    cruises = fetch_all_cruises()
    print(f"Fetched {len(cruises)} cruises.")
    
    DIR = os.path.dirname(os.path.realpath(__file__))

    date = datetime.now().strftime("%Y_%m_%d")

    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)