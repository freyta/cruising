
# Python scripts
You must have Python 3 installed on your system to run this.
Install the required libraries

    pip3 install --user -r requirements.txt

Clone the directory and change into the folder

    git clone https://github.com/freyta/cruising.git
    cd cruising/Python


Run the script

    python3 scrape_websites.py

Output will be similar to this:

    [!] Starting to scrape cruises
    [!] Getting Royal Caribbean
    [!] Found 804 cruises
    [!] Getting P&O
    [!] Found 299 cruises
    [!] Getting Carnival
    547 left.
    447 left.
    347 left.
    247 left.
    147 left.
    47 left.
    1 left.
    [!] Found 3663 cruises
    [!] Getting Princess
    [!] Found 693 cruises
    [!] Getting Azamara
    AFRICA
    *SNIP*
    ASIA
    [!] Found 322 cruises
    [!] Dumping 5747 cruises to a cruises_2025_01_07.json


An example of the output is as follows:

    [
        {
            "date": "2025-06-11",
            "dep": "Brisbane",
            "title": "New Guinea Island Encounter",
            "ship": "Pacific Encounter",
            "price": 824.93,
            "nights": 10,
            "price_per_night": 82.49,
            "room": "Interior",
            "pax": 4,
            "obc": "$100 onboard spending money included per room"
        },
        {
            "date": "2026-03-21",
            "dep": "Barcelona, Spain",
            "title": "15-Day Transatlantic from Barcelona, Spain",
            "ship": "Carnival Dream",
            "price": 1322.0,
            "nights": 15,
            "price_per_night": 88.13
        }
    ]

----

You can scrape each individual site as well by entering the directory of the company you want to scrape, and then running the script i.e. if you use Linux:


    cd carnival && python3 carnival.py

---


In the Princess directory is a file called [`book_cabin.py`](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py) which is used to track prices of a specific room you want to book. For instance, if you have booked room E417 on a cruise, you can track the price to see if it goes cheaper so you can rebook it at that cheaper price.

You will need to modify a few lines in that script to tailor it to your needs.  

[Line 21](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py#L21): These are the cabin classes you want to check the price of

[Line 30](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py#L30): The id of the cruise you want to track

[Line 31](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py#L31): The date of the cruise you want to track

[Line 33](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py#L33): The cabin you want to track

[Line 50](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py#L31) and [line 60](https://github.com/freyta/cruising/blob/main/Python/princess/book_cabin.py#L60): Add your customer cruise number to get prices specific to you.
