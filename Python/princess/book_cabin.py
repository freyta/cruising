import requests
import json
import uuid

sessionId = uuid.uuid4()

# The headers we will send
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Referer': 'https://www.princess.com/',
    'AppId': f'{{"agencyId":"DIRECTAU","cruiseLineCode":"PCL","sessionId":"{uuid.uuid4()}","systemId":"PB","gdsCookie":"CO=AU"}}',
    'ProductCompany': 'PC',
    'BookingCompany': 'PA',
    'ReqSrc': 'W',
    'pcl-client-id': '32e7224ac6cc41302f673c5f5d27b4ba',
    'Origin': 'https://www.princess.com',
    'DNT': '1',
}

# The cabin codes we want to go through
CODES = ['OZ', 'OY', 'OW', 'OV', 'OF', 'OE', 'OB']


# Iterate through all of the codes above to find how much each class costs
for code in CODES:
    json_data = {
        'currency': 'AUD',
        'product': {
            'selectedCruise': {
                'id': '3618',             # This is the cruise ID you want to get the price of 
                'startDate': '20261007',  # The date of the cruise
                'cabin': {
                    'number': 'E417',     # Change this to the room you want!
                    'zone': 'M',
                    'category': {
                        'code': code,     # The code of the class you are booking
                    },
                },
            },
        },
        'passengers': [
            {
                'paxId': 1,
                'promoCode': 'NP1',
                'transportation': {
                    'city': 'SYD',
                    'country': 'AU',
                },
                'insuranceInd': 'N',
                'ccn': 0, # Change this to your cruise customer numbers
            },
            {
                'paxId': 2,
                'promoCode': 'NP1',
                'transportation': {
                    'city': 'SYD',
                    'country': 'AU',
                },
                'insuranceInd': 'N',
                'ccn': 1, # Change this to your cruise customer numbers
            },
        ],
    }

    # Perform the actual request
    response = requests.post(
        'https://gw.api.princess.com/pcl-web/internal/pbmf/p1.0/invoice-pricing',
        headers=headers,
        json=json_data,
    )


    # If the request was succesful, print out the information.
    if response.status_code == 200:
        # Set up some nice colours.
        RED = '\033[91m'
        RESET = '\033[0m'
        resp_json = response.json()

        for i in resp_json.get('invoicePricing','').get('guestInvoiceItems'):
            if i.get('seqNumber') == "0":
                amount = i.get('amount')
                desc = i.get('description')
                if code == "OV":
                    print(f"{RED}[{code}] {desc} is: ${amount}{RESET}")
                else:
                    print(f"[{code}] {desc} is: ${amount}")

    else:
        print(response.content)