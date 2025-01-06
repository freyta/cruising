import requests

def get_cruises(page_number):
    """Fetches cruise data from the Carnival API for a given page number."""
    url = f"https://www.carnival.com.au/cruisesearch/api/search?pageNumber={page_number}&numadults=2&pagesize=100&sort=fromprice&showBest=true&async=true&currency=AUD&locality=7&client=cruisesearch2021"
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

    return sorted(cruise_list, key=lambda x: x['price_per_night'], reverse=True)

if __name__ == "__main__":
    cruises = fetch_all_cruises()
    for cruise in cruises:
        print(f"[{cruise['date']}]: {cruise['title']} on the {cruise['ship']}. ${cruise['price']} ({cruise['price_per_night']} p/n)")
