import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, html, dcc
import plotly.express as px

engine = create_engine('postgresql://admin:1234@localhost:5432/testdb')

sales = pd.read_sql("select * from vw_sales;", engine)

sales['date'] = pd.to_datetime(sales['date'])
sales['year'] = sales['date'].dt.year
sales['quarter'] = sales['date'].dt.quarter
sales['month'] = sales['date'].dt.month

heatmap_data = pd.pivot_table(
    sales,
    index='product_name',
    columns=['year', 'quarter', 'month'],
    values='sales_amount',
    aggfunc='sum',
    fill_value=0
)

heatmap_data.columns = [
    f'{year}-Q{quarter}-{month:02d}'
    for year, quarter, month in heatmap_data.columns
]

heatmap_data = heatmap_data.astype(float)

fig = px.imshow(
    heatmap_data,
    aspect="auto",
    title="제품별 연도/분기/월 매출 히트맵"
)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("제품별 매출 히트맵"),
    dcc.Graph(figure=fig, style={'height': '800px'})
])

if __name__ == '__main__':
    app.run(debug=True)