import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from mplsoccer import Radar, FontManager, grid
import matplotlib.pyplot as plt
import streamlit as st

## fonts from mpl soccer docs walkthrough

URL1 = ('https://raw.githubusercontent.com/googlefonts/SourceSerifProGFVersion/main/fonts/'
        'SourceSerifPro-Regular.ttf')
serif_regular = FontManager(URL1)
URL2 = ('https://raw.githubusercontent.com/googlefonts/SourceSerifProGFVersion/main/fonts/'
        'SourceSerifPro-ExtraLight.ttf')
serif_extra_light = FontManager(URL2)
URL3 = ('https://raw.githubusercontent.com/google/fonts/main/ofl/rubikmonoone/'
        'RubikMonoOne-Regular.ttf')
rubik_regular = FontManager(URL3)
URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
robotto_thin = FontManager(URL4)
URL5 = ('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
        'RobotoSlab%5Bwght%5D.ttf')
robotto_bold = FontManager(URL5)


import plotly.graph_objects as go
import numpy as np

def mpl_radar_spts(df, home_player, away_player):
    # 1) your raw metric columns
    stats = [
        "live_ball_scas_p90",
        "dead_ball_taken_p90",
        "dead_ball_scas_p90",
        "dead_ball_gcas_p90",
        "dead_ball_sca_eff_p90"
    ]
    # 2) human‑friendly labels (in the same order)
    labels = [
        "Live Ball SCAs",
        "Dead Balls Taken",
        "Dead Ball SCAs",
        "Dead Ball GCAs",
        "Dead Ball SCA Efficiency"
    ]

    # 3) percentile ceiling for the axis
    vals = df[stats].astype(float).values
    high = np.percentile(vals, 95, axis=0).max()

    # 4) extract each player’s values
    home_vals = df.loc[df.player_name == home_player, stats].iloc[0].tolist()
    away_vals = df.loc[df.player_name == away_player, stats].iloc[0].tolist()

    # 5) close the loop
    labels_c = labels + labels[:1]
    home_c  = home_vals  + home_vals[:1]
    away_c  = away_vals  + away_vals[:1]

    # 6) build the figure
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=home_c,
        theta=labels_c,
        fill='toself',
        name=home_player,
        marker_color='#00f2c1',  # teal
        opacity=0.6
    ))
    fig.add_trace(go.Scatterpolar(
        r=away_c,
        theta=labels_c,
        fill='toself',
        name=away_player,
        marker_color='#d80499',  # magenta
        opacity=0.6
    ))

    # 7) layout tweaks for dark mode & square size
    fig.update_layout(
        title=dict(
            text=f"{home_player} vs {away_player}",
            x=0.5,
            font=dict(color='white', size=20)
        ),
        polar=dict(
            bgcolor='#252730',            # chart background
            radialaxis=dict(
                visible=True,
                range=[0, high],
                tickfont=dict(color='white'),
                gridcolor='#39353f'
            ),
            angularaxis=dict(
                tickfont=dict(color='white'),
                gridcolor='#39353f'
            )
        ),
        paper_bgcolor='#252730',          # figure background
        font=dict(color='white'),
        showlegend=True,
        legend=dict(font=dict(color='white')),
        width=600, height=600             # square dimensions
    )

    return fig


# def mpl_radar_spts(df, home_player, away_player):
#     # Show the raw table for inspection (Streamlit)
#     st.dataframe(df)

#     # Explicitly name your columns so order never drifts


#     keep_columns = [
#         "live_ball_scas_p90",
#         "dead_ball_taken_p90",
#         "dead_ball_scas_p90",
#         "dead_ball_gcas_p90",
#         "dead_ball_sca_eff_p90"
#     ]

#     col_headers = [
#         "Live Ball SCAs",
#         "Dead Balls Taken",
#         "Dead Ball SCAs",
#         "Dead Ball GCAs",
#         "Dead Ball SCA Efficiency"
#     ]

#     # Compute 95th‑percentile ceiling
#     vals = df[keep_columns].astype(float).values
#     high = np.percentile(vals, 95, axis=0).tolist()
#     low  = [0.0]*len(keep_columns)

