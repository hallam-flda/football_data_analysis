import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import re
import random

headers = {'User-Agent': 'Mozilla/5.0'}

def get_league_data(url):
  # home and away form
  league_table_ha_df = pd.read_html(url, header = [0,1])[1]
  league_table_ha_df.columns = [
    f"{parent.strip()}_{child.strip()}" if "Unnamed" not in str(parent) else child.strip()
    for parent, child in league_table_ha_df.columns
  ]

  return league_table_ha_df

def get_team_data(url):
    time.sleep(10)
    print(f"trying URL {url}")
    squad_tables = pd.read_html(url)
    league_squad_df = squad_tables[0]

    prefix_map = {
        "Playing Time": "ptime_",
        "Performance": "perf_",
        "Expected": "exp_",
        "Progression": "prog_",
        "Per 90 Minutes": "p90_"
    }


    league_squad_df.columns = [
        f"{prefix_map.get(parent.strip(), '')}{child.strip()}" if "Unnamed" not in str(parent) else child.strip()
        for parent, child in league_squad_df.columns
    ]

    # extracting team name from url
    match = re.search(r'/([^/]+)-Stats$', url)
    team_name = match.group(1).replace('-', ' ') if match else None
    season = squad_tables[1]["Date"][0][:4]

    # useful for joining later
    league_squad_df['Team'] = team_name
    league_squad_df['Season'] = season

    # last two rows are totals
    league_squad_df = league_squad_df[:-2]

    print(f'{team_name} gathered')
    return league_squad_df

