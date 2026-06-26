import dash
import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, dash_table, dcc, Input, Output
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

group_customer_sales = (sales.groupby('customer_name')['sales_amount']
                        .sum()
                        .reset_index()
                        .sort_values('sales_amount', ascending=False)
                        .head(20)
                        )


fig = px.bar(
    group_customer_sales,
    x='sales_amount',
    y='customer_name',

)

app = dash.Dash(__name__)
app.layout = dcc.Graph(
    figure=fig
)

if __name__ == '__main__':
    app.run(debug=True)
