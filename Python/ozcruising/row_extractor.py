from bs4 import BeautifulSoup
from dateutil import parser

def get_cruises(cruise_codes, session, POST_URL, HEADERS):
    cruise_codes = ",".join(cruise_codes)
    html_content = session.post(POST_URL, headers=HEADERS, data={"aCruiseCodes": cruise_codes, "aSeoFragment":""})
    return html_content

def clean_cruise_name(departure, destination):
    try:
        # Extract the departure location from the string
        departure = departure.split("Departing ")[1]

        # Check if the departure is part of the destination
        if departure in destination:
            # Remove the departure from the destination string
            destination = destination.replace(f"{departure} to ", "")
            return destination
        return destination
    except IndexError:
        # If "Departing" is not found, return the original destination
        
        destination = destination.replace(f"{departure} to ", "")
        return destination

def extract_cruise_info(row):
    """Extract relevant information from a single cruise row."""
    # Cruise Line
    cruise_line_div = row.select_one('div[style="margin-left: auto; margin-top: 5px; min-height: 30px; text-align: center;"] img')
    cruise_line = cruise_line_div.get('alt').split("[")[1].split("]")[0].strip() if cruise_line_div else None

    # Cruise Code
    cruise_code_div = row.select_one('div[style="/*position: relative;left: 0;*/text-align: left;"] a')
    cruise_code = cruise_code_div.get('id') if cruise_code_div else None

    # Destination
    destination_div = row.select(
        'div[style="margin-bottom: 10px; margin-left: auto; margin-top: 0px; text-align: center;"] div:nth-child(1)'
    )
    destination = destination_div[1].get_text(strip=True) if destination_div else None

    # Date
    date_div = row.select(
        'div[style="margin-bottom: 10px; margin-left: auto; margin-top: 0px; text-align: center;"] div:nth-child(2)'
    )
    date = parser.parse(date_div[0].get_text(strip=True)).strftime("%Y-%m-%d") if date_div else None

    # Departure
    departure_div = row.select_one(
        'div[style="margin-bottom: 10px; margin-left: auto; margin-top: 0px; text-align: center;"] div:nth-child(3) strong font'
    )
    departure = departure_div.get_text(strip=True) if departure_div else None

    # Nights
    nights_div = row.select_one('div[style="min-height: 130px;"] div:nth-child(1)')
    nights = int(nights_div.get_text(strip=True).split(" Nights")[0]) if nights_div and "Nights" in nights_div.get_text(strip=True) else None

    # Ship
    ship_div = row.select_one('div[style="min-height: 130px;"] div:nth-child(2)')
    ship = ship_div.get_text(strip=True) if ship_div else None

    # Price
    price = None
    for div in row.select('div[style="min-height: 45px;"] div'):
        text = div.get_text(strip=True)
        if "Twin From" in text:
            price_text = text.split("Twin From  $")[1].split(" ")[0].replace(",", "")
            price = float(price_text) if price_text else None
            break

    return nights, destination, departure, date, cruise_line, cruise_code, price, ship

def fetch_cruises_in_batches(cruise_codes, session, post_url, headers):
    """Fetch cruises in batches of 30 and parse their details."""
    cruises = []

    for counter in range(0, len(cruise_codes), 30):
        # Fetch the next batch of cruises
        html_content = get_cruises(cruise_codes[counter:counter + 30], session, post_url, headers)

        soup = BeautifulSoup(html_content.content.decode(), 'html.parser')
        rows = soup.find_all('div', class_='col-xs-12 col-sm-12 col-md-6 col-lg-4 cruise-card')

        for row in rows:
            nights, destination, departure, date, cruise_line, cruise_code, price, ship = extract_cruise_info(row)
            if nights and price and cruise_line and cruise_code:
                price_per_night = round(price / nights, 2)
                
                # Avoid duplicates based on unique cruise attributes
                if not any(
                    c[0] == nights and c[1] == destination and c[2] == price and c[4] == cruise_line and c[7] == cruise_code and c[8] == ship
                    for c in cruises
                ):
                    cruises.append((
                        nights, clean_cruise_name(departure, destination), price, price_per_night,
                        cruise_line, departure, date, cruise_code, ship
                    ))
            else:
                print(f"Price or nights data missing for {cruise_code}.")

    return sorted(cruises, key=lambda x: x[3])