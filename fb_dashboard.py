
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import fbref

st.set_page_config(layout="wide")

#st.caption("All data comes from FBRef this dashboard is purely educational and not intended for any commercial purpose.")

prem_table_ha = pd.read_csv("data/data/fbref_dashboard/prem_table_ha.csv")
player_stats = pd.read_csv("data/data/fbref_dashboard/all_prem_squads.csv")
set_piece_takers = pd.read_csv("data/data/fbref_dashboard/set_piece_takers_fbref.csv")
fixture_list = pd.read_csv("data/data/fbref_dashboard/fixture_list.csv")


team_list = set(prem_table_ha.Squad)
team_list = sorted(list(team_list))

player_team_list = set(player_stats.Team)
player_team_list = sorted(list(player_team_list))

team_mapping = zip(team_list, player_team_list)
team_mapping = dict(team_mapping)


prem_table_ha['Squad'] = prem_table_ha['Squad'].replace(team_mapping)
fixture_list['Home'] = fixture_list['Home'].replace(team_mapping)
fixture_list['Away'] = fixture_list['Away'].replace(team_mapping)



set_piece_takers = set_piece_takers[set_piece_takers["season"] == 2024]

home_team = None
away_team = None

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


    game_week = st.selectbox(
        "Game Week",
        fixture_list["Wk"].unique().astype(int),
        index = None,
        placeholder="Select Game Week..."
    )

    if game_week:
        fixture_list = fixture_list[fixture_list["Wk"] == game_week]
        options_list = fixture_list["Date"] + " - " + fixture_list["Time"] + " " + fixture_list["Home"] + " vs " + fixture_list["Away"]
        fixture = st.selectbox(
            "Fixture",
            options_list,
            index=None,
            placeholder="Select Fixture..."
        )
        if fixture:
            # Split off the datetime part
            _, teams_part = fixture.split(" - ", 1)
            # Now split again to get the team names
            teams_string = teams_part.split(" ", 1)[1]  # remove the time (e.g. "16:30")
            home_team, away_team = teams_string.split(" vs ")

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

    st.write("Spreadex Override",help = "Use this to override the home and away team ratings with your own values. This is useful if you have a strong opinion on a game and want to adjust the ratings accordingly.")
    home_suprem = st.slider("Home Team Supremacy", -4.0, 4.0, 0.0, 0.05)
    total_goals = st.slider("Total Goals", 0.0, 6.0, 2.0, 0.05)
    home_goals = home_suprem/2 + total_goals/2
    away_goals = total_goals - home_goals
    st.write(f"Home Goals: {home_goals:.2f}")  
    st.write(f"Away Goals: {away_goals:.2f}")
    use_spreadex = st.toggle("Use Spreadex Supremacies", value=False)

home_stats = prem_table_unformatted[prem_table_unformatted[("Squad")] == home_team]
away_stats = prem_table_unformatted[prem_table_unformatted[("Squad")] == away_team]

plot1, plot2 = st.columns([1,1])

with plot1:
    if home_team and away_team:
        rated_team_table = fbref.team_rating_cols(prem_table_unformatted)
        lambda_home, lambda_away = fbref.poisson_rating(rated_team_table, home_team, away_team)
        poisson_fig = fbref.poisson_plots(home_team, away_team, lambda_home, lambda_away)
        st.plotly_chart(poisson_fig)



with plot2:
    if home_set_piece_player:
        home_set_piece_radar_chart = fbref.radar_spts(set_piece_takers, home_set_piece_player, away_set_piece_player ,plot_average = True)
        st.plotly_chart(home_set_piece_radar_chart)




lower_left, lower_right = st.columns([1,1])

with lower_left:
    st.write("A")


if use_spreadex:
    lambda_home = home_goals
    lambda_away = away_goals
else:
    lambda_home, lambda_away = fbref.poisson_rating(rated_team_table, home_team, away_team)

with lower_right:
    st.subheader("Probabilties")
    if home_team and away_team and home_set_piece_player and away_set_piece_player and home_defender and away_defender:
        spt_home_dead_ball_prop = st.slider(f"Proportion of {home_team} Set Pieces Taken by {home_set_piece_player} in game (%)",0.0,1.0,0.5,0.01)
        home_team_df = rated_team_table[rated_team_table['Squad'] == home_team]
        home_team_df = home_team_df.iloc[0]
        home_player_df = defender_stats[defender_stats['Player'] == home_defender]
        home_player_df['player_xG_contr'] = home_player_df['p90_xG']/home_team_df['Home_xGp90']
        home_player_df = home_player_df.iloc[0]
        home_defender_cont = home_player_df['player_xG_contr']
        home_prob = fbref.cb_score_spt_assist(lambda_home, home_defender_cont, spt_taker_prop = spt_home_dead_ball_prop)
        st.write(f'There is a {home_prob*100:.4f}% chance that {home_defender} will score from a set piece taken by {home_set_piece_player} This implies a fair betting price of {1/home_prob:.2f} ')

    if home_team and away_team and home_set_piece_player and away_set_piece_player and home_defender and away_defender:
        spt_away_dead_ball_prop = st.slider(f"Proportion of {away_team} Set Pieces Taken by {away_set_piece_player} in game (%)",0.0,1.0,0.5,0.01)
        away_team_df = rated_team_table[rated_team_table['Squad'] == away_team]
        away_team_df = away_team_df.iloc[0]
        away_player_df = defender_stats[defender_stats['Player'] == away_defender]
        away_player_df['player_xG_contr'] = away_player_df['p90_xG']/away_team_df['Away_xGp90']
        away_player_df = away_player_df.iloc[0]
        away_defender_cont = away_player_df['player_xG_contr']
        away_prob = fbref.cb_score_spt_assist(lambda_away, away_defender_cont, spt_taker_prop = spt_away_dead_ball_prop)
        st.write(f'There is a {away_prob*100:.4f}% chance that {away_defender} will score from a set piece taken by {away_set_piece_player} This implies a fair betting price of {1/away_prob:.2f} ')
