import requests
import os
import json
from datetime import datetime

def get_promos(cruise_id, promo_json):
    promo = []
    if cruise_id in promo_json:
        for promos in promo_json[cruise_id]:
            promo.append(promos['rteText'])
        return promo  # Return the data if needed
    else:
        return None  # Return None if not found

def get_cruises():
    count = 0
    scraped_cruises = []
    
    promo_json = requests.get("https://www.hollandamerica.com/bin/carnival/badgeDetails.hal.au.en.json").json()
    
    while True:
        data = requests.get(f"https://www.hollandamerica.com/search/halcruisesearch?&start={count}&rows=99&country=au&language=en&fq=departDate:[NOW/DAY+1DAY TO *]&fq={{!tag=collapse}}{{!collapse field=itineraryId}}&expand=true&expand.rows=50").json()
        
        try:
            cruises = data.get('response', {}).get('docs', [])
        except:
            return sorted(scraped_cruises, key=lambda x: x['price_per_night'])
        
        for i in cruises:
                departure_date = i['departDate'].split("T")[0]
                dep = i['embarkPortName'].split("#")[0]
                title = i['name']
                ship = i['shipName'].split("#")[0]
                price = i['sortPrice_AUD']
                nights = i['duration']
                price_per_night = round((price / nights), 2)
                cruise_id = i['cruiseId']
                
                promos = get_promos(cruise_id, promo_json)
                
                scraped_cruises.append({
                    "date": departure_date,
                    "dep": dep,
                    "title": title,
                    "ship": ship,
                    "price": price,
                    "nights": nights,
                    "price_per_night": price_per_night,
                    "promos": promos
                })
        if not cruises:
            break

        count += 99
    return sorted(scraped_cruises, key=lambda x: x['price_per_night'])


if __name__ == "__main__":
    cruises = get_cruises()
    print(f"Fetched {len(cruises)} cruises.")

    DIR = os.path.dirname(os.path.realpath(__file__))

    date = datetime.now().strftime("%Y_%m_%d")

    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)