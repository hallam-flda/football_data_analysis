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

def players_plotting_coords(df, home_team = None, away_team = None):

    tidy = df[
    (df['away_team'] == away_team) &
    (df['home_team'] == home_team) &
    (df['home_player_grid'].str.contains(":", na=False))
    ].copy()
    tidy[["home_xplot","home_yplot"]] = tidy["home_player_grid"].str.extract(r'^(\d+):(\d+)$')
    tidy['home_xplot'] = tidy['home_xplot'].astype(float)
    tidy['home_yplot'] = tidy['home_yplot'].astype(float)
    tidy['home_formation_list'] = tidy['home_formation'].str.split('-').to_list()
    tidy['home_xplot'] = np.where(tidy["home_player_pos"] == "G", 5, X_MIN + (tidy['home_xplot'] - 1) * (X_MAX - X_MIN) / tidy['home_formation_list'].apply(len))
    # Calculate max yplot per xplot
    max_y_per_x = tidy.groupby("home_xplot")["home_yplot"].transform("max")
    tidy['home_max_y_per_x'] = max_y_per_x
    denominator = (max_y_per_x - 1).replace(0, 2)
    tidy['denominator'] = denominator  
    tidy['home_yplot'] = np.where(tidy['home_max_y_per_x'] == 1, 2.1, tidy['home_yplot'])
    tidy['home_yplot'] = np.where(
        tidy['home_player_pos'] == "G",
        40,  # fixed y for goalkeeper
        np.where(tidy['home_max_y_per_x'] == 2,
                 (Y_MIN*2) + ((tidy['home_yplot'] - 1) * ((Y_MAX*0.7 - Y_MIN*1.2) / (denominator))),
                    Y_MIN + ((tidy['home_yplot'] - 1) * ((Y_MAX - Y_MIN) / (denominator)))
    )
    )

        # Away team processing (mirrored x-axis)
    tidy[["away_xplot", "away_yplot"]] = tidy["away_player_grid"].str.extract(r'^(\d+):(\d+)$').astype(float)
    tidy['away_formation_list'] = tidy['away_formation'].str.split('-').to_list()
    tidy['away_xplot'] = np.where(
        tidy["away_player_pos"] == "G",
        120 - 5,  # fixed x for GK on opposite side
        120 - (X_MIN + (tidy['away_xplot'] - 1) * (X_MAX - X_MIN) / tidy['away_formation_list'].apply(len))
    )
    tidy['away_max_y_per_x'] = tidy.groupby("away_xplot")["away_yplot"].transform("max")
    away_denominator = (tidy['away_max_y_per_x'] - 1).replace(0, 2)
    tidy['away_yplot'] = np.where(tidy['away_max_y_per_x'] == 1, 2.1, tidy['away_yplot'])
    tidy['away_yplot'] = np.where(
        tidy['away_player_pos'] == "G",
        40,
        np.where(
            tidy['away_max_y_per_x'] == 2,
            (Y_MIN * 2) + ((tidy['away_yplot'] - 1) * ((Y_MAX * 0.7 - Y_MIN * 1.2) / away_denominator)),
            Y_MIN + ((tidy['away_yplot'] - 1) * ((Y_MAX - Y_MIN) / away_denominator))
        )
    )


    return tidy

def plot_pitch_with_players(df):
    pitch = Pitch(
        pitch_color='grass', line_color='white', stripe=True,
        corner_arcs=True, pitch_type='statsbomb'#,
        # axis=True, label=True, tick=True
    )
    fig, ax = pitch.draw()

    for _, row in df.iterrows():
        # Plot player circle
        circle = plt.Circle(
            (row['home_xplot'], row['home_yplot']), 
            radius=2.5, 
            color='white', 
            ec='black', 
            zorder=3
        )
        ax.add_patch(circle)

        circle = plt.Circle(
            (row['away_xplot'], row['away_yplot']), 
            radius=2.5, 
            color='white', 
            ec='black', 
            zorder=3
        )
        ax.add_patch(circle)

        # Player number inside the circle
        ax.text(
            row['home_xplot'], row['home_yplot'], 
            str(row['home_player_number']), 
            va='center', ha='center', 
            fontsize=8, fontweight='bold', 
            zorder=4
        )

        ax.text(
            row['away_xplot'], row['away_yplot'], 
            str(row['away_player_number']), 
            va='center', ha='center', 
            fontsize=8, fontweight='bold', 
            zorder=4
        )

        # Player name underneath
        ax.text(
            row['home_xplot'], row['home_yplot'] - 6,  # slightly below the circle
            row['home_player_name'], 
            va='top', ha='center', 
            fontsize=6, color='white', 
            zorder=4
        )

        ax.text(
            row['away_xplot'], row['away_yplot'] - 6,  # slightly below the circle
            row['away_player_name'], 
            va='top', ha='center', 
            fontsize=6, color='white', 
            zorder=4
        )

    return fig, ax