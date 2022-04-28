import pandas as pd
import numpy as np
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import json
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

# ----------- READ DATA -------------------
df = pd.read_csv('./data/tocantins.csv', sep=';')
df_tocantins = df[~df['municipio'].isna()]
df_tocantins.drop(df_tocantins.loc[:,['Unnamed: 0']], axis=1, inplace=True)
tocantins_geojson = json.load(open('tocantins.json', 'r'))

# ---------- PREPROCESSING ---------------
# Change data to datetime type
df_tocantins['data'] = pd.to_datetime(df_tocantins['data'])

#change object type to string stype

df_tocantins = df_tocantins.astype({'regiao': 'str',
                                    'estado': 'str',
                                    'nomeRegiaoSaude': 'str'
                                   })

#change float columns to integer
df_tocantins = df_tocantins.astype({'codmun': 'int64', 
                                    'codRegiaoSaude': 'int64',
                                    'populacaoTCU2019': 'int64',
                                    'casosAcumulado': 'int64',
                                    'interior/metropolitana': 'int64'
                                    })

# Change columns names
new_columns = ['Região', 'Estado', 'Município', 'Código UF', 'Código Município',
               'Código Região Saúde','Nome Região Saúde', 'Data', 'Semana EPI', 
               'População TCU 2019', 'Casos Acumulados', 'Casos Novos', 
               'Óbitos Acumulados','Óbitos Novos', 'Recuperados Novos', 
               'Acompanhamento Novos','Metropolitana']

df_tocantins.columns = new_columns

# Remove columns 
df_tocantins.drop('Acompanhamento Novos', axis=1, inplace=True)
df_tocantins.drop('Recuperados Novos', axis=1, inplace=True)

# Change numbers to category names to column Metropolitana
df_tocantins.loc[df_tocantins['Metropolitana'] == 1,'Metropolitana'] = 'Metropolitana'
df_tocantins.loc[df_tocantins['Metropolitana'] == 0,'Metropolitana'] = 'Interior'

# preprocessing
df_tocantins.loc[df_tocantins['Casos Novos'] < 0,'Casos Novos'] = 0
df_tocantins.loc[df_tocantins['Casos Acumulados'] < 0,'Casos Acumulados'] = 0
df_tocantins.loc[df_tocantins['Óbitos Acumulados'] < 0,'Óbitos Acumulados'] = 0
df_tocantins.loc[df_tocantins['Óbitos Novos'] < 0,'Óbitos Novos'] = 0

#filter data before April 17th
df_tocantins = df_tocantins.loc[df_tocantins['Data'] < '2022-04-18']

#logos
github_icon_path = 'github.png'
#github_icon_encode = base64.b64encode(open(github_icon_path, 'rb').read()).decode('ascii')

## CONSTANTS
FIG_CASOS_NOVOS_MAP = {}
FIG_CASOS_ACUMULADOS_MAP = {}
FIG_OBITOS_NOVOS_MAP = {}
FIG_OBITOS_ACUMULADOS_MAP = {}
FIG_REGIAO_SAUDE_MAP = {}
FIG_REGIAO_INTERIOR_MAP = {}

map_background_color = '#fafaf8'
# bg_selected_color = '#e6e6d3'
bg_selected_color = '#e2e9ed'
tab_colors = '#e2e9ed'

DROPDOWN_OPTIONS = ['Casos Acumulados', 'Casos Novos', 'Óbitos Acumulados', 'Óbitos Novos']
MUNICIPIOS_E_TOCANTINS = np.append(df_tocantins['Município'].unique(),'Tocantins')
CITY_OPTIONS = ['Casos Acumulados', 'Casos Novos', 'Óbitos Acumulados']
OPTIONS_CASES_LISTOFDICT = [{'label': 'Casos Acumulados', 'value': 'Casos Acumulados'},
                            {'label': 'Casos Novos', 'value': 'Casos Novos'},
                            {'label': 'Óbitos Acumulados', 'value': 'Óbitos Acumulados'},
                            {'label': 'Óbitos Novos', 'value': 'Óbitos Novos'}]

