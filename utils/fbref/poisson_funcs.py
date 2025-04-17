import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import plotly.graph_objects as go
from scipy.stats import poisson

def team_rating_cols(df):
    df['Home_xGp90'] = df['Home_xG']/df["Home_MP"]
    df['Home_xGAp90'] = df['Home_xGA']/df["Home_MP"]
    df['Away_xGp90'] = df['Away_xG']/df["Away_MP"]
    df['Away_xGAp90'] = df['Away_xGA']/df["Away_MP"]
    df['league_home_xGp90'] = df['Home_xGp90'].mean()
    df['league_home_xGAp90'] = df['Home_xGAp90'].mean()
    df['league_away_xGp90'] = df['Away_xGp90'].mean()
    df['league_away_xGAp90'] = df['Away_xGAp90'].mean()
    df['home_att_rating'] = df['Home_xGp90']/df['league_home_xGp90']
    df['home_def_rating'] = df['Home_xGAp90']/df['league_home_xGAp90']
    df['away_att_rating'] = df['Away_xGp90']/df['league_away_xGp90']
    df['away_def_rating'] = df['Away_xGAp90']/df['league_away_xGAp90']
    return df

def poisson_rating(df, home_team, away_team):
    home_team_df = df[df['Squad'] == home_team]
    away_team_df = df[df['Squad'] == away_team]
    home_team_df = home_team_df.iloc[0]
    away_team_df = away_team_df.iloc[0]

    mu_home = home_team_df['league_home_xGp90']
    att_home = home_team_df['home_att_rating']
    def_away = away_team_df['away_def_rating']

    lambda_home = mu_home * att_home * def_away

    mu_away = away_team_df['league_away_xGp90']
    att_away = away_team_df['away_att_rating']
    def_home = home_team_df['home_def_rating']

    lambda_away = mu_away * att_away * def_home

    return lambda_home, lambda_away

def cb_score_spt_assist(team_lambda, cb_goal_contr, spt_assist_contr = 0.47, spt_taker_prop = 0.8):
    pct_chance = 1-np.exp(-team_lambda*cb_goal_contr*spt_assist_contr*spt_taker_prop)
    return pct_chance
    

def poisson_plots(lambda_home, lambda_away):
    x = np.arange(0, 10)

    poisson_home = poisson.pmf(x, mu=lambda_home)
    poisson_away = poisson.pmf(x, mu=lambda_away)

    max_y = max(max(poisson_home), max(poisson_away)) * 1.2  # Add padding

    fig = go.Figure()

    # Home team line
    fig.add_trace(go.Scatter(
        x=x, y=poisson_home,
        mode='lines+markers',
        name='Home Team',
        line=dict(color='dodgerblue', width=2),
        marker=dict(symbol='circle', size=6)
    ))

    # Away team line
    fig.add_trace(go.Scatter(
        x=x, y=poisson_away,
        mode='lines+markers',
        name='Away Team',
        line=dict(color='tomato', width=2),
        marker=dict(symbol='circle', size=6)
    ))

    # Dashed vertical line + annotation: lambda_home
    fig.add_shape(
        type='line',
        x0=lambda_home, x1=lambda_home,
        y0=0, y1=max_y,
        line=dict(color='dodgerblue', width=1, dash='dash')
    )
    fig.add_annotation(
        x=lambda_home, y=max_y,
        text=f"Expected xG = {lambda_home:.2f}",
        showarrow=False,
        font=dict(color='dodgerblue'),
        yshift=10
    )

    # Dashed vertical line + annotation: lambda_away
    fig.add_shape(
        type='line',
        x0=lambda_away, x1=lambda_away,
        y0=0, y1=max_y,
        line=dict(color='tomato', width=1, dash='dash')
    )
    fig.add_annotation(
        x=lambda_away, y=max_y-0.05,
        text=f"Expected xG = {lambda_away:.2f}",
        showarrow=False,
        font=dict(color='tomato'),
        yshift=10
    )

    # Layout and styling
    fig.update_layout(
        title='Poisson Goal Distribution',
        xaxis_title='Goals',
        yaxis_title='Probability',
        yaxis=dict(range=[0, max_y]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(t=60, b=40, l=50, r=50)
    )

    return fig