#     # Build the radar
#     radar = Radar(
#         col_headers,           # use the same list here
#         low,
#         high,
#         round_int=[False]*5,
#         num_rings=4,
#         ring_width=1,
#         center_circle_radius=1
#     )

#     # Grab each player’s stats
#     try:
#         home_vals = df.loc[df["player_name"] == home_player, keep_columns].iloc[0].tolist()
#         away_vals = df.loc[df["player_name"] == away_player, keep_columns].iloc[0].tolist()
#     except IndexError as e:
#         raise ValueError("Player not found.") from e

#     # Create a single polar subplot
#     fig, ax = radar.setup_axis(facecolor='#0D1117')

#     fig.patch.set_facecolor('#0D1117')
#     ax.patch .set_facecolor('#0D1117')
#     fig.set_size_inches(12, 12)   # 6×6 inches
#     fig.set_dpi(400)             # fewer pixels

#     # 5) Draw the grid & comparisons
#     radar.draw_circles(
#         ax=ax,
#         facecolor='#28252c',
#         edgecolor='#39353f',
#         lw=1.5
#     )
#     p1, p2, *_ = radar.draw_radar_compare(
#         home_vals,
#         away_vals,
#         ax=ax,
#         kwargs_radar  ={'facecolor': '#00f2c1', 'alpha': 0.6},
#         kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6}
#     )

#     # 6) White labels
#     radar.draw_range_labels(
#         ax=ax,
#         fontsize=15,
#         fontproperties=robotto_thin.prop,
#         color='white'
#     )
#     radar.draw_param_labels(
#         ax=ax,
#         fontsize=15,
#         fontproperties=robotto_thin.prop,
#         color='white'
#     )

#     # 7) Title
#     ax.set_title(
#         f"{home_player} vs {away_player}",
#         color='white',
#         fontsize=20,
#         y=1.1
#     )

#     # 8) legend with transparent frame
#     leg = ax.legend([p1, p2], [home_player, away_player],
#                     loc='upper right', fontsize=12,
#                     frameon=True,  # create the box…
#                     facecolor='none',  # …but make it invisible
#                     edgecolor='none')
#     for t in leg.get_texts():
#         t.set_color('white')

#     # 9) tighten up margins so no white sliver shows
#     fig.subplots_adjust(top=0.85, bottom=0.05, left=0.05, right=0.95)


#     return fig


def radar_spts(df, home_player=None, away_player=None, plot_average=False):
    # Select relevant columns
    keep_columns = df.columns[5:10].tolist()

    # Normalise metrics using Min-Max scaling
    df_norm = df.copy()
    df_norm[keep_columns] = (df[keep_columns] - df[keep_columns].min()) / (df[keep_columns].max() - df[keep_columns].min())

    chart_col_names = ["Live Ball SCAs", "Dead Ball % Taken", "Dead Ball SCAs", "Dead Ball GCAs", "Dead Ball<br>SCA Efficiency"]

    radar_data = []

    if home_player:
        home_player_row = df_norm[df_norm["player_name"] == home_player]
        home_player_values = home_player_row[keep_columns].iloc[0].tolist()
        radar_data.append({
            "Metric": chart_col_names,
            "Value": home_player_values,
            "Label": [home_player] * len(keep_columns)
        })

    if away_player:
        away_player_row = df_norm[df_norm["player_name"] == away_player]
        away_player_values = away_player_row[keep_columns].iloc[0].tolist()  
        radar_data.append({
            "Metric": chart_col_names,
            "Value": away_player_values,
            "Label": [away_player] * len(keep_columns)
        })

    # Averages for all players
    if plot_average:
        avg_values = df_norm[keep_columns].mean().tolist()
        radar_data.append({
            "Metric": chart_col_names,
            "Value": avg_values,
            "Label": ["Set Piece Taker Average"] * len(keep_columns)
        })

    # Combine all data into one DataFrame
    radar_df = pd.concat([pd.DataFrame(d) for d in radar_data], ignore_index=True)

    # Plot
    fig = px.line_polar(radar_df, r="Value", theta="Metric", color="Label", title=f"{home_player} vs {away_player}", line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
        title=dict(
            text=f"{home_player} vs {away_player}",
            x=0.3,          
            y=0.85,         
            xanchor='center',
            yanchor='top',
            font=dict(size=20)
            ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]),
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(
                tickfont=dict(size=14),  
                rotation=90, 
                direction="clockwise" 
            )
        ),
        margin=dict(l=50, r=50, t=50, b=50) 
    )

    return fig

