import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Streamlit設定
st.set_page_config(
    page_title="コンサル向けシミュレーションツール",
    page_icon="📊",
    layout="wide"
)

# セッション状態の初期化
if 'monthly_costs' not in st.session_state:
    st.session_state.monthly_costs = {}
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False
if 'selected_preset' not in st.session_state:
    st.session_state.selected_preset = "デフォルト"

st.title("📊 コンサル向けシミュレーション作成ツール")
st.markdown("---")

# サイドバーで基本設定
st.sidebar.header("基本設定")
simulation_period = st.sidebar.selectbox("シミュレーション期間", ["12ヶ月", "24ヶ月", "36ヶ月"])
start_date = st.sidebar.date_input("開始日", datetime.now())

# 期間の設定
months = int(simulation_period.split("ヶ月")[0])
dates = [start_date + timedelta(days=30*i) for i in range(months)]
month_names = [date.strftime("%Y年%m月") for date in dates]

# 業界・イベント別プリセット定義
PRESETS = {
    "デフォルト": {
        "description": "標準的な設定",
        "consultant_multipliers": [1.0] * 12,
        "production_multipliers": [1.0] * 12,
        "ad_multipliers": [1.0] * 12
    },
    "EC・小売業": {
        "description": "EC・小売業向け（年末商戦、夏物・冬物シーズン対応）",
        "consultant_multipliers": [1.2, 1.0, 1.0, 1.1, 1.0, 1.0, 1.1, 1.0, 1.0, 1.1, 1.3, 1.5],
        "production_multipliers": [1.3, 0.8, 0.9, 1.2, 0.9, 1.0, 1.2, 0.9, 1.0, 1.2, 1.4, 1.6],
        "ad_multipliers": [1.4, 0.7, 0.8, 1.3, 0.8, 0.9, 1.3, 0.8, 0.9, 1.3, 1.5, 1.8]
    },
    "旅行・レジャー": {
        "description": "旅行・レジャー業界（GW、夏休み、年末年始ピーク）",
        "consultant_multipliers": [1.3, 1.0, 1.2, 1.4, 1.5, 1.0, 1.6, 1.6, 1.0, 1.0, 1.0, 1.4],
        "production_multipliers": [1.4, 0.9, 1.3, 1.5, 1.6, 0.9, 1.7, 1.7, 0.9, 0.9, 0.9, 1.5],
        "ad_multipliers": [1.5, 0.8, 1.4, 1.6, 1.7, 0.8, 1.8, 1.8, 0.8, 0.8, 0.8, 1.6]
    },
    "BtoB": {
        "description": "BtoB企業（年度末、四半期末強化）",
        "consultant_multipliers": [1.0, 1.0, 1.4, 1.0, 1.0, 1.2, 1.0, 1.0, 1.2, 1.0, 1.0, 1.3],
        "production_multipliers": [1.0, 1.0, 1.5, 1.0, 1.0, 1.3, 1.0, 1.0, 1.3, 1.0, 1.0, 1.4],
        "ad_multipliers": [1.0, 1.0, 1.6, 1.0, 1.0, 1.4, 1.0, 1.0, 1.4, 1.0, 1.0, 1.5]
    },
    "スタートアップ": {
        "description": "スタートアップ企業（資金調達時期考慮）",
        "consultant_multipliers": [1.5, 1.0, 1.0, 1.2, 1.0, 1.0, 1.0, 1.0, 1.3, 1.0, 1.0, 1.0],
        "production_multipliers": [1.6, 1.0, 1.0, 1.3, 1.0, 1.0, 1.0, 1.0, 1.4, 1.0, 1.0, 1.0],
        "ad_multipliers": [1.7, 1.0, 1.0, 1.4, 1.0, 1.0, 1.0, 1.0, 1.5, 1.0, 1.0, 1.0]
    }
}

def apply_preset_costs(preset_name, consultant_base, production_base, ad_base):
    if preset_name not in PRESETS:
        return
    
    preset = PRESETS[preset_name]
    for i in range(min(months, 12)):
        month_index = (start_date.month + i - 1) % 12
        
        consultant_cost = int(consultant_base * preset["consultant_multipliers"][month_index])
        production_cost_calc = int(production_base * preset["production_multipliers"][month_index])
        
        st.session_state.monthly_costs[f"consultant_{i}"] = consultant_cost
        st.session_state.monthly_costs[f"production_{i}"] = production_cost_calc

