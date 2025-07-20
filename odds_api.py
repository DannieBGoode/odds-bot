from dotenv import load_dotenv
load_dotenv()
import os
import requests
from config import POPULAR_SOCCER_KEYS

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

def fetch_sports():
    url = f"{ODDS_API_BASE}/sports/?apiKey={ODDS_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        sports = resp.json()
        filtered = [s for s in sports if s["active"] and s["key"] in POPULAR_SOCCER_KEYS]
        if len(filtered) < 6:
            filtered = [s for s in sports if s["active"]][:6]
        return filtered
    except Exception as e:
        print(f"Error fetching sports: {e}")
        return []

def fetch_events(sport_key):
    url = f"{ODDS_API_BASE}/sports/{sport_key}/events?apiKey={ODDS_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        events = resp.json()
        return events[:6]
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def fetch_odds(event_id, sport_key):
    url = f"{ODDS_API_BASE}/sports/{sport_key}/events/{event_id}/odds?apiKey={ODDS_API_KEY}&regions=eu,uk,us&markets=h2h"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        odds_data = resp.json()
        for bookmaker in odds_data.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] == "h2h":
                    return {
                        "bookmaker": bookmaker["title"],
                        "outcomes": market["outcomes"]
                    }
        return None
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return None 