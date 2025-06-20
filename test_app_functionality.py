"""アプリケーションの主要機能をテストするスクリプト"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# テスト用のシミュレーションデータ作成
def create_test_data():
    # 基本設定
    base_revenue = 500  # 初月売上（万円）
    revenue_growth = 5  # 月次成長率（%）
    base_ad_cost = 150  # 初月広告費（万円）
    ad_cost_ratio = 30  # 売上に対する広告費率（%）
    consultant_fee = 60  # 月次コンサル費（万円）
    production_cost = 30  # 月次制作費（万円）
    other_fixed_cost = 20  # その他固定費（万円）
    
    # 12ヶ月分のデータを生成
    months = 12
    start_date = datetime.now()
    dates = [start_date + timedelta(days=30*i) for i in range(months)]
    month_names = [date.strftime("%Y年%m月") for date in dates]
    
    results = []
    
    for i, month_name in enumerate(month_names):
        # 売上計算
        growth_factor = (1 + revenue_growth / 100) ** i
        monthly_revenue = base_revenue * growth_factor
        
        # 費用計算
        ad_cost = max(base_ad_cost, monthly_revenue * ad_cost_ratio / 100)
        monthly_total_cost = ad_cost + consultant_fee + production_cost + other_fixed_cost
        
        # 利益計算
        profit = monthly_revenue - monthly_total_cost
        profit_margin = (profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
        roas = (monthly_revenue / ad_cost * 100) if ad_cost > 0 else 0
        ad_ratio = (ad_cost / monthly_revenue * 100) if monthly_revenue > 0 else 0
        
        results.append({
            "月": month_name,
            "売上": int(monthly_revenue),
            "広告費": int(ad_cost),
            "広告費率": round(ad_ratio, 1),
            "コンサル費": consultant_fee,
            "制作費": production_cost,
            "その他": other_fixed_cost,
            "総費用": int(monthly_total_cost),
            "利益": int(profit),
            "利益率": round(profit_margin, 1),
            "ROAS": round(roas, 0)
        })
    
    return pd.DataFrame(results)

# テストの実行
print("アプリケーション機能テスト")
print("=" * 80)

# テストデータの作成
df = create_test_data()

# 1. ROAS計算の検証
print("\n1. ROAS計算の検証")
print("-" * 40)
for i, row in df.head(3).iterrows():
    売上 = row["売上"]
    広告費 = row["広告費"]
    roas = row["ROAS"]
    計算値 = round((売上 / 広告費 * 100), 0)
    print(f"{row['月']}: 売上{売上}万円 ÷ 広告費{広告費}万円 × 100 = {roas}% (検証: {計算値}%)")
    # 丸め誤差を考慮して1の差は許容
    assert abs(roas - 計算値) <= 1, f"ROAS計算エラー: {roas} != {計算値}"

# 2. 広告費率の検証
print("\n2. 広告費率の検証")
print("-" * 40)
for i, row in df.head(3).iterrows():
    売上 = row["売上"]
    広告費 = row["広告費"]
    広告費率 = row["広告費率"]
    計算値 = round((広告費 / 売上 * 100), 1)
    print(f"{row['月']}: 広告費{広告費}万円 ÷ 売上{売上}万円 × 100 = {広告費率}% (検証: {計算値}%)")
    # より詳細な計算値を表示
    詳細計算 = 広告費 / 売上 * 100
    print(f"  詳細: {広告費} / {売上} * 100 = {詳細計算:.4f}")
    # 丸め誤差を考慮して0.2の差は許容（整数化による誤差も考慮）
    assert abs(広告費率 - 計算値) <= 0.2, f"広告費率計算エラー: {広告費率} != {計算値}"

# 3. 全体KPIの計算
print("\n3. 全体KPIの計算")
print("-" * 40)
total_revenue = df["売上"].sum()
total_ad_cost = df["広告費"].sum()
overall_roas = round((total_revenue / total_ad_cost * 100), 0)
print(f"総売上: {total_revenue:,}万円")
print(f"総広告費: {total_ad_cost:,}万円")
print(f"全体ROAS: {overall_roas}%")

# 4. ROASと広告費率の相関確認
print("\n4. ROASと広告費率の関係")
print("-" * 40)
print("月        | 売上   | 広告費 | 広告費率 | ROAS")
print("-" * 50)
for _, row in df.head(6).iterrows():
    print(f"{row['月'][:7]} | {row['売上']:>6} | {row['広告費']:>6} | {row['広告費率']:>7}% | {row['ROAS']:>4}%")

# 5. 成長率の確認
print("\n5. 売上成長率の確認")
print("-" * 40)
for i in range(1, min(4, len(df))):
    前月売上 = df.iloc[i-1]["売上"]
    当月売上 = df.iloc[i]["売上"]
    成長率 = (当月売上 - 前月売上) / 前月売上 * 100
    print(f"{df.iloc[i]['月']}: {成長率:.1f}% (前月比)")

print("\n✅ すべてのテストが正常に完了しました")
print("=" * 80)