OPTIONS_REGIAO_SAUDES = [{'label': 'Casos Acumulados por região no tempo', 'value': 'Casos Acumulados'},
                        {'label': 'Casos Acumulados totais', 'value': 'Casos Acumulados2'},
                        {'label': 'Óbitos Acumulados por região no tempo', 'value': 'Óbitos Acumulados'},
                        {'label': 'Óbitos Acumulados totais', 'value': 'Óbitos Acumulados2'},
]

OPTIONS_INTERIOR = [{'label': 'Casos Acumulados Interior', 'value': 'Casos Acumulados'},
                    {'label': 'Óbitos Acumulados Interior', 'value': 'Óbitos Acumulados'}]

# Casos CARD
df_casosCard = df_tocantins[['Casos Acumulados', 'Data']].sort_values(by='Data').groupby('Data').sum()
size_casosCard = len(df_casosCard)
casosCardValue = df_casosCard.iloc[size_casosCard-1:]['Casos Acumulados'][0]
casosCard = '{0:,}'.format(int(casosCardValue)).replace(',','.')

# Óbitos CARD
df_obitosCard = df_tocantins[['Óbitos Acumulados', 'Data']].sort_values(by='Data').groupby('Data').sum()
size_obitosTO = len(df_obitosCard)
obitosCardValue = df_obitosCard.iloc[size_obitosTO-1:]['Óbitos Acumulados'][0]
obitosCard = '{0:,}'.format(int(obitosCardValue)).replace(',','.')

# Recuperados CARD
recuperadosCardValue = casosCardValue-obitosCardValue
recuperadosCard = '{0:,}'.format(int(recuperadosCardValue)).replace(',','.')

# ---------- Dash app -----------------

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB],
        meta_tags=[{'name': 'viewport', 'content': 'width=device-width,initial-scale=1.0'}])
server = app.server

# ------------- App Layout --------------

