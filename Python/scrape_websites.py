#!/bin/python3

import carnival.carnival as carnival
import pando.pando as pando
import royal_caribbean.rc as rc
import princess.princess as princess
import azamara.azamara as azamara
import celebrity.celebrity as celebrity
import hollandamerica.hollandamerica as hollandamerica
import cunard.cunard as cunard
import json
import os
from datetime import datetime

DIR = os.path.dirname(os.path.realpath(__file__))


def get_rc():
    print("[!] Getting Royal Caribbean")
    cruises = rc.fetch_all_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_carnival():
    print("[!] Getting Carnival")
    cruises = carnival.fetch_all_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_pando():
    print("[!] Getting P&O")
    cruises = pando.get_cruises("https://api.pocruises.com.au/cruiseresults/search")
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_princess():
    print("[!] Getting Princess")
    cruises = princess.get_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_azamara():
    print("[!] Getting Azamara")
    cruises = azamara.get_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_celebrity():
    print("[!] Getting Celebrity Cruises")
    cruises = celebrity.get_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_hollandamerica():
    print("[!] Getting Holland America")
    cruises = hollandamerica.get_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

def get_cunard():
    print("[!] Getting Cunard")
    cruises = cunard.fetch_all_cruises()
    print(f"[!] Found {len(cruises)} cruises")
    return cruises

if __name__ == '__main__':
    print("[!] Starting to scrape cruises")
    cruise_functions = [
        get_rc(),
        get_pando(),
        get_carnival(),
        get_princess(),
        # get_azamara(),
        get_celebrity(),
        get_hollandamerica(),
        get_cunard()
    ]

    cruises = []
    for cruise_line in cruise_functions:
        for cruise in cruise_line:
            if cruise['price'] > 0:
                cruises.append(cruise)


    cruises.sort(key=lambda cruise: cruise["price_per_night"], reverse=False)
    date = datetime.now().strftime("%Y_%m_%d")
    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)