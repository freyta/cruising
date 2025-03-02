import requests
import json
import os
from datetime import datetime

DIR = os.path.dirname(os.path.realpath(__file__))

def get_cruises():
    """
    Sends a POST request to the given URL and fetches JSON response.
    
    Returns:
        dict or None: The JSON response if the request is successful, otherwise None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.celebritycruises.com/au/cruises?country=AUS&market=au',
        'Origin': 'https://www.celebritycruises.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'country': 'AUS',
        'language': 'en-gb',
        'currency': 'AUD',
        'office': 'AUS',
        'apollographql-query-name': 'cruiseSearch_Cruises',
    }

    all_cruises = []  # Store all results here
    scraped_cruises = []
    pagination_count = 50  # Adjust as needed
    pagination_skip = 0
    
    while True:
        payload = {
            "operationName": "cruiseSearch_Cruises",
            "variables": {
                "sort": {"by": "PRICE", "order": "ASC"},
                "pagination": {"count": pagination_count, "skip": pagination_skip}
            },
            "query": """
            query cruiseSearch_Cruises($filters: String, $qualifiers: String, $sort: CruiseSearchSort, $pagination: CruiseSearchPagination) {  cruiseSearch(    filters: $filters    qualifiers: $qualifiers    sort: $sort    pagination: $pagination  ) {    results {      cruises {        id        productViewLink        highlights {          id          backgroundColor          label          borderColor          textColor          shape          __typename        }        lowestPriceSailing {          bookingLink          id          lowestStateroomClassPrice {            price {              value              currency {                code                symbol                __typename              }              __typename            }            stateroomClass {              id              content {                code                __typename              }              __typename            }            __typename          }          sailDate          startDate          endDate          taxesAndFees {            value            __typename          }          taxesAndFeesIncluded          __typename        }        displaySailing {          bookingLink          id          lowestStateroomClassPrice {            price {              value              currency {                code                __typename              }              __typename            }            stateroomClass {              id              content {                code                __typename              }              __typename            }            __typename          }          sailDate          startDate          endDate          taxesAndFees {            value            __typename          }          taxesAndFeesIncluded          __typename        }        masterSailing {          itinerary {            name            code            media {              images {                path                __typename              }              __typename            }            days {              number              type              ports {                activity                arrivalTime                departureTime                port {                  code                  name                  region                  media {                    images {                      path                      __typename                    }                    __typename                  }                  __typename                }                __typename              }              __typename            }            departurePort {              code              name              region              __typename            }            destination {              code              name              __typename            }            postTour {              days {                number                type                ports {                  activity                  arrivalTime                  departureTime                  port {                    code                    name                    region                    __typename                  }                  __typename                }                __typename              }              duration              __typename            }            preTour {              days {                number                type                ports {                  activity                  arrivalTime                  departureTime                  port {                    code                    name                    region                    __typename                  }                  __typename                }                __typename              }              duration              __typename            }            portSequence            sailingNights            ship {              code              name              stateroomClasses {                id                name                content {                  amenities                  area                  code                  maxCapacity                  media {                    images {                      path                      meta {                        description                        title                        location                        __typename                      }                      __typename                    }                    __typename                  }                  superCategory                  __typename                }                __typename              }              media {                images {                  path                  __typename                }                __typename              }              __typename            }            portSequence            totalNights            type            __typename          }          __typename        }        sailings {          bookingLink          id          itinerary {            code            __typename          }          sailDate          startDate          endDate          taxesAndFees {            value            __typename          }          taxesAndFeesIncluded          stateroomClassPricing {            price {              value              currency {                code                symbol                __typename              }              __typename            }            stateroomClass {              id              content {                code                __typename              }              __typename            }            __typename          }          __typename        }        __typename      }      total      __typename    }    __typename  }}
            """
        }
        
        response =  requests.post('https://www.celebritycruises.com/graph', headers=headers, json=payload)

        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            exit()
        
        data = response.json()
        
        try:
            cruises = data.get('data', {}).get('cruiseSearch', {}).get('results', {}).get('cruises', [])
        except AttributeError:
            print(json.dumps(data, indent=2, sort_keys=True))
            return sorted(scraped_cruises, key=lambda x: x['price_per_night'])


        for sailing in cruises:
            price = sailing['lowestPriceSailing']['lowestStateroomClassPrice']['price']['value']
            departure_date = sailing['lowestPriceSailing']['sailDate']
            dep = sailing['masterSailing']['itinerary']['departurePort']['name']
            title = sailing['masterSailing']['itinerary']['name']
            nights = sailing['masterSailing']['itinerary']['sailingNights']
            ship = sailing['masterSailing']['itinerary']['ship']['name']
            price_per_night = round(price / nights,2)

            scraped_cruises.append({
                    "date": departure_date,
                    "dep": dep,
                    "title": title,
                    "ship": ship,
                    "price": price,
                    "nights": nights,
                    "price_per_night": price_per_night
                    })
        if not cruises:
            # No more results to fetch
            break

        # Add fetched cruises to the collection
        all_cruises.extend(cruises)

        # Increment the pagination skip for the next batch
        pagination_skip += pagination_count

        
    return sorted(scraped_cruises, key=lambda x: x['price_per_night'])
    
if __name__ == "__main__":
    cruises = get_cruises()
    
    DIR = os.path.dirname(os.path.realpath(__file__))

    date = datetime.now().strftime("%Y_%m_%d")

    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)