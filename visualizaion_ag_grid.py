import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, html
import dash_ag_grid as dag

engine = create_engine('postgresql://admin:1234@localhost:5432/testdb')

sql = '''
select * from vw_sales;
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
    'product_name' if i == 0
    else f'{col[0]}_Q{col[1]}_{col[2]}'
    for i, col in enumerate(pivot_sales.columns)
]

column_defs = [
    {
        "headerName": "제품명",
        "field": "product_name",
        "pinned": "left",
        "width": 220
    }
]

for year in sorted(sales['year'].unique()):
    year_children = []

    for quarter in sorted(sales[sales['year'] == year]['quarter'].unique()):
        quarter_children = []

        month_order = sales[
            (sales['year'] == year) &
            (sales['quarter'] == quarter)
        ][['month', 'date']].copy()

        month_order['month_num'] = month_order['date'].dt.month

        months = (
            month_order
            .drop_duplicates('month')
            .sort_values('month_num')['month']
            .tolist()
        )

        for month in months:
            field_name = f'{year}_Q{quarter}_{month}'

            if field_name in pivot_sales.columns:
                quarter_children.append({
                    "headerName": month,
                    "field": field_name,
                    "type": "numericColumn",
                    "valueFormatter": {
                        "function": "params.value ? params.value.toLocaleString() : '0'"
                    }
                })

        year_children.append({
            "headerName": f"{quarter}분기",
            "children": quarter_children
        })

    column_defs.append({
        "headerName": str(year),
        "children": year_children
    })

app = Dash(__name__)

app.layout = html.Div([
    html.H1("제품별 연도 / 분기 / 월 매출 피벗 테이블"),

    dag.AgGrid(
        rowData=pivot_sales.to_dict('records'),
        columnDefs=column_defs,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "minWidth": 100
        },
        dashGridOptions={
            "animateRows": True
        },
        style={
            "height": "800px",
            "width": "100%"
        }
    )
])

if __name__ == '__main__':
    app.run(debug=True)