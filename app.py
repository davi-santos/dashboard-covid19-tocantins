import pandas as pd
import numpy as np
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import json
import plotly.graph_objects as go

# ---------- READING DATA AND CALCULATING VARIABLES -------------

# Read data from csv
df = pd.read_csv('./data/tocantins.csv')
df_tocantins = df[~df['municipio'].isna()]
tocantins_regioes = json.load(open('tocantins.json', 'r'))
map_background_color = '#fafaf8'

# preprocessing
df_tocantins['casosNovos'] = df_tocantins['casosNovos'].apply(lambda x: x if x > 0 else 0)
df_tocantins['casosAcumulado'] = df_tocantins['casosAcumulado'].apply(lambda x: x if x > 0 else 0)
df_tocantins['obitosAcumulado'] = df_tocantins['obitosAcumulado'].apply(lambda x: x if x > 0 else 0)
df_tocantins['obitosNovos'] = df_tocantins['obitosNovos'].apply(lambda x: x if x>0 else 0)

#logos
github_icon_path = 'github.png'
#github_icon_encode = base64.b64encode(open(github_icon_path, 'rb').read()).decode('ascii')

DROPDOWN_OPTIONS = 'casosAcumulado casosNovos obitosAcumulado obitosNovos'.split()
MUNICIPIOS_E_TOCANTINS = np.append(df_tocantins['municipio'].unique(),'Tocantins')
CITY_OPTIONS = 'casosAcumulado casosNovos obitosAcumulado'.split()
OPTIONS_CASES_LISTOFDICT = [{'label': 'Casos Acumulados', 'value': 'casosAcumulado'},
                            {'label': 'Casos Novos', 'value': 'casosNovos'},
                            {'label': 'Óbitos Acumulados', 'value': 'obitosAcumulado'},
                            {'label': 'Óbitos Novos', 'value': 'obitosNovos'}]

# Casos CARD
df_casosCard = df_tocantins[['casosAcumulado', 'data']].sort_values(by='data').groupby('data').sum()
size_casosCard = len(df_casosCard)
casosCardValue = df_casosCard.iloc[size_casosCard-1:]['casosAcumulado'][0]
casosCard = '{0:,}'.format(int(casosCardValue)).replace(',','.')

# Óbitos CARD
df_obitosCard = df_tocantins[['obitosAcumulado', 'data']].sort_values(by='data').groupby('data').sum()
size_obitosTO = len(df_obitosCard)
obitosCardValue = df_obitosCard.iloc[size_obitosTO-1:]['obitosAcumulado'][0]
obitosCard = '{0:,}'.format(int(obitosCardValue)).replace(',','.')

# Recuperados CARD
recuperadosCardValue = casosCardValue-obitosCardValue
recuperadosCard = '{0:,}'.format(int(recuperadosCardValue)).replace(',','.')

# --------- functions ----------------

def getNameCase(case=''):
    name_case = ''
    
    if case=='':
        name_case='NULL'

    if case == 'casosAcumulado':
        name_case = 'Casos Acumulados'
    elif case == 'casosNovos':
        name_case = 'Casos Novos'
    elif case == 'obitosAcumulado':
        name_case = 'Óbitos Acumulados'
    else:
        name_case = 'Óbitos Novos'
    
    return name_case

# ---------- Dash app -----------------

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

# ------------- App Layout --------------

