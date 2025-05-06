import pandas as pd
from datetime import date

def club_name_mapping(first_name_series, second_name_series):
    team_list = set(first_name_series)
    team_list = sorted(list(team_list))

    player_team_list = set(second_name_series)
    player_team_list = sorted(list(player_team_list))

    team_mapping = zip(team_list, player_team_list)
    team_mapping = dict(team_mapping)

    return team_mapping

def get_current_gameweek(df):
    df['Date'] = pd.to_datetime(df['Date'])

    week_agg = (
        df
        .groupby('Wk')['Date']
        .agg(['min', 'max'])
        .sort_index()
    )

    week_agg = week_agg.rename(columns={'max': 'latest_date'})

    week_agg['earliest_date'] = (
        week_agg['latest_date']
        .shift(1)
        + pd.Timedelta(days=1)
    )

    week_agg['earliest_date'].fillna(week_agg['min'], inplace=True)
    week_ranges = (
        week_agg
        .drop(columns='min')
        .reset_index()
    )
    today = pd.to_datetime(date.today())
    mask = (
        (week_ranges['earliest_date'] <= today) &
        (week_ranges['latest_date']   >= today)
    )

    current_wk = week_ranges.loc[mask, 'Wk']

    return current_wk

def get_last_week_lineup(lineups_df, team, previous_week):
    
    team_lineup = lineups_df[
        ((lineups_df['home_team'] == team) | (lineups_df['away_team'] == team)) &
        (lineups_df['Wk'] == previous_week)
    ].copy()

    # identify whether the team was playing at home or away
    team_lineup['team_role'] = team_lineup.apply(
        lambda row: 'home' if row['home_team'] == team else 'away',
        axis=1
    )

    role = team_lineup['team_role'].iloc[0]
    keep_columns = [col for col in team_lineup.columns if col.startswith(role)]

    team_lineup = team_lineup[keep_columns]
    team_lineup.columns = [col.removeprefix(f"{role}_") for col in team_lineup.columns]

    return team_lineup