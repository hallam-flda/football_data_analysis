import json
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import streamlit as st

X_MIN = 10
Y_MIN = 10
X_MAX = 50
Y_MAX = 70

def make_player_table(df, list_col, prefix, role):
    # 1. explode that one list
    exploded = df.explode(list_col).reset_index(drop=True)
    # 2. flatten team & coach
    team_flat  = pd.json_normalize(exploded["team"]).add_prefix("team_")
    coach_flat = pd.json_normalize(exploded["coach"]).add_prefix("coach_")
    # 3. pull out the inner 'player' dict and normalize *that*
    inner = exploded[list_col].apply(lambda x: x.get("player", {}) if isinstance(x, dict) else {})
    player_flat = pd.json_normalize(inner).add_prefix(f"{prefix}_")
    # 4. stitch back, drop the old columns, tag role
    base = exploded.drop(columns=["team", "coach", list_col])
    out  = pd.concat([base, team_flat, coach_flat, player_flat], axis=1)
    out["role"] = role
    return out

def join_players_and_subs(df):  
    starters = make_player_table(df, "startXI",    prefix="player", role="starter")
    subs     = make_player_table(df, "substitutes", prefix="player", role="sub")
    players  = pd.concat([starters, subs], ignore_index=True)
    tidy     = players.drop(columns=["startXI", "substitutes"])
    tidy[["xplot","yplot"]] = tidy["player_grid"].str.split(':', expand = True)
    tidy['xplot'] = tidy['xplot'].astype(float)
    tidy['yplot'] = tidy['yplot'].astype(float)
    tidy['formation_list'] = tidy['formation'].str.split('-').to_list()
    tidy['xplot'] = X_MIN + (tidy['xplot'] - 1) * (X_MAX - X_MIN) / tidy['formation_list'].apply(len)

    # Calculate max yplot per xplot
    max_y_per_x = tidy.groupby("xplot")["yplot"].transform("max")

    # Apply scaling using per-x max values
    tidy['yplot'] = np.where(
    tidy['player_pos'] == "G",
    40,  # fixed value for goalkeeper
    Y_MIN + ((tidy['yplot'] - 1) * (Y_MAX - Y_MIN) / (max_y_per_x-1) )
)

    return tidy

def process_team_coords(team_df, is_away=False):
    team = team_df[team_df['player_grid'].str.contains(":", na=False)].copy()
    
    
    team[["xplot", "yplot"]] = team["player_grid"].str.extract(r'^(\d+):(\d+)$').astype(float)
    
    
    team['formation_list'] = team['formation'].str.split('-').to_list()
    line_width = (X_MAX - X_MIN)
    formation_lens = team['formation_list'].apply(len)

    outfield_x = (X_MIN + (team['xplot'] - 1) * line_width / formation_lens)
    if is_away:
        outfield_x = 120 - outfield_x

    team['xplot'] = np.where(
        team["player_pos"] == "G",
        115 if is_away else 5,
        outfield_x
    )

    
    team['max_y_per_x'] = team.groupby("xplot")["yplot"].transform("max")
    denominator = (team['max_y_per_x'] - 1).replace(0, 2)
    team['yplot'] = np.where(team['max_y_per_x'] == 1, 2.1, team['yplot'])

   
    team['yplot'] = np.where(
        team['player_pos'] == "G",
        40,
        np.where(
            team['max_y_per_x'] == 2,
            (Y_MAX * 0.85) - ((team['yplot'] - 1) * ((Y_MAX * 0.75 - Y_MIN * 1.3) / denominator)),
            Y_MAX - ((team['yplot'] - 1) * ((Y_MAX - Y_MIN) / denominator))
        )
    )

    return team


def players_plotting_coords(home_team_df=None, away_team_df=None):
    home = process_team_coords(home_team_df, is_away=False)
    away = process_team_coords(away_team_df, is_away=True)
    return home, away

def plot_pitch_with_players(home_df, away_df):
    pitch = Pitch(
        pitch_color='grass', line_color='white', stripe=True,
        corner_arcs=True, pitch_type='statsbomb'#,
        # axis=True, label=True, tick=True
    )
    fig, ax = pitch.draw()

    for _, row in home_df.iterrows():
        # Plot player circle
        circle = plt.Circle(
            (row['xplot'], row['yplot']), 
            radius=2.5, 
            color='white', 
            ec='black', 
            zorder=3
        )
        ax.add_patch(circle)

        # Player number inside the circle
        ax.text(
            row['xplot'], row['yplot'], 
            str(row['player_number']), 
            va='center', ha='center', 
            fontsize=8, fontweight='bold', 
            zorder=4
        )

        # Player name underneath
        ax.text(
            row['xplot'], row['yplot'] - 6,  # slightly below the circle
            row['player_name'], 
            va='top', ha='center', 
            fontsize=6, color='white', 
            zorder=4
        )


    for _, row in away_df.iterrows():
        # Plot player circle
        circle = plt.Circle(
            (row['xplot'], row['yplot']), 
            radius=2.5, 
            color='white', 
            ec='black', 
            zorder=3
        )
        ax.add_patch(circle)

        # Player number inside the circle
        ax.text(
            row['xplot'], row['yplot'], 
            str(row['player_number']), 
            va='center', ha='center', 
            fontsize=8, fontweight='bold', 
            zorder=4
        )

        # Player name underneath
        ax.text(
            row['xplot'], row['yplot'] - 6,  # slightly below the circle
            row['player_name'], 
            va='top', ha='center', 
            fontsize=6, color='white', 
            zorder=4
        )

    return fig, ax