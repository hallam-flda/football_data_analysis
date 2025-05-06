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

def players_plotting_coords(home_team_df = None, away_team_df = None):

    home = home_team_df[(home_team_df['player_grid'].str.contains(":", na=False))].copy()
    home[["xplot","yplot"]] = home["player_grid"].str.extract(r'^(\d+):(\d+)$')
    home['xplot'] = home['xplot'].astype(float)
    home['yplot'] = home['yplot'].astype(float)
    home['formation_list'] = home['formation'].str.split('-').to_list()
    home['xplot'] = np.where(home["player_pos"] == "G", 5, X_MIN + (home['xplot'] - 1) * (X_MAX - X_MIN) / home['formation_list'].apply(len))
    # Calculate max yplot per xplot
    max_y_per_x = home.groupby("xplot")["yplot"].transform("max")
    home['max_y_per_x'] = max_y_per_x
    denominator = (max_y_per_x - 1).replace(0, 2)
    home['denominator'] = denominator  
    home['yplot'] = np.where(home['max_y_per_x'] == 1, 2.1, home['yplot'])
    home['yplot'] = np.where(
        home['player_pos'] == "G",
        40,  # fixed y for goalkeeper
        np.where(home['max_y_per_x'] == 2,
                 (Y_MIN*2) + ((home['yplot'] - 1) * ((Y_MAX*0.7 - Y_MIN*1.2) / (denominator))),
                    Y_MIN + ((home['yplot'] - 1) * ((Y_MAX - Y_MIN) / (denominator)))
    )
    )

    # Away team processing (mirrored x-axis)
    away = away_team_df[(away_team_df['player_grid'].str.contains(":", na=False))].copy()
    away[["xplot", "yplot"]] = away["player_grid"].str.extract(r'^(\d+):(\d+)$').astype(float)
    away['formation_list'] = away['formation'].str.split('-').to_list()
    away['xplot'] = np.where(
        away["player_pos"] == "G",
        120 - 5,  # fixed x for GK on opposite side
        120 - (X_MIN + (away['xplot'] - 1) * (X_MAX - X_MIN) / away['formation_list'].apply(len))
    )
    away['max_y_per_x'] = away.groupby("xplot")["yplot"].transform("max")
    denominator = (away['max_y_per_x'] - 1).replace(0, 2)
    away['yplot'] = np.where(away['max_y_per_x'] == 1, 2.1, away['yplot'])
    away['yplot'] = np.where(
        away['player_pos'] == "G",
        40,
        np.where(
            away['max_y_per_x'] == 2,
            (Y_MIN * 2) + ((away['yplot'] - 1) * ((Y_MAX * 0.7 - Y_MIN * 1.2) / denominator)),
            Y_MIN + ((away['yplot'] - 1) * ((Y_MAX - Y_MIN) / denominator))
        )
    )


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