def butterfly_plot_prep(player_df):
    
    player_df = player_df[['ptime_Starts', 'p90_xG', 'p90_Gls', 'player_xG_contr']]
    player_df['player_xG_contr'] = round(player_df['player_xG_contr'],3)
    return player_df

def apply_min_bar(val, raw, min_val=0.05):
    if pd.isna(raw) or pd.isna(val):
        return min_val  # You could also return 0 or skip entirely
    if raw == 0:
        return min_val
    return max(val, min_val)

def cb_butterfly(home_player_df = None, away_player_df = None, home_player=None, away_player=None):
    # Example data
    metrics = ['Starts', 'xG Per 90', 'Goals Per 90', 'Avg Team xG Prop']
    player_a_stats = home_player_df
    player_b_stats = away_player_df

    # Normalise
    max_vals = np.maximum(player_a_stats, player_b_stats)
    player_a_norm = player_a_stats / max_vals
    player_b_norm = player_b_stats / max_vals

    # Apply min bar width
    MIN_BAR_WIDTH = 0.2
    player_a_norm = [apply_min_bar(val, raw) for val, raw in zip(player_a_norm, player_a_stats)]
    player_b_norm = [apply_min_bar(val, raw) for val, raw in zip(player_b_norm, player_b_stats)]

    # Reverse for top-down display
    metrics = metrics[::-1]
    player_a_stats = player_a_stats[::-1]
    player_b_stats = player_b_stats[::-1]
    player_a_norm = player_a_norm[::-1]
    player_b_norm = player_b_norm[::-1]

    fig = go.Figure()

    # Left (Player A) – use negative x
    fig.add_trace(go.Bar(
        y=metrics,
        x=[-v for v in player_a_norm],   # ← negate
        name=home_player,
        orientation='h',
        marker=dict(color='blue', opacity=0.9),
        width=0.4,
        hoverinfo='skip',
        cliponaxis=False,
        xaxis='x1'
    ))

    # Right (Player B)
    fig.add_trace(go.Bar(
        y=metrics,
        x=player_b_norm,
        name=away_player,
        orientation='h',
        marker=dict(color='red', opacity=0.9),
        width=0.4,
        cliponaxis=False,
        xaxis='x2'
    ))

    # Add metric names in the centre
    for i, metric in enumerate(metrics):
        fig.add_annotation(
            x=0.5, y=i, xref='paper', yref='y',
            text=metric,
            showarrow=False,
            font=dict(color='white', size=12),
            xanchor='center',
            yanchor='middle'
        )
    
    for i, val in enumerate(player_a_stats):
        fig.add_annotation(
            x=-player_a_norm[i] - 0.02,   # just outside the bar
            y=i,
            xref='x1',
            yref='y',
            text=str(val),
            showarrow=False,
            font=dict(color='white', size=12),
            xanchor='right',
            yanchor='middle'
        )

    
    for i, val in enumerate(player_b_stats):
        fig.add_annotation(
            x=player_b_norm[i] + 0.01,
            y=i,
            xref='x2',
            yref='y',
            text=str(val),
            showarrow=False,
            font=dict(color='white', size=12),
            xanchor='left',
            yanchor='middle'
        )

    # Layout with two side-by-side axes
    fig.update_layout(
        title=f'{home_player} vs {away_player}',
        barmode='overlay',
        xaxis=dict(
            domain=[0, 0.38],
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        xaxis2=dict(
            domain=[0.62, 1],
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=200,
        margin=dict(l=40, r=40, t=20, b=20),
        bargap=0.8,
        legend=dict(orientation='h', x=0.7, xanchor='center', y=1.5)
    )

    return fig