def calculate_optimization_suggestions(df):
    suggestions = []
    
    # ROASが低い月の特定
    low_roas_months = df[df["ROAS"] < df["ROAS"].mean() - df["ROAS"].std()]
    if not low_roas_months.empty:
        suggestions.append({
            "type": "警告",
            "title": "ROAS改善が必要な月があります",
            "detail": f"{', '.join(low_roas_months['月'].tolist())}のROASが平均を大きく下回っています。広告費の見直しを検討してください。",
            "impact": "高"
        })
    
    # 利益率の変動が大きい場合
    profit_margin_std = df["利益率"].std()
    if profit_margin_std > 10:
        suggestions.append({
            "type": "注意",
            "title": "利益率の変動が大きいです",
            "detail": f"利益率の標準偏差が{profit_margin_std:.1f}%です。費用配分の最適化により安定化が可能です。",
            "impact": "中"
        })
    
    # 総費用が売上を上回る月
    loss_months = df[df["利益"] < 0]
    if not loss_months.empty:
        suggestions.append({
            "type": "警告",
            "title": "赤字月があります",
            "detail": f"{', '.join(loss_months['月'].tolist())}で赤字になっています。緊急の費用見直しが必要です。",
            "impact": "高"
        })
    
    # 広告費効率の最適化提案
    high_ad_months = df[df["広告費"] > df["売上"] * 0.4]
    if not high_ad_months.empty:
        suggestions.append({
            "type": "提案",
            "title": "広告費最適化の機会",
            "detail": f"{', '.join(high_ad_months['月'].tolist())}の広告費率が40%を超えています。効率化により利益改善が見込めます。",
            "impact": "中"
        })
    
    return suggestions

# メインコンテンツ
tab1, tab2, tab3, tab4 = st.tabs(["📈 基本設定", "📅 月別費用設定", "📊 結果表示", "📁 エクスポート"])