app.layout = dbc.Container([
    #Row 1
    dbc.Row(children=[
        dbc.Col(children=[
            html.H4('Dashboard covid-19 Tocantins', className='text-left mt-3 mb-3 ml-5'),
        ], width=5,
        ),
        dbc.Col(children=[
            html.A(
                html.Img(src=app.get_asset_url('github.png')),
                href='https://www.w3schools.com/cssref/css_colors.asp', 
                target='_blank'
            ),
            html.A(
                html.Img(src=app.get_asset_url('medium.png'), style={"margin-left": "10px"}), 
                href='#',
                target='_blank'
            ),
            html.A(
                html.Img(src=app.get_asset_url('linkedin-logo.png'), style={"margin-left": "10px"}), 
                href='https://www.linkedin.com/in/davi-santos-datascientist/',
                target='_blank'
            )], 
            width=1, className='text-right mt-3 mb-3'
        )],
        justify='between', align='center', className='bg-white border border-black text-black mb-2 mt-0'
    ),
    dbc.Row([        
        dbc.Col([
            dbc.Row(
                dbc.Col(children=[
                    html.H5('Dados Gerais no Tocantins', className='text-center mt-2'),
                    html.P('Os dados adquiridos são oficiais do ministério da saúde. Os cartões em destaque apresentam o acumulado no Estado do Tocantins. Para mais detalhes, utilizar as opções gráficas abaixo e o mapa do Tocantins ao lado.', className='text-black')
                ])
            ),
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardHeader(children=[
                            html.H5('Casos'),
                            html.H4(casosCard)
                        ], className='text-black', style={'background-color': '#FFFACD'}),
                    ), 
                    width=4
                    #F0E68C
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardHeader(children=[
                            html.H5('Recuperados'),
                            html.H4(recuperadosCard)
                        ], className='text-black', style={'background-color': '#98FB98'})
                    ), width=4
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardHeader(children=[
                            html.H5('Óbitos'),
                            html.H4(obitosCard)
                        ], className='text-black', style={'background-color': '#FFB6C1'})
                    ), width=4
                )
            ], className='mb-3 mt-0 text-center text-black'),
            dbc.Row(children=[
                dbc.Col(
                    dbc.Tabs(children=[
                        dbc.Tab(children=[
                            dbc.Row([
                                dbc.Col(
                                    children=[
                                        dcc.Dropdown(options=OPTIONS_CASES_LISTOFDICT, id='city-options', value='casosAcumulado', style={'background-color':map_background_color}),
                                        dcc.Graph(id='top-10-cities', figure={})
                                    ],
                                    width=12,
                                    className='border-0'
                                )
                            ], className='mt-2')
                        ],label="Cidades mais impactadas", tab_id="tab-2", label_style={'color': 'black'}),
                        dbc.Tab(children=[
                            dbc.Row(children=[
                                dbc.Col(
                                    dcc.Dropdown(options=[{'label': x, 'value': x} for x in MUNICIPIOS_E_TOCANTINS], 
                                        id='drop-cidade', value='Tocantins', style={'background-color': map_background_color}),
                                    width=6,
                                ),
                                dbc.Col(
                                    dcc.Dropdown(options=OPTIONS_CASES_LISTOFDICT, id='drop-caso', value='casosAcumulado', style={'background-color':map_background_color}),
                                    width=6
                                ), 
                            ], className='mt-2'),
                            dbc.Row(children=[
                            dbc.Col(
                                dcc.Graph(id='general-graph', figure={}),
                                width=12,
                                className='border-0'
                            ),
                        ], style={'color':'black'}),
                        ],label="Dados Gerais no Tocantins", tab_id="tab-1", label_style={'color': 'black'}),
                    ], className=''),
                )
            ], justify='center',),
        ], width=5, className='mt-3'),
        dbc.Col(
            html.Div(children=[
                dbc.RadioItems(
                    id="radios",
                    className="btn-group mt-2 mb-2",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-dark",
                    labelCheckedClassName="active",
                    options=[
                        {'label': 'Casos Novos', 'value':'casosNovos'},
                        {'label': 'Casos Acumulados', 'value':'casosAcumulado'},
                        {'label': 'Óbitos Novos', 'value':'obitosNovos'},
                        {'label': 'Óbitos Acumulados', 'value':'obitosAcumulado'},
                        
                    ],
                    value='casosNovos'
                ),
                dcc.Graph(id="choropleth-map", figure={}, style={'height': '84vh'})],
                className='text-center ml-5', style={'background-color': map_background_color}
            ), width=6,  style={'background-color': map_background_color}, className='mt-3'    
        ),
    ],
    className='ml-5', justify='center'), 
    
], fluid=True, style={'background-color': map_background_color})


# --------- App callbacks ------
@app.callback(
    Output(component_id='general-graph', component_property='figure'),
    [Input(component_id='drop-cidade', component_property='value'), Input('drop-caso', 'value')]
)
def something(city, feature_chosen):
    figure = {}
    figure_title = getNameCase(feature_chosen)

    if city=='Tocantins':
        df_copy = df_tocantins[[feature_chosen,'data']].groupby('data').sum()
        figure = px.line(df_copy, x=df_copy.index, y=feature_chosen, title=f'{figure_title} - Tocantins', color_discrete_sequence=px.colors.qualitative.D3)
    else:
        df_copy = df_tocantins[df_tocantins['municipio'] == city][[feature_chosen,'data']].groupby('data').sum()
        figure = px.line(df_copy, x=df_copy.index, y=feature_chosen, title=f'{figure_title} - {city}', color_discrete_sequence=px.colors.qualitative.D3)

    figure.update_layout(paper_bgcolor=map_background_color)

    return figure

@app.callback(
    Output(component_id='top-10-cities', component_property='figure'),
    [Input(component_id='city-options', component_property='value')]
)
def updateFigureTopCities(city_option):
    
    fig_title = getNameCase(city_option)

    df_copy = df_tocantins[[city_option, 'municipio']].groupby('municipio').max().sort_values(city_option, ascending=False)[:10]
    fig = px.bar(df_copy, x=df_copy.index, y=city_option, title=f'{fig_title} - 10 cidades em destaque', color_discrete_sequence=px.colors.qualitative.D3)

    fig.update_layout(paper_bgcolor=map_background_color)

    return fig

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('radios', 'value')]
)
def update_Tocantins_map(option_chosen):

    df_copy = df_tocantins[df_tocantins['data'] == '2022-02-10'].copy()
    max_value = df_copy[option_chosen].max()
    min_value = df_copy[option_chosen].min()

    fig = px.choropleth_mapbox(df_copy, locations='municipio', 
                    color=option_chosen, geojson=tocantins_regioes,
                    range_color=(min_value,max_value),
                    featureidkey='properties.name',
                    zoom=6,
                    center={"lat": -9.370232849190968, "lon": -47.926742249757595},
                          color_continuous_scale='oryel')
                          # os que gostei: ylorrd, turbid, sunsetdark, speed, ++ pinkyl, peach
                          # NOVOS q gostei: oryel (best of all), mint, matter (good)
    fig.update_layout(
                    paper_bgcolor=map_background_color,
                    mapbox_style="carto-positron",
                    autosize=True,
                    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                    showlegend=False,)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)