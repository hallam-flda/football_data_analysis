
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import fbref

st.set_page_config(layout="wide")
st.caption("All data comes from FBRef this dashboard is purely educational and not intended for any commercial purpose.")

prem_table_ha = pd.read_csv("data/data/fbref_dashboard/prem_table_ha.csv")
team_list = set(prem_table_ha.Squad)
set_piece_takers = pd.read_csv("data/data/fbref_dashboard/set_piece_takers_fbref.csv")
set_piece_takers = set_piece_takers[set_piece_takers["season"] == 2024]

st.dataframe(set_piece_takers.head())


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

    home_spt_list = set_piece_takers[set_piece_takers["player_club"] == home_team]
    home_spt_list = list(home_spt_list.player_name)

    away_spt_list = set_piece_takers[set_piece_takers["player_club"] == away_team]
    away_spt_list = list(away_spt_list.player_name)

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


import plotly.express as px

def radar_spts(df, player):
    # Select relevant columns
    keep_columns = df.columns[5:10].tolist()

    # Normalise metrics using Min-Max scaling
    df_norm = df.copy()
    df_norm[keep_columns] = (df[keep_columns] - df[keep_columns].min()) / (df[keep_columns].max() - df[keep_columns].min())

    # Filter for the specified player
    player_row = df_norm[df_norm["player_name"] == player]
    
    if player_row.empty:
        raise ValueError(f"No data found for player: {player}")
    
    # Extract the normalised values
    values = player_row[keep_columns].iloc[0].tolist()

    # Create a temporary DataFrame for plotting
    radar_df = {
        "Metric": keep_columns,
        "Value": values
    }

    fig = px.line_polar(radar_df, r="Value", theta="Metric", line_close=True)
    fig.update_traces(fill='toself')

        # Make background transparent
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='rgba(0,0,0,0)'
        )
    )
    return fig


plot1, plot2 = st.columns([1,1])

with plot1:
    if home_set_piece_player:
        home_set_piece_radar_chart = radar_spts(set_piece_takers, home_set_piece_player)
        st.plotly_chart(home_set_piece_radar_chart)

with plot2:
    if away_set_piece_player:
        away_set_piece_radar_chart = radar_spts(set_piece_takers, away_set_piece_player)
        st.plotly_chart(away_set_piece_radar_chart)

st.subheader("League Form")

if home_team and away_team:
    both_stats = prem_table_ha[prem_table_ha[("","Squad")].isin([home_team,away_team])]
    st.dataframe(both_stats.iloc[:,1:])

home_stats = prem_table_unformatted[prem_table_unformatted[("Squad")] == home_team]
away_stats = prem_table_unformatted[prem_table_unformatted[("Squad")] == away_team]


st.subheader("Probability Output")
if home_team:
    home_summary_line = f'{home_team} have played {home_stats.iloc[0].Home_MP} matches at home with a cumulative xG of {home_stats.iloc[0].Home_xG} averaging at {round(home_stats.iloc[0].Home_xG/home_stats.iloc[0].Home_MP,2)} xG per game '
    st.write(home_summary_line)

if away_team:  
    away_summary_line = f'{away_team} have played {away_stats.iloc[0].Away_MP} matches away with a cumulative xG of {away_stats.iloc[0].Away_xG} averaging at {round(away_stats.iloc[0].Away_xG/away_stats.iloc[0].Away_MP,2)} xG per game '
    st.write(away_summary_line)



# squad_stats_df = pd.read_csv("data/data/fbref_dashboard/all_prem_squads.csv")

# home_squad_df = squad_stats_df[squad_stats_df["Team"] == home_team]
# away_squad_df = squad_stats_df[squad_stats_df["Team"] == away_team]

# home_team_squad_stats, away_team_squad_stats = st.columns([1,1])

# with home_team_squad_stats:
#     st.subheader("Home Team Player Stats")
#     st.dataframe(home_squad_df)


# with away_team_squad_stats:
#     st.subheader("Away Team Player Stats")
#     st.dataframe(away_squad_df)