app.layout = dbc.Container([
    #Row 1
    dbc.Row(children=[
        dbc.Col(children=[
            html.H4('Dashboard covid-19 Tocantins', className='text-left mt-3 mb-3 ml-5 text-black'),
        ], xxl=5, xl=5, lg=5, md=7, sm=7, xs=9
        ),
        dbc.Col(children=[
            html.A(
                html.Img(src=app.get_asset_url('github.png')),
                href='https://github.com/davi-santos/dashboard-covid19-tocantins/tree/main', 
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
             xxl=1, xl=2, lg=2, md=2, sm=3, xs=3, className='text-right mt-3 mb-3'
        )],
        justify='between', align='center', className='border border-black text-black mb-2 mt-0',
        style={'background-color': bg_selected_color}
    ),
    dbc.Row([        
        dbc.Col([
            dbc.Row(
                dbc.Col(children=[
                    html.H5('Dados Gerais no Tocantins', className='text-center mt-2'),
                    html.P('Os dados adquiridos são oficiais do ministério da saúde. \
                        Os cartões em destaque apresentam o acumulado no Estado do Tocantins. \
                            Para mais detalhes, utilizar as opções gráficas abaixo e o mapa do Tocantins ao lado.', 
                    className='text-black')
                ])
            ),
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardHeader(children=[
                            html.H5('Casos'),
                            html.H4(casosCard)
                        ], className='text-light', style={'background-color': '#333333'}),
                    ), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardHeader(children=[
                            html.H5('Recuperados'),
                            html.H4(recuperadosCard)
                        ], className='text-light', style={'background-color': '#333333'})
                    ), width=4
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardHeader(children=[
                            html.H5('Óbitos'),
                            html.H4(obitosCard)
                        ], className='text-light', style={'background-color': '#333333'})
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
                                        dcc.Dropdown(options=OPTIONS_CASES_LISTOFDICT, id='city-options', value='Casos Acumulados', 
                                        style={'background-color':map_background_color}),
                                        dcc.Loading(dcc.Graph(id='top-10-cities', figure={})),
                                    ],
                                    width=12,
                                    className='border-0'
                                )
                            ], className='mt-2')
                        ],label="Cidades mais impactadas", active_label_style={"background-color": tab_colors},
                        tab_id="tab-2", label_style={'color': 'black'}),
                        dbc.Tab(children=[
                            dbc.Row(children=[
                                dbc.Col(
                                    dcc.Dropdown(options=[{'label': x, 'value': x} for x in MUNICIPIOS_E_TOCANTINS], 
                                        id='drop-cidade', value='Tocantins', style={'background-color': map_background_color}),
                                    width=6,
                                ),
                                dbc.Col(
                                    dcc.Dropdown(options=OPTIONS_CASES_LISTOFDICT, id='drop-caso', value='Casos Acumulados', 
                                    style={'background-color':map_background_color}),
                                    width=6
                                ), 
                            ], className='mt-2'),
                            dbc.Row(children=[
                            dbc.Col(
                                dcc.Loading(type='default', children=[dcc.Graph(id='general-graph', figure={})]),
                                width=12,
                                className='border-0'
                            ),
                        ], style={'color':'black'}),
                        ],label="Dados Gerais no Tocantins", active_label_style={"background-color": tab_colors},
                        tab_id="tab-1", label_style={'color': 'black'}),
                        dbc.Tab(children=[
                            dbc.Row([
                                dbc.Col(
                                    children=[
                                        dcc.Dropdown(options=OPTIONS_REGIAO_SAUDES, id='regioes-saude-options', 
                                        value='Casos Acumulados', style={'background-color':map_background_color}),
                                        dcc.Loading(children=[dcc.Graph(id='regiao-graph', figure={})], type='default'),
                                        
                                    ],
                                    width=12,
                                    className='border-0'
                                )
                            ], className='mt-2')
                        ],label="Regiões de Saúde", active_label_style={"background-color": tab_colors},tab_id="tab-3", 
                        label_style={'color': 'black'}),
                    dbc.Tab(children=[
                            dbc.Row([
                                dbc.Col(
                                    children=[
                                        dcc.Dropdown(options=OPTIONS_INTERIOR, id='interior-options', value='Casos Acumulados', style={'background-color':map_background_color}),
                                        dcc.Graph(id='interior-graph', figure={})
                                    ],
                                    width=12,
                                    className='border-0'
                                )
                            ], className='mt-2')
                        ],label="Interior", active_label_style={"background-color": tab_colors}, 
                        tab_id="tab-4", label_style={'color': 'black'}),
                    ], className=''),
                )
            ], justify='center',),
        ], xxl=5, xl=5, lg=12, md=12, sm=12, xs=12, className='mt-3'),
        dbc.Col(
            html.Div(children=[
                dbc.RadioItems(
                    id="radios",
                    className="btn-group mt-1 mb-1",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-dark",
                    labelCheckedClassName="active",
                    options=[
                        {'label': 'Casos Acumulados', 'value':'Casos Acumulados'},
                        {'label': 'Casos Novos', 'value':'Casos Novos'},
                        {'label': 'Óbitos Acumulados', 'value':'Óbitos Acumulados'},
                        {'label': 'Óbitos Novos', 'value':'Óbitos Novos'},
                        {'label': 'Região de Saúde', 'value':'Nome Região Saúde'},
                        {'label': 'Região do Interior', 'value':'Metropolitana'},
                    ],
                    value='Casos Acumulados'
                ),
                dcc.Loading(
                    id='loading-1', type='default', children=[dcc.Graph(id="choropleth-map", figure={}, style={'height': '84vh'})]
                )],
                className='text-center ml-5', style={'background-color': map_background_color}
            ), xxl=7, xl=7, lg=12, md=12, sm=12, xs=12,  style={'background-color': map_background_color}, className='mt-3'    
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
    
    if not city or not feature_chosen:
        raise PreventUpdate

    figure = {}

    if city=='Tocantins':
        df_copy = df_tocantins[[feature_chosen,'Data']].groupby('Data').sum()
        figure = px.line(df_copy, x=df_copy.index, y=feature_chosen, title=f'{feature_chosen} - Tocantins', color_discrete_sequence=px.colors.qualitative.D3)
    else:
        df_copy = df_tocantins[df_tocantins['Município'] == city][[feature_chosen,'Data']].groupby('Data').sum()
        figure = px.line(df_copy, x=df_copy.index, y=feature_chosen, title=f'{feature_chosen} - {city}', color_discrete_sequence=px.colors.qualitative.D3)

    figure.update_layout(paper_bgcolor=map_background_color)

    return figure

@app.callback(
    Output(component_id='top-10-cities', component_property='figure'),
    [Input(component_id='city-options', component_property='value')]
)
def updateFigureTopCities(city_option):
    
    if not city_option:
        raise PreventUpdate

    n_cities = 5

    df_copy = df_tocantins[[city_option, 'Município']].groupby('Município').max().sort_values(city_option, ascending=False)[:n_cities]
    fig = px.bar(df_copy, x=df_copy.index, y=city_option, title=f'{city_option} - {n_cities} cidades em destaque', 
    color_discrete_sequence=px.colors.qualitative.Vivid)
    #Prism = roxo (bom), Safe = azul claro (bom), Set3 = verde claro (bonito), Vivid=amarelo forte (perfeito)
    #

    fig.update_layout(paper_bgcolor=map_background_color)

    return fig

@app.callback(
    Output('regiao-graph', 'figure'),
    [Input('regioes-saude-options', 'value')]
)
def updateRegiaoTab(option_chosen):

    if not option_chosen:
        raise PreventUpdate

    fig = {}

    if option_chosen=='Casos Acumulados' or option_chosen=='Óbitos Acumulados':
        df = df_tocantins[[option_chosen, 'Nome Região Saúde', 'Data']]\
                                .groupby(['Nome Região Saúde', 'Data']).sum().reset_index()
        fig = px.line(df, x='Data', color='Nome Região Saúde', y=option_chosen, 
                title=f'{option_chosen} por Região de Saúde no tempo')

        fig.update_layout(showlegend=False, paper_bgcolor=map_background_color,)
    else:
        option_chosen=option_chosen[:-1]
        most_recent_date = df_tocantins['Data'].max().date().isoformat()
        df = df_tocantins[df_tocantins['Data'] == most_recent_date][[option_chosen, 'Nome Região Saúde']]\
                        .groupby('Nome Região Saúde').sum()
        fig = px.bar(df, df.index, option_chosen, title=f'{option_chosen} por Região de Saúde',
            color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(showlegend=False, paper_bgcolor=map_background_color,)

    return fig

@app.callback(
    Output('interior-graph', 'figure'),
    [Input('interior-options', 'value')]
)
def updateInteriorGraph(option_chosen):

    if not option_chosen:
        raise PreventUpdate

    fig = {}

    df = df_tocantins.groupby(['Data', 'Metropolitana'])\
        .sum().reset_index().sort_values(option_chosen)

    fig = px.line(data_frame=df, x='Data', y=option_chosen, color='Metropolitana', 
            title=f'{option_chosen} entre interior e metrópole no tempo')
    fig.update_layout(paper_bgcolor=map_background_color)

    return fig

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('radios', 'value')]
)
def update_Tocantins_map(option_chosen):

    if not option_chosen:
        raise PreventUpdate

    #mudar data para mais recente, tirar essa
    # most_recent_date = df_tocantins['Data'].max()
    # df_copy = df_tocantins[df_tocantins['Data'] == most_recent_date].copy()
    df_copy = df_tocantins[df_tocantins['Data'] == '2022-02-10'].copy()
    max_value = df_copy[option_chosen].max()
    min_value = df_copy[option_chosen].min()

    fig = px.choropleth_mapbox(df_copy, locations='Município', 
                    color=option_chosen, geojson=tocantins_geojson,
                    range_color=(min_value,max_value),
                    featureidkey='properties.name',
                    zoom=6,
                    center={"lat": -9.370232849190968, "lon": -47.926742249757595},
                          color_continuous_scale='oryel')
    fig.update_layout(
                    paper_bgcolor=map_background_color,
                    mapbox_style="carto-positron",
                    autosize=True,
                    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                    showlegend=True)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)