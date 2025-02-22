#!/bin/python3

import carnival.carnival as carnival
import pando.pando as pando
import royal_caribbean.rc as rc
import princess.princess as princess
import azamara.azamara as azamara
import celebrity.celebrity as celebrity
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

if __name__ == '__main__':
    print("[!] Starting to scrape cruises")
    cruises = []

    royal_caribbean = get_rc()
    po_cruises = get_pando()
    carnival_cruises = get_carnival()
    princess_cruises = get_princess()
    # azamara_cruises = get_azamara()
    celebrity_cruises = get_celebrity()
    
    for i in royal_caribbean:
        if i['price'] > 0:
            cruises.append(i)
    for i in po_cruises:
        if i['price'] > 0:
            cruises.append(i)
    for i in carnival_cruises:
        if i['price'] > 0:
            cruises.append(i)
    for i in princess_cruises:
        if i['price'] > 0:
            cruises.append(i)
    # for i in azamara_cruises:
    #    if i['price'] > 0:
    #        cruises.append(i)
    for i in celebrity_cruises:
        if i['price'] > 0:
            cruises.append(i)

    cruises.sort(key=lambda cruise: cruise["price_per_night"], reverse=False)
    date = datetime.now().strftime("%Y_%m_%d")
    with open(f"{DIR}/cruises_{date}.json", "w") as f:
        print(f"[!] Dumping {len(cruises)} cruises to a {DIR}/cruises_{date}.json")
        json.dump(cruises, f, indent=2)