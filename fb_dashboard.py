
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import fbref

st.set_page_config(layout="wide")


#st.caption("All data comes from FBRef this dashboard is purely educational and not intended for any commercial purpose.")

prem_table_ha = pd.read_csv("data/data/fbref_dashboard/prem_table_ha.csv")
player_stats = pd.read_csv("data/data/fbref_dashboard/all_prem_squads.csv")
set_piece_takers = pd.read_csv("data/data/fbref_dashboard/set_piece_takers_fbref.csv")

team_list = set(prem_table_ha.Squad)
team_list = sorted(list(team_list))

player_team_list = set(player_stats.Team)
player_team_list = sorted(list(player_team_list))

team_mapping = zip(team_list, player_team_list)
team_mapping = dict(team_mapping)

prem_table_ha['Squad'] = prem_table_ha['Squad'].replace(team_mapping)

team_list = set(prem_table_ha.Squad)

set_piece_takers = set_piece_takers[set_piece_takers["season"] == 2024]

home_set_piece_player = None
away_set_piece_player = None


defender_stats = player_stats[player_stats["Pos"].fillna("").astype(str).str.contains("DF")]


prem_table_unformatted = prem_table_ha.copy()
prem_table_ha = prem_table_ha.rename(columns={"Rk": "Position"})
prem_table_ha = prem_table_ha.loc[:, ~prem_table_ha.columns.str.contains('^Unnamed')]

prem_table_ha.columns = pd.MultiIndex.from_tuples(
    [col.split("_",1) if "_" in col else ("",col) for col in prem_table_ha.columns]
)

with st.sidebar:

    update_dashboard = st.button("Click Here To Update Dashboard")

    home_team = st.selectbox(
        "Home Team",
        team_list,
        index=None,
        placeholder="Select Home Team..."
    )

    away_team = st.selectbox(
        "Away Team",
        team_list,
        index=None,
        placeholder="Select Away Team..."
    )

    set_piece_takers["player_club"] = set_piece_takers["player_club"].replace(team_mapping)

    home_spt_list = set_piece_takers[set_piece_takers["player_club"] == home_team]
    home_spt_list = list(home_spt_list.player_name)
    home_def_list = defender_stats[defender_stats["Team"] == home_team]
    home_def_list = list(home_def_list.Player)

    away_spt_list = set_piece_takers[set_piece_takers["player_club"] == away_team]
    away_spt_list = list(away_spt_list.player_name)
    away_def_list = defender_stats[defender_stats["Team"] == away_team]
    away_def_list = list(away_def_list.Player)

    

    if home_team:
        home_set_piece_player = st.selectbox(
            "Home Set Piece Taker",
            home_spt_list,
            index=None,
            placeholder = "Select Home Set Piece Taker..."
        )
    if away_team:
        away_set_piece_player = st.selectbox(
            "Away Set Piece Taker",
            away_spt_list,
            index=None,
            placeholder = "Select Away Set Piece Taker..."
        )

    if home_team:
        home_defender = st.selectbox(
            "Home Defender",
            home_def_list,
            index=None,
            placeholder = "Select Home Defender..."
        )
    if away_team:
        away_defender = st.selectbox(
            "Away Defender",
            away_def_list,
            index=None,
            placeholder = "Select Away Defender..."
        )



plot1, plot2 = st.columns([1,1])

with plot1:
    if home_set_piece_player:
        home_set_piece_radar_chart = fbref.radar_spts(set_piece_takers, home_set_piece_player, plot_average = True)
        st.plotly_chart(home_set_piece_radar_chart)


with plot2:
    if away_set_piece_player:
        away_set_piece_radar_chart = fbref.radar_spts(set_piece_takers, away_set_piece_player, plot_average = True)
        st.plotly_chart(away_set_piece_radar_chart)


home_stats = prem_table_unformatted[prem_table_unformatted[("Squad")] == home_team]
away_stats = prem_table_unformatted[prem_table_unformatted[("Squad")] == away_team]

lower_left, lower_right = st.columns([1,1])

with lower_left:

    if home_team and away_team and home_set_piece_player and away_set_piece_player and home_defender and away_defender:
        test_df = fbref.team_rating_cols(prem_table_unformatted)
        lamba_home, lambda_away = fbref.poisson_rating(test_df, home_team, away_team)
        poisson_fig = fbref.poisson_plots(lamba_home, lambda_away)
        st.plotly_chart(poisson_fig)

with lower_right:
    st.write("dgwgefgdf")

