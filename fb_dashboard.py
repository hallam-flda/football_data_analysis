
import streamlit as st
import pandas as pd
from utils import fbref

st.set_page_config(layout="wide")

prem_table_ha = pd.read_csv("data/data/fbref_dashboard/prem_table_ha.csv")
team_list = set(prem_table_ha.Squad)

league_stats, prob_output = st.columns([1,1])

with league_stats: 
    st.header("League Form", divider = True)
    home_team = st.selectbox(
        "Home Team",
        team_list,
        index=None,
        placeholder="Select Home Team...",
    )

    if home_team:
        home_stats = prem_table_ha[prem_table_ha["Squad"] == home_team]
        st.dataframe(home_stats.iloc[:,1:])

    away_team = st.selectbox(
        "Away Team",
        team_list,
        index=None,
        placeholder="Select Away Team...",
    )

    if away_team:
        away_stats = prem_table_ha[prem_table_ha["Squad"] == away_team]
        st.dataframe(away_stats.iloc[:,1:])

with prob_output:
    st.header("Probability Output", divider = True)
    if home_team:
        home_summary_line = f'{home_team} have played {home_stats.iloc[0].Home_MP} matches at home with a cumulative xG of {home_stats.iloc[0].Home_xG} averaging at {round(home_stats.iloc[0].Home_xG/home_stats.iloc[0].Home_MP,2)} xG per game '
        st.write(home_summary_line)

    if away_team:  
        away_summary_line = f'{away_team} have played {away_stats.iloc[0].Away_MP} matches away with a cumulative xG of {away_stats.iloc[0].Away_xG} averaging at {round(away_stats.iloc[0].Away_xG/away_stats.iloc[0].Away_MP,2)} xG per game '
        st.write(away_summary_line)



squad_stats_df = pd.read_csv("data/data/fbref_dashboard/all_prem_squads.csv")


home_squad_df = squad_stats_df[squad_stats_df["Team"] == home_team]
away_squad_df = squad_stats_df[squad_stats_df["Team"] == away_team]

home_team_squad_stats, away_team_squad_stats = st.columns([1,1])

with home_team_squad_stats:
    st.header("Home Team Player Stats", divider = True)
    st.dataframe(home_squad_df)


with away_team_squad_stats:
    st.header("Away Team Player Stats", divider = True)
    st.dataframe(away_squad_df)

# home_col, away_col, output_probs = st.columns([1,1,2])

# with home_col:
#     st.dataframe(home_squad_df)