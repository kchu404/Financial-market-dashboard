import pandas as pd 
from dash import Dash, dcc, html
import plotly.express as px
from dash.dependencies import Input, Output

#automate financial data ingestion

# Load CSV file (financial market data from Kaggle)
df = pd.read_csv("global_financial_markets_2000_Now.csv")


# Show summary 
print(df.head())
print(df.describe())


# Cleaning and preprocessing data

#sorting data
df = df.sort_values(['symbol', 'date'])
df['indexed_price'] = df.groupby('asset_name')['close'].transform(lambda x: (x / x.iloc[0]) * 100)

#Remove duplicates 
df = df.drop_duplicates() 

# Fill missing price values
price_col = ['open', 'high', 'low', 'close']
df[price_col] = df.groupby('symbol')[price_col].transform(lambda x: x.ffill())

#fill missing volume values
df['volume'] = df.groupby('symbol')['volume'].transform(lambda x: x.fillna(0))

# drop unusable rows
df = df.dropna(subset=['symbol', 'close'])

# Convert dates -> converts date to datetime object 
df['date'] = pd.to_datetime(df['date'])

#initialise multiline chart  
app = Dash(__name__)
app.layout = html.Div([
    html.H1("Stock Market Financial Dashboard"),
    dcc.Dropdown(
        id = 'date-filter',
        options = [{'label': 'All', 'value': 'All'}] +
        [{'label': name, 'value': name} for name in df['asset_name'].unique()],
        value= 'All'
        ),

    dcc.Graph(
        id = 'line-chart'
        ),
        
])


@app.callback(
    Output('line-chart', 'figure'),
    Input('date-filter', 'value')
)


def update_charts(selected_asset):
    if selected_asset == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['asset_name'] == selected_asset]

    fig = px.line(
        filtered_df,
        x= 'date',
        y='indexed_price',
        color='asset_name',
        title = 'Indexed Stock Price Over Time'
        )
    return fig

app.run(debug = True)


