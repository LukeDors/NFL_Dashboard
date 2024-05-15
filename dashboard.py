import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import matplotlib.pyplot as plt

st.set_page_config(
    page_title='NFL Dashboard',
    page_icon='🏈',
    layout='wide',
    initial_sidebar_state='expanded'
)

#sidebar_cols = st.columns((8,8,8,8))

def create_img(label):
    return st.button(label, key=label)

team_dict = {
    'Arizona Cardinals': 'ARI',
    'Atlanta Falcons': 'ATL',
    'Baltimore Ravens': 'BAL',
    'Buffalo Bills': 'BUF',
    'Carolina Panthers': 'CAR',
    'Cincinnati Bengals': 'CIN',
    'Chicago Bears': 'CHI',
    'Cleveland Browns': 'CLE',
    'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN',
    'Detroit Lions': 'DET',
    'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU',
    'Indianapolis Colts': 'IND',
    'Jacksonville Jaguars': 'JAX',
    'Kansas City Chiefs': 'KC',
    'Las Vegas Raiders': 'OAK',
    'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LA',
    'Miami Dolphins': 'MIA',
    'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE',
    'New Orleans Saints': 'NO',
    'New York Giants': 'NYG',
    'New York Jets': 'NYJ',
    'Philadelphia Eagles': 'PHI',
    'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF',
    'Seattle Seahawks': 'SEA',
    'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN',
    'Washington Commanders': 'WAS'
}

alt.themes.enable('dark')

data = pd.read_csv('data.csv')

col = st.columns((5, 6, 2), gap='medium')

with st.sidebar:
    st.title('NFL Data 2009 to 2018')
    team = st.selectbox('Choose a Team', team_dict.values())

    if team:
        team_data = data.query(f"home_team == '{team}' or away_team == '{team}'")
        season_list = team_data['season'].unique()
        season_list.sort()
        season = st.selectbox('Choose a Season', season_list)

    if season:
        season_data = team_data.query(f"season == '{season}'")
        games = season_data.groupby('game_date').apply(lambda x: (x['home_team'].iloc[0], x['away_team'].iloc[0])).sort_index()
        game_list = []
        game_dict = {}
        for i in range(len(games)):
            t = games[i]
            home = list(team_dict.keys())[list(team_dict.values()).index(t[0])]
            away = list(team_dict.keys())[list(team_dict.values()).index(t[1])]
            game_list.append(f'{away} @ {home}')
            game_dict[f'{away} @ {home}'] = pd.Series(games.index)[i]
        game = st.selectbox('Choose Game', game_list)

    if game:
        game_data = season_data.query(f"game_date == '{game_dict[game]}'")
        drive = st.selectbox('Select a Drive', game_data['drive'].unique())

def make_info(data):
    st.markdown('## Drive Statistics')

    st.markdown('#### Passing')
    passing = data.groupby(['passer_player_name', 'posteam'])[['yards_gained', 'pass_attempt', 'incomplete_pass', 'interception']].sum().sort_values(by='yards_gained', ascending=False).reset_index()
    passing.columns = ['Player', 'Team', 'Yards', 'Attempts', 'Incompletions', 'Interceptions']
    passing = passing.reset_index(drop=True)
    passing['Yards'], passing['Attempts'], passing['Incompletions'], passing['Interceptions'] = passing['Yards'].astype(int), passing['Attempts'].astype(int), passing['Incompletions'].astype(int), passing['Interceptions'].astype(int)
    st.table(passing)

    st.markdown('#### Rushing')
    rushing = data.groupby(['rusher_player_name', 'posteam'])[['yards_gained', 'rush_attempt', 'fumble']].sum().sort_values(by='yards_gained', ascending=False).reset_index()
    rushing.columns = ['Player', 'Team', 'Yards', 'Carries', 'Fumbles']
    rushing = rushing.reset_index(drop=True)
    rushing['Yards'], rushing['Carries'], rushing['Fumbles'] = rushing['Yards'].astype(int), rushing['Carries'].astype(int), rushing['Fumbles'].astype(int)
    st.table(rushing)

    st.markdown('#### Receiving')
    receiving = data.groupby(['receiver_player_name', 'posteam'])[['yards_gained', 'pass_attempt', 'fumble']].sum().sort_values(by='yards_gained', ascending=False).reset_index()
    receiving.columns = ['Player', 'Team', 'Yards', 'Receptions', 'Fumbles']
    receiving = receiving.reset_index(drop=True)
    receiving['Yards'], receiving['Receptions'], receiving['Fumbles'] = receiving['Yards'].astype(int), receiving['Receptions'].astype(int), receiving['Fumbles'].astype(int)
    st.table(receiving)
        


