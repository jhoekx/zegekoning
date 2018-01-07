#!/usr/bin/python3

import argparse
import re
import sys

from collections import Counter

from requests import Session

s = Session()

def find_races(year):
    data = s.get("http://helga-o.com/webres/index.php", params={"year": year}).text
    return [int(laufId) for laufId in re.findall('index.php\\?lauf=(\d+)', data)]

def load_race(id):
    try:
        return s.get("http://helga-o.com/webres/ws.php", params={"lauf": id}).json()
    except:
        print("Failed to load %s"%(id), file=sys.stderr)
        return None

def count_wins(year, club):
    winners = Counter()
    for race in find_races(year):
        results = load_race(race)
        if results is None:
            continue
        for category in results["categories"].values():
            for runner in category["results"]:
                if runner["position"] == "1" and (club is None or club in runner["club"].lower()):
                    winners[runner["name"]] += 1
    return winners.most_common()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("--club", action="store")
    args = parser.parse_args()
    return args.year, args.club

if __name__ == "__main__":
    year, club = parse_args()
    for name, count in count_wins(year, club):
        print(name, count)
