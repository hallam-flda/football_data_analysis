
import pandas as pd

def most_common_team(team_df):
    most_common_players = team_df.sort_values("MP", ascending = False)
    most_common_players = list(most_common_players["Player"].head(11))
    return most_common_players


def get_league_data(url):
  # standard league table
  league_table_df = pd.read_html(url)[0]

  # home and away form
  league_table_ha_df = pd.read_html(url, header = [0,1])[1]
  league_table_ha_df.columns = [
    f"{parent.strip()}_{child.strip()}" if "Unnamed" not in str(parent) else child.strip()
    for parent, child in league_table_ha_df.columns
  ]

  return league_table_df, league_table_ha_df