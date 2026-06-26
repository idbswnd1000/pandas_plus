import dash
import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, html, dash_table, dcc, Input, Output
import dash_ag_grid as dag
import plotly.express as px
engine = create_engine('postgresql://admin:1234@localhost:5432/testdb')

sql = '''
SELECT * FROM vw_sales;
'''

sales = pd.read_sql(sql, engine)

sales['date'] = pd.to_datetime(sales['date'])
sales['year'] = sales['date'].dt.year.astype(str)
sales['quarter'] = sales['date'].dt.quarter.astype(str)
sales['month'] = sales['date'].dt.strftime('%b')

region_options = [
    {"label": region, "value": region} for region in sales['province'].unique()
]

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2('지역별 제품 매출 그래프'),
    dcc.Dropdown(
        id='region_dropdown',
        options=region_options,
        value=region_options[0]['value'],
        clearable=False,
    ),
    dcc.Graph(id='region_graph'),
])

@app.callback(
    Output('region_graph', 'figure'),
    Input('region_dropdown', 'value')
)

def region_graph(province_value):
    filtered_sales = sales[sales['province'] == province_value]
    grouped_sales = (filtered_sales.groupby('product_name')['net_profit']
                     .sum().reset_index()
                     .sort_values('net_profit', ascending=True)
                     .head(10))
    fig = px.bar(
        grouped_sales,
        x='net_profit',
        y='product_name',
        title=f'{province_value} 지역 제품별 매출',
        labels={
            'product_name': "제품명",
            "net_profit" : '총순이익'
        }
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)