def make_drive(data):
    st.markdown(f"# {data['away_team'].unique()[0]} at {data['home_team'].unique()[0]} {data['season'].unique()[0]}")
    colormap = {
        'extra_point': 'aqua',
        'kickoff': 'violet',
        'pass': 'blue',
        'run': 'red',
        'punt': 'darkgray',
        'field_goal': 'darkgray',
        'no_play': 'yellow',
        'qb_kneel': 'red',
        'qb_spike': 'blue'
    }
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='green'
    )

    data.reset_index(drop=True, inplace=True)
    for i in [0,10,20,30,40,50,60,70,80,90,100]:
        if i == 0 or i == 100:
            fig.add_trace(go.Line(x=[i,i], y=[-100,100], line=dict(color='white', width=2), zorder=4, showlegend=False, opacity=.5))
        else:
            fig.add_trace(go.Line(x=[i,i], y=[-100,100], line=dict(color='white', width=1), zorder=4, showlegend=False, opacity=.5))
    for i, row in data.iterrows():
        if row['yards_gained'] != 0:
            fig.add_trace(go.Bar(x=[row['yards_gained']], y=[data.index[i]], marker_color=colormap[row['play_type']], zorder=2, opacity=1,
                                 base=100-row['yardline_100'], orientation='h', showlegend=False, hovertemplate=row['desc'] + "<extra></extra>"))
        else:
            fig.add_trace(go.Scatter(x=[100 - row['yardline_100']], marker_color=colormap[row['play_type']], 
                            y=[data.index[i]], hoverinfo=None,
                            mode='markers', hovertemplate=row['desc'] + "<extra></extra>", showlegend=False))
    
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="black",
            font_size=14,
            font_family="Calibri"
        ),
        xaxis=dict(
            title='Yardline',
            tickmode='array',
            tickvals=[0,10,20,30,40,50,60,70,80,90,100],
            ticktext=['0','10','20','30','40','50','60','70','80','90','100'],
        ),
        yaxis=dict(
            title='Play Number',
            tickmode='array',
            tickvals=[i for i in list(data.index)],
            ticktext=[str(i+1) for i in list(data.index)]
        ),
        title = f"Summary of Drive {data['drive'][0]}",
        title_x = 0.43,
        legend=dict(
            x=1,
            y=0.5,
            traceorder='normal',
            font=dict(size=12),
            bordercolor='white',
            borderwidth=1
        )
    )
    fig.add_annotation(x=-10, y=len(data)/2, text=data['posteam'][0], textangle=-90, showarrow=False, font=dict(size=60))
    fig.add_annotation(x=110, y=len(data)/2, text=data['defteam'][0], textangle=90, showarrow=False, font=dict(size=60))
    
    fig.update_yaxes(range=[-1, len(data)+1])
    fig.update_xaxes(range=[-20, 120])

    st.markdown(f"### {data['posteam'].unique()[0]} ball")
    st.markdown(f"### Current Score: {data['posteam'].unique()[0]}: {int(data['posteam_score'].unique()[0])} {data['defteam'].unique()[0]}: {int(data['defteam_score'].unique()[0])}")
    return fig

with col[0]:
    if drive:
        plot = make_info(game_data.query(f"drive == {drive}"))

with col[1]:
    if drive:
        plot = make_drive(game_data.query(f"drive == {drive}"))
        st.plotly_chart(plot, use_container_width=True)

with col[2]:
    if drive:
        colormap = {
            'Extra Point': 'aqua',
            'Kickoff': 'violet',
            'Pass/QB Spike': 'blue',
            'Run/QB Kneel': 'red',
            'Field Goal/Punt': 'darkgray',
            'No Play/Penalty': 'yellow',
        }
        legend_html = '<br><ul style="list-style-type: none;padding: 0;display: flex;flex-direction: column">\n'

        for label, color in colormap.items():
            legend_html += f"<li style='margin-bottom: 5px;'>\n<div style='display: inline-block;width: 20px;height: 20px;border-radius: 50%;background-color: {color}'></div>\n&emsp;{label}\n</li>\n"

        legend_html += '</ul>'

        st.markdown("## Legend")

        st.markdown(legend_html, unsafe_allow_html=True)