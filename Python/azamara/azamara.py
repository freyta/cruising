import requests
import json
import os
from datetime import datetime

def fetch_json(url):
    """
    Sends a GET request to the given URL and fetches JSON response.

    Parameters:
        url (str): The URL to send the POST request to.

    Returns:
        dict or None: The JSON response if the request is successful, otherwise None.
    """
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0'
    }
    s = requests.Session()

    # Get the locale. This is so we use the correct currency
    locale = s.get('https://www.azamara.com/api/1/services/locale/get-user-locale.json?req=/au/cruises', headers=HEADERS)
    
    s = s.get(url, headers=HEADERS)
    if s.status_code == 200:
        return s.json()
    else:
        return None

def get_cruises(url=None):
    """
    Fetches and processes cruise data from the provided URL.

    Parameters:
        url (str): The URL to fetch the cruise data from.

    Returns:
        list of dict: A sorted list of cruises with relevant information such as name, price, nights, 
                      departure date, and price per night (ppn).
    """
    # Fetch data from the URL
    if url == None:
        url = "https://www.azamara.com/api/1/services/search/get-all-cruises-cached.json"
    data = fetch_json(url)
    cruise_list = []

    if data:
        for item in data.get('results'):

            
                departure_date = item.get('voyageEmbarkDate')[:10]

                objectId = item.get('objectId')
                try:
                    dep = fetch_json(f'https://www.azamara.com/api/1/services/search/get-itinerary-cached.json?siteId=azamara&cruise={objectId}&type=full')
                    dep = dep.get('days')[0].get('portCity')
                except AttributeError:
                    dep = "ERROR!!"

                title = item.get('voyageDestination')
                print(title)
                ship = item.get('ships')[0]
                nights = item.get('voyageDuration')
                if item.get('bookingDetails', {}).get('isBookable') == True:
                    price = item.get('extendedVoyageData', []).get('pricing', []).get('voyagePricePerPersonStartingFrom')
                else:
                    price = 0
                price_per_night = round(float(price) / float(nights), 2)

                
                cruise_list.append({
                    "date": departure_date,
                    "dep": dep,
                    "title": title,
                    "ship": ship,
                    "price": price,
                    "nights": nights,
                    "price_per_night": price_per_night
                })

    return sorted(cruise_list, key=lambda x: x['price_per_night'])



if __name__ == "__main__":
    URL = 'https://www.azamara.com/api/1/services/search/get-all-cruises-cached.json'

    cruises = get_cruises(URL)
    DIR = os.path.dirname(os.path.realpath(__file__))

    date = datetime.now().strftime("%Y_%m_%d")

    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)