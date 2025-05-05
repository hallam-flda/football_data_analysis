import pandas as pd

def club_name_mapping(first_name_series, second_name_series):
    team_list = set(first_name_series)
    team_list = sorted(list(team_list))

    player_team_list = set(second_name_series)
    player_team_list = sorted(list(player_team_list))

    team_mapping = zip(team_list, player_team_list)
    team_mapping = dict(team_mapping)

    return team_mapping