with tab1:
    st.header("シミュレーション設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("売上設定")
        base_revenue = st.number_input("初月売上（万円）", value=500, step=50)
        revenue_growth = st.slider("月次成長率（%）", -10.0, 50.0, 5.0, 0.1)
        revenue_seasonal = st.checkbox("季節変動を考慮")
        
        if revenue_seasonal:
            peak_months = st.multiselect("ピーク月", 
                                       ["1月", "2月", "3月", "4月", "5月", "6月", 
                                        "7月", "8月", "9月", "10月", "11月", "12月"],
                                       default=["12月"])
            peak_multiplier = st.slider("ピーク月倍率", 1.0, 3.0, 1.5, 0.1)
    
    with col2:
        st.subheader("費用設定")
        
        # 広告費
        base_ad_cost = st.number_input("初月広告費（万円）", value=150, step=10)
        ad_cost_ratio = st.slider("売上に対する広告費率（%）", 0.0, 50.0, 30.0, 1.0)
        
        # 固定費
        consultant_fee = st.number_input("月次コンサル費（万円）", value=60, step=10)
        production_cost = st.number_input("月次制作費（万円）", value=30, step=5)
        other_fixed_cost = st.number_input("その他固定費（万円）", value=20, step=5)
    
    # 自動スケジューリング機能
    st.subheader("🤖 自動スケジューリング")
    enable_auto_schedule = st.toggle("自動スケジューリングを有効化")
    
    if enable_auto_schedule:
        col1, col2 = st.columns(2)
        
        with col1:
            target_budget = st.number_input("目標予算（万円/月）", value=200, step=10)
            priority_mode = st.selectbox(
                "優先モード",
                ["利益最大化", "売上成長重視", "リスク最小化"],
                help="どの指標を最優先するかを選択"
            )
        
        with col2:
            if st.button("🎯 最適スケジュール生成", type="primary"):
                # 簡単な最適化ロジック
                for i in range(months):
                    if priority_mode == "利益最大化":
                        # 利益を最大化する配分
                        consultant_opt = min(target_budget * 0.4, consultant_fee * 1.2)
                        production_opt = min(target_budget * 0.2, production_cost * 1.1)
                    elif priority_mode == "売上成長重視":
                        # 売上成長を重視する配分
                        consultant_opt = min(target_budget * 0.5, consultant_fee * 1.5)
                        production_opt = min(target_budget * 0.3, production_cost * 1.3)
                    else:  # リスク最小化
                        # リスクを最小化する安定配分
                        consultant_opt = target_budget * 0.3
                        production_opt = target_budget * 0.15
                    
                    st.session_state.monthly_costs[f"consultant_{i}"] = int(consultant_opt)
                    st.session_state.monthly_costs[f"production_{i}"] = int(production_opt)
                
                st.success("✅ 最適なスケジュールを生成しました！")
                st.rerun()

# シミュレーション計算
def calculate_simulation():
    results = []
    
    for i, month_name in enumerate(month_names):
        # 売上計算
        growth_factor = (1 + revenue_growth / 100) ** i
        monthly_revenue = base_revenue * growth_factor
        
        # 季節変動
        if revenue_seasonal:
            month_num = (start_date.month + i - 1) % 12 + 1
            month_str = f"{month_num}月"
            if month_str in peak_months:
                monthly_revenue *= peak_multiplier
        
        # 月別費用の取得（自動調整モード対応）
        if st.session_state.auto_mode:
            # 売上に応じた自動調整
            revenue_ratio = monthly_revenue / base_revenue if base_revenue > 0 else 1
            dynamic_multiplier = 0.8 + (revenue_ratio * 0.4)  # 0.8-1.2の範囲で調整
            
            monthly_consultant = st.session_state.monthly_costs.get(f"consultant_{i}", consultant_fee) * dynamic_multiplier
            monthly_production = st.session_state.monthly_costs.get(f"production_{i}", production_cost) * dynamic_multiplier
        else:
            monthly_consultant = st.session_state.monthly_costs.get(f"consultant_{i}", consultant_fee)
            monthly_production = st.session_state.monthly_costs.get(f"production_{i}", production_cost)
        
        # 費用計算
        ad_cost = max(base_ad_cost, monthly_revenue * ad_cost_ratio / 100)
        monthly_total_cost = ad_cost + monthly_consultant + monthly_production + other_fixed_cost
        
        # 利益計算
        profit = monthly_revenue - monthly_total_cost
        profit_margin = (profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
        roas = (monthly_revenue / ad_cost * 100) if ad_cost > 0 else 0
        
        results.append({
            "月": month_name,
            "売上": int(monthly_revenue),
            "広告費": int(ad_cost),
            "広告費率": round(ad_cost / monthly_revenue * 100, 1) if monthly_revenue > 0 else 0,
            "コンサル費": int(monthly_consultant),
            "制作費": int(monthly_production),
            "その他": other_fixed_cost,
            "総費用": int(monthly_total_cost),
            "利益": int(profit),
            "利益率": round(profit_margin, 1),
            "ROAS": round(roas, 0)
        })
    
    return pd.DataFrame(results)

# 結果計算
df = calculate_simulation()

with tab2:
    st.header("月別費用設定")
    
    # 自動設定プリセット
    st.subheader("🚀 スマート設定（業界別プリセット）")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_preset = st.selectbox(
            "業界・ビジネスタイプを選択",
            options=list(PRESETS.keys()),
            index=list(PRESETS.keys()).index(st.session_state.selected_preset),
            help="業界に最適化された季節変動パターンが自動適用されます"
        )
        st.caption(PRESETS[selected_preset]["description"])
    
    with col2:
        if st.button("🎯 プリセット適用", type="primary"):
            apply_preset_costs(selected_preset, consultant_fee, production_cost, base_ad_cost)
            st.session_state.selected_preset = selected_preset
            st.success(f"✅ {selected_preset}のプリセットを適用しました")
            st.rerun()
    
    with col3:
        auto_mode = st.toggle("自動調整モード", value=st.session_state.auto_mode)
        st.session_state.auto_mode = auto_mode
        if auto_mode:
            st.caption("📈 売上に連動して費用が自動調整されます")
    
    st.markdown("---")
    st.info("💡 各月ごとに個別に費用を設定できます。設定しない月はデフォルト値が使用されます")
    
    # 月別費用設定
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("コンサル費用")
        for i, month_name in enumerate(month_names):
            key = f"consultant_{i}"
            default_value = st.session_state.monthly_costs.get(key, consultant_fee)
            value = st.number_input(
                f"{month_name} コンサル費（万円）", 
                value=int(default_value), 
                step=10, 
                key=key
            )
            st.session_state.monthly_costs[key] = value
    
    with col2:
        st.subheader("制作費用")
        for i, month_name in enumerate(month_names):
            key = f"production_{i}"
            default_value = st.session_state.monthly_costs.get(key, production_cost)
            value = st.number_input(
                f"{month_name} 制作費（万円）", 
                value=int(default_value), 
                step=5, 
                key=key
            )
            st.session_state.monthly_costs[key] = value
    
    # プリセット可視化
    if selected_preset != "デフォルト":
        st.subheader("📊 選択中のプリセット変動パターン")
        preset_data = PRESETS[selected_preset]
        
        pattern_df = pd.DataFrame({
            "月": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
            "コンサル費倍率": preset_data["consultant_multipliers"],
            "制作費倍率": preset_data["production_multipliers"],
            "広告費倍率": preset_data["ad_multipliers"]
        })
        
        fig_pattern = px.line(pattern_df, x="月", y=["コンサル費倍率", "制作費倍率", "広告費倍率"],
                             title=f"{selected_preset} - 季節変動パターン",
                             labels={"value": "倍率", "variable": "費目"})
        fig_pattern.update_layout(xaxis_tickangle=-45, height=300)
        st.plotly_chart(fig_pattern, use_container_width=True)
    
    # 一括設定ボタン
    st.subheader("一括設定")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("全てをデフォルト値にリセット"):
            for i in range(months):
                st.session_state.monthly_costs[f"consultant_{i}"] = consultant_fee
                st.session_state.monthly_costs[f"production_{i}"] = production_cost
            st.rerun()
    
    with col2:
        bulk_consultant = st.number_input("一括コンサル費設定", value=60, step=10)
        if st.button("全月にコンサル費適用"):
            for i in range(months):
                st.session_state.monthly_costs[f"consultant_{i}"] = bulk_consultant
            st.rerun()
    
    with col3:
        bulk_production = st.number_input("一括制作費設定", value=30, step=5)
        if st.button("全月に制作費適用"):
            for i in range(months):
                st.session_state.monthly_costs[f"production_{i}"] = bulk_production
            st.rerun()

with tab3:
    st.header("シミュレーション結果")
    
    # KPI表示
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = df["売上"].sum()
    total_cost = df["総費用"].sum()
    total_profit = df["利益"].sum()
    total_ad_cost = df["広告費"].sum()
    overall_roas = (total_revenue / total_ad_cost * 100) if total_ad_cost > 0 else 0
    
    with col1:
        st.metric("総売上", f"{total_revenue:,}万円")
    with col2:
        st.metric("総費用", f"{total_cost:,}万円")
    with col3:
        st.metric("総利益", f"{total_profit:,}万円", f"{total_profit/total_revenue*100:.1f}%")
    with col4:
        st.metric("全体ROAS", f"{overall_roas:.0f}%", help="全期間の総売上÷総広告費×100")
    
    # グラフ表示
    col1, col2 = st.columns(2)
    
    with col1:
        fig_revenue = px.line(df, x="月", y=["売上", "総費用", "利益"], 
                             title="売上・費用・利益推移",
                             color_discrete_map={"売上": "blue", "総費用": "red", "利益": "green"})
        fig_revenue.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        fig_roas = px.bar(df, x="月", y="ROAS", title="ROAS推移（売上÷広告費×100）")
        fig_roas.update_layout(xaxis_tickangle=-45)
        fig_roas.add_hline(y=100, line_dash="dash", line_color="red", 
                          annotation_text="損益分岐点(100%)")
        st.plotly_chart(fig_roas, use_container_width=True)
    
    # 追加のグラフ：広告費率とROASの関係
    col3, col4 = st.columns(2)
    
    with col3:
        fig_ad_ratio = px.bar(df, x="月", y="広告費率", title="広告費率推移（広告費÷売上×100）")
        fig_ad_ratio.update_layout(xaxis_tickangle=-45)
        fig_ad_ratio.add_hline(y=ad_cost_ratio, line_dash="dash", line_color="green", 
                              annotation_text=f"目標広告費率({ad_cost_ratio}%)")
        st.plotly_chart(fig_ad_ratio, use_container_width=True)
    
    with col4:
        # 散布図で広告費率とROASの相関を表示
        fig_scatter = px.scatter(df, x="広告費率", y="ROAS", 
                               title="広告費率とROASの相関",
                               text="月", size="売上")
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # AI最適化提案
    st.subheader("🤖 AI最適化提案")
    suggestions = calculate_optimization_suggestions(df)
    
    if suggestions:
        for suggestion in suggestions:
            if suggestion["type"] == "警告":
                st.error(f"⚠️ **{suggestion['title']}** (影響度: {suggestion['impact']})\n\n{suggestion['detail']}")
            elif suggestion["type"] == "注意":
                st.warning(f"⚡ **{suggestion['title']}** (影響度: {suggestion['impact']})\n\n{suggestion['detail']}")
            else:  # 提案
                st.info(f"💡 **{suggestion['title']}** (影響度: {suggestion['impact']})\n\n{suggestion['detail']}")
    else:
        st.success("✅ 現在の設定は良好です。大きな改善点は見つかりませんでした。")
    
    # データテーブル
    st.subheader("詳細データ")
    st.dataframe(df, use_container_width=True)

with tab4:
    st.header("エクスポート")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Excel出力")
        
        def to_excel(simulation_df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                simulation_df.to_excel(writer, sheet_name='シミュレーション結果', index=False)
                
                workbook = writer.book
                worksheet = writer.sheets['シミュレーション結果']
                
                # 列幅調整
                worksheet.set_column('A:A', 12)
                worksheet.set_column('B:J', 10)
                
            return output.getvalue()
        
        excel_data = to_excel(df)
        st.download_button(
            label="📥 Excelファイルをダウンロード",
            data=excel_data,
            file_name=f"simulation_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        st.subheader("CSV出力")
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSVファイルをダウンロード",
            data=csv,
            file_name=f"simulation_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# フッター
st.markdown("---")
st.markdown("💡 **使い方**: 左側で設定を変更し、リアルタイムで結果を確認できます")

if __name__ == "__main__":
    pass