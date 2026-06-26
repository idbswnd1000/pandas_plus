import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, dash_table

engine = create_engine('postgresql://admin:1234@localhost:5432/testdb')

sql = '''
SELECT * FROM vw_sales;
'''

sales = pd.read_sql(sql, engine)

sales['date'] = pd.to_datetime(sales['date'])
sales['year'] = sales['date'].dt.year
sales['quarter'] = sales['date'].dt.quarter
sales['month'] = sales['date'].dt.strftime('%b')

pivot_sales = pd.pivot_table(
    sales,
    index='product_name',
    columns=['year', 'quarter', 'month'],
    values='sales_amount',
    aggfunc='sum',
    fill_value=0
)

pivot_sales = pivot_sales.reset_index()

pivot_sales.columns = [
    ('', '', '') if col == 'product_name'
    else col
    for col in pivot_sales.columns
]

columns = []

for col in pivot_sales.columns:
    if col == ('', '', ''):
        columns.append({
            'name': ['', '', ''],
            'id': 'product_name'
        })
    else:
        year, quarter, month = col
        columns.append({
            'name': [str(year), f'{quarter}분기', str(month)],
            'id': f'{year}_Q{quarter}_{month}'
        })

pivot_sales.columns = [
    'product_name' if col == ('', '', '')
    else f'{col[0]}_Q{col[1]}_{col[2]}'
    for col in pivot_sales.columns
]

app = Dash(__name__)

app.layout = dash_table.DataTable(
    data=pivot_sales.to_dict('records'),
    columns=columns,
    merge_duplicate_headers=True,
    page_action='none',
    style_table={
        'overflowX': 'auto'
    },
    style_cell={
        'textAlign': 'center',
        'minWidth': '100px',
        'width': '100px',
        'maxWidth': '150px'
    }
)

if __name__ == '__main__':
    app.run(debug=True)