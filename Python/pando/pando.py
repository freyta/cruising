import requests

def fetch_json(url):
    """
    Sends a POST request to the given URL and fetches JSON response.

    Parameters:
        url (str): The URL to send the POST request to.

    Returns:
        dict or None: The JSON response if the request is successful, otherwise None.
    """
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0'
    }
    # Send a POST request to the provided URL
    r = requests.post(url, headers=HEADERS)
    # Check if the request was successful
    if r.status_code == 200:
        return r.json()
    else:
        return None

def get_cruises(url):
    """
    Fetches and processes cruise data from the provided URL.

    Parameters:
        url (str): The URL to fetch the cruise data from.

    Returns:
        list of dict: A sorted list of cruises with relevant information such as name, price, nights, 
                      departure date, and price per night (ppn).
    """
    # Fetch data from the URL
    data = fetch_json(url)
    all_cruises = []

    # Proceed if data is fetched successfully
    if data:
        # Iterate over each item in the 'Items' list of the response
        for item in data.get('Items', []):
            title = item.get('ItineraryName')  # Get the itinerary name
            # Create a dictionary mapping departure keys to their respective dates
            departure_dates = {
                date['Key']: (
                   date['Value'].replace("T00:00:00+00:00", ""))
                for date in item.get('DepartureDates', [])
            }

            # Iterate over voyages and extract relevant details
            for sailing in item.get('Voyages', []):
                price = sailing.get('FromPrice')  # Extract the price
                nights = sailing.get('NumberOfNights')  # Extract the number of nights
                voyage_code = sailing.get('VoyageCode')  # Extract the voyage code
                room_type = sailing.get('RoomType') # Extract the room type
                dep = sailing.get('DeparturePort')
                ship = sailing.get('Ship').split("\u00ae")[0]
                # Get the departure date for the voyage using its code
                departure_date = departure_dates.get(voyage_code)
                pax = sailing.get('CabinSizeNumeric')
                try:
                    obc = sailing['OnBoardCredits'][0]['Title']
                except:
                    obc = "$0"

                # Append cruise information to the list
                all_cruises.append({
                    "date": departure_date,
                    "dep": dep,
                    "title": title,
                    "ship": ship,
                    "price": price,
                    "nights": nights,
                    # Calculate price per night if price and nights are valid
                    "price_per_night": round(price / nights, 2) if price and nights else None,
                    "room": room_type,
                    "pax": pax,
                    "obc": obc
                })
                
        # Sort cruises by price per night in descending order (highest ppn first)
        return sorted(
            all_cruises, 
            key=lambda x: (x['price_per_night'] or float('inf'), x['nights']), 
            reverse=True
        )
    else:
        print("Error getting data from the API.")
        exit()

if __name__ == "__main__":
    # ANSI escape codes for colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHAT = '\033[97m'
    RESET = '\033[0m'
    # Fetch and process cruises from the specified URL
    cruises = get_cruises("https://api.pocruises.com.au/cruiseresults/search")
    # Display the cruise details
    for cruise in cruises:
        if cruise['room'] == "Interior":
            print(f"{GREEN}{cruise['title']}{RESET} costs {YELLOW}{cruise['price']}{RESET} ({CYAN}{cruise['price_per_night']} per night{RESET}) in a {BLUE}{cruise['room']}{RESET} room, departs on {RED}{cruise['date']}{RESET} for {WHAT}{cruise['nights']} nights{RESET}. You get {cruise['obc']} worth of OBC.")
