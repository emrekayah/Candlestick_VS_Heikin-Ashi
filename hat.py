from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

symbol='ETH-USD'
radios="1d"
def up_data(symbol,radios):
    end_date= date.today().strftime("%Y-%m-%d")
    start_date= (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    df = yf.download(symbol, 
                   interval=radios,
                   start=start_date, 
                   end=end_date, 
                   progress=False)
    df["Date"] = df.index
    df = df[["Date", "Open", "High", "Low", 
             "Close", "Adj Close", "Volume"]]

    df["Close_hk"]=(df["Open"]+df["High"]+df["Low"]+df["Close"])/4
    df["Open_hk"]=(df["Open"].shift(1)+df["Close"].shift(1))/2

    df.reset_index(drop=True, inplace=True)
    return df



app.layout = dbc.Container([
    html.H1(' Candlestick Chart vs Heikin-Ashi Chart', style={'textAlign': 'center'}),
     
    dbc.Row([
        dbc.Col([html.Label('symbol:'),
                  dcc.Input(id="symbol", type="text", placeholder="", style={'marginRight':'10px'}),], width=4),
        dbc.Col( [dbc.RadioItems(
            id="radios",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[
                {"label": "5 minute", "value":"5m"},
                {"label": "1 hour  ", "value":"1h"},
                {"label": "1 day   ", "value":"1d"},
                {"label": "1 week  ", "value":"1wk"} 
            ],
            value="1d",
        ),],
        className="radio-group"
        ), 
    ]),

    dbc.Row([
        dbc.Col([html.Label('CandleStick Chart')], width=dict(size=4, offset=2)),
        dbc.Col([html.Label('Heikin-Ashi')], width=dict(size=4, offset=2))
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id='candle', figure={}, style={'height': '80vh'})], width=6),
        dbc.Col([dcc.Graph(id='hk', figure={}, style={'height': '80vh'})], width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Checklist(
        id='toggle_rangeslider',
        options=[{'label': ' Include Rangeslider','value': 'slider'}],
        value=['slider']        
    ),),
    ]),
], fluid=True)


@callback(
    Output(component_id='candle', component_property='figure'),
    Output(component_id='hk', component_property='figure'),
    Input(component_id='symbol', component_property='value'),
    Input("toggle_rangeslider", "value"),
    Input("radios", "value"))

def build_graphs(symbol,toggle_rangeslider,radios): 
    df=up_data(symbol,radios) 

    print(symbol)
    print(df.head())

    fig_candle = go.Figure(
        go.Candlestick(x=df['Date'],
                       open=df['Open'],
                       high=df['High'],
                       low=df['Low'],
                       close=df['Close'],
                       text=df['Volume'])
    )

    fig_candle.update_layout(margin=dict(t=30, b=30)) 
    fig_candle.update_yaxes(tickprefix="$") 
    fig_candle.update_layout( xaxis_rangeslider_visible='slider' in toggle_rangeslider)

    fig_hk = go.Figure(
        go.Candlestick(x=df['Date'],
                       open=df['Open_hk'],
                       high=df['High'],
                       low=df['Low'],
                       close=df["Close_hk"],
                       text=df['Volume'])
    )

    fig_hk.update_layout(margin=dict(t=30, b=30))
    fig_hk.update_yaxes(tickprefix="$") 
    fig_hk.update_layout( xaxis_rangeslider_visible='slider' in toggle_rangeslider) 
    return fig_candle, fig_hk

if __name__=='__main__':
    app.run_server()