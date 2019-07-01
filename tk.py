import sqlite3 as sql
from time import sleep, time
import datetime as dt
import logging

import requests

from colored import *


class Station():
    def __init__(
            self,
            brand,
            diesel,
            dist,
            e10,
            e5,
            id,
            lat,
            lng,
            name,
            place,
            postCode,
            street,
            **kwargs):
        self.id = id
        self.brand = brand
        self.name = name
        self.price_e5 = e5
        self.price_e10 = e10
        self.price_diesel = diesel
        self.distance = dist
        self.latitude = lat
        self.longitude = lng
        self.place = place
        self.street = street
        self.zip_code = postCode

    def __str__(self):
        return f"{self.name} in {self.place}: super @ {self.price_e5}"

    def __format__(self, format_spec):
        return f"{str(self):{format_spec}}"


def get_stations(params):
    data = requests.get(
        "https://creativecommons.tankerkoenig.de/json/list.php?", params=params)

    if not data.status_code == requests.codes.ok:
        raise ValueError("Couldn't fetch data from tankerkönig")

    stations = [Station(**station) for station in data.json()["stations"]]
    return stations


def print_stations(stations):
    headers = {"Name": "name", "Place": "place", "E5": "price_e5", "ID": "id"}
    lengths = [max(map(lambda s: len(str(getattr(s, attr_name))), stations)) for (header, attr_name) in headers.items()]
    headline_segs = []
    for i, header in enumerate(headers.keys()):
        headline_segs.append(f"{header:^{lengths[i]}}")
        
    print_colored(" | ".join(headline_segs), Modifier.Bold)
    for i, station in enumerate(stations):
        color, bg_color = (Color.Black, BgColor.Green) if i%2 else (Color.Green, BgColor.Default)
        station_segs = []
        for i, attr in enumerate(headers.values()):
            attribute = getattr(station, attr)
            if attribute is None:
                attribute = "---"
            else:
                attribute = str(attribute).title()
            station_segs.append(f"{attribute:{lengths[i]}}")
        print_colored(" | ".join(station_segs), color, bg_color)


def get_prices(params):
    data = requests.get("https://creativecommons.tankerkoenig.de/json/prices.php?", params)

    if not data.status_code == requests.codes.ok:
        raise ValueError("Couldn't fetch data from tankerkönig")

    return data.json()["prices"]


def get_logger():
    handler = logging.FileHandler(filename="log.log")
    formatter = logging.Formatter(
        fmt='{asctime} [{levelname:8}] from {module:>20}.{funcName:30} "{message}"', 
        style="{", 
        datefmt="%Y-%m-%dT%H:%m:%S")

    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


if __name__ == "__main__":

    logger = get_logger()

    with open("tankerkönig.key", "r") as f:
        params_list = {
            "lat": 50.043804,
            "lng": 10.238617,
            "rad": 20.0,
            "type": "all",
            # "sort" : "price",
            "apikey": f.read()
        }

    try:
        stations = get_stations(params_list)
    except requests.exceptions.ConnectionError as e:
        print_colored("Failed to query stations.", Color.Red)
        print(e)
        exit()

    print_colored("\nPolling the following stations:\n", Modifier.Bold, Color.Cyan)
    print_stations(stations)

    params_prices = {
        "apikey": params_list["apikey"],
        "ids": ",".join(map(lambda s: s.id, stations))
    }

    con = sql.connect("prices.db")
    
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS prices(
            id STRING,
            timestamp INTEGER,
            price_e5 REAL,
            price_e10 REAL,
            price_diesel REAL,
            PRIMARY KEY (id, timestamp)
        );
        """)


    while True:
        t1 = time()
        try:
            prices = get_prices(params_prices)
        except ValueError as e:
            logger.debug(str(e))
            continue
        t = dt.datetime.now()
        price_data = []
        for id_, data in prices.items():
            price_data.append([id_, t, data["e5"], data["e10"], data["diesel"]])
        with con:
            con.executemany(
                "INSERT INTO prices VALUES (?, ?, ?, ?, ?)", price_data)
        
        t2 = time()
        sleep(60 * 10 - (t2 - t1)) # poll values every 10 minutes