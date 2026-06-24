import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

if __name__ == '__main__':
    merged_sales = pd.read_pickle('./data/merged_sales.pkl')
    merged_sales['판매금액'] = (
            merged_sales['수량'] *
            (merged_sales['단가'] * (1 - merged_sales['할인율']))
    )
    merged_sales['순이익'] = (
            merged_sales['수량'] *
            (
                    merged_sales['단가'] * (1 - merged_sales['할인율'])
                    - merged_sales['원가']
            )
    )
    result = pd.pivot_table(
        merged_sales,
        index=['분류명'],
        columns=['년도'],
        values='순이익',
        aggfunc=sum,
        fill_value=0
    )
    print(result)

    exit()
    result = merged_sales.groupby(
        ["분류명", "제품분류명", "제품명"]
    ).agg(
        총매출액=("판매금액", "sum"),
        총순이익=("순이익", "sum"),
        총수량=("수량", "sum")
    ).reset_index().round(2)
    # TOP 10
    top10 = result.sort_values(
        "총매출액",
        ascending=False
    ).head(10)
    plt.figure(figsize=(12, 6))
    plt.barh(
        top10["제품명"],
        top10["총매출액"]
    )
    # 1위가 위로
    plt.gca().invert_yaxis()
    plt.title("제품별 총매출액 TOP 10")
    plt.xlabel("총매출액")
    plt.ylabel("제품명")
    plt.tight_layout()
    plt.show()
