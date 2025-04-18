from utils.fbref.scraping_funcs import get_team_data
import pandas as pd

squad_urls = [
    "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats",
    "https://fbref.com/en/squads/8602292d/Aston-Villa-Stats",
    "https://fbref.com/en/squads/4ba7cbea/Bournemouth-Stats",
    "https://fbref.com/en/squads/cd051869/Brentford-Stats",
    "https://fbref.com/en/squads/d07537b9/Brighton-and-Hove-Albion-Stats",
    "https://fbref.com/en/squads/cff3d9bb/Chelsea-Stats",
    "https://fbref.com/en/squads/47c64c55/Crystal-Palace-Stats",
    "https://fbref.com/en/squads/d3fd31cc/Everton-Stats",
    "https://fbref.com/en/squads/fd962109/Fulham-Stats",
    "https://fbref.com/en/squads/b74092de/Ipswich-Town-Stats",
    "https://fbref.com/en/squads/a2d435b3/Leicester-City-Stats",
    "https://fbref.com/en/squads/822bd0ba/Liverpool-Stats",
    "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats",
    "https://fbref.com/en/squads/19538871/Manchester-United-Stats",
    "https://fbref.com/en/squads/b2b47a98/Newcastle-United-Stats",
    "https://fbref.com/en/squads/a2d435b3/Nottingham-Forest-Stats",
    "https://fbref.com/en/squads/33c895d4/Southampton-Stats",
    "https://fbref.com/en/squads/361ca564/Tottenham-Hotspur-Stats",
    "https://fbref.com/en/squads/7c21e445/West-Ham-United-Stats",
    "https://fbref.com/en/squads/8cec06e1/Wolverhampton-Wanderers-Stats"
]

all_prem_squads = []

for url in squad_urls:
  print(f'starting {url}')
  df = get_team_data(url)
  all_prem_squads.append(df)
  print('data appended')

all_prem_squads_df = pd.concat(all_prem_squads)

all_prem_squads_df.to_csv("all_prem_squads.csv")