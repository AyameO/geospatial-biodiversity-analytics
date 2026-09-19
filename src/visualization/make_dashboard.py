import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------------------------------
# 1. ページ構成とダークテーマ用のカスタムCSS
# ------------------------------------------------------------
st.set_page_config(
    page_title="Global 30 by 30 Progress",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 各要素を1つの美しいカードにまとめるためのCSS
st.markdown("""
    <style>
    .stApp {
        background-color: #060b19;
        color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-top: 0px !important;
    }
    .stMarkdown p {
        color: #a0aec0;
    }
    /* st.container(border=True) の枠線と背景色を1つのカードとして統合 */
    div[data-testid="stContainer"] {
        background-color: #0b132b !important;
        border-radius: 12px !important;
        padding: 24px !important;
        border: 1px solid #1c2a4f !important;
        margin-bottom: 16px !important;
    }
    /* 注意書き用のカスタムスタイル */
    .custom-caption {
        color: #a0aec0;
        font-size: 0.85rem;
        margin-top: 12px;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 2. データの読み込みと前処理
# ------------------------------------------------------------
gis_path = "data/dashboard/visualization_results.csv"
reported_path = "data/dashboard/reported_area_results.csv"

@st.cache_data
def load_and_process_data():
    try:
        # 実ファイルを読み込み
        gis_df = pd.read_csv(gis_path)
        reported_df = pd.read_csv(reported_path)
        
        # カテゴリ毎のフィルタリング
        pa_oecm = gis_df[gis_df["category"] == "pa_oecm"].set_index("realm")
        pa_only = gis_df[gis_df["category"] == "pa_only"].set_index("realm")
        oecm_only = gis_df[gis_df["category"] == "oecm_only"].set_index("realm")
        
        # 報告面積データのパース
        rep_map = reported_df.set_index("metric")["area_km2"].to_dict()
    except FileNotFoundError:
        # 万が一ファイルが見つからない場合の、プレースホルダー用ダミーデータ
        pa_oecm = pd.DataFrame({
            'coverage_pct': [8.26, 16.15],
            'gis_area_km2':,
            'denominator_km2': [363100000, 134540000]
        }, index=['marine', 'terrestrial'])
        
        pa_only = pd.DataFrame({'gis_area_km2': [29675211, 20367872]}, index=['marine', 'terrestrial'])
        oecm_only = pd.DataFrame({'gis_area_km2': [325977, 1517809]}, index=['marine', 'terrestrial'])
        rep_map = {'reported_terrestrial_area': 44263950, 'reported_marine_area': 29403000}
        
    return pa_oecm, pa_only, oecm_only, rep_map

# データの確定
pa_oecm, pa_only, oecm_only, rep_map = load_and_process_data()

# 配色の定義
COLOR_MARINE = '#00a8ff'          # 海洋（鮮やかなブルー）
COLOR_TERRESTRIAL = '#2ecc71'      # 陸地（鮮やかなグリーン）
COLOR_MARINE_DARK = '#006699'     # 海洋・Reported用（少し暗めの水色）
COLOR_TERRESTRIAL_DARK = '#1e7e34' # 陸地・Reported用（少し暗めの緑）
COLOR_CARD_BG = '#0b132b'          # グラフの背景

# ------------------------------------------------------------
# 3. タイトル・ヘッダー
# ------------------------------------------------------------
col_head_left, col_head_right = st.columns([7, 3])
with col_head_left:
    st.caption("Geospatial Biodiversity Analytics")
    st.markdown("<h1 style='font-size: 2.5rem; margin-top: -10px;'>Global 30 by 30 Progress</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1rem; color: #a0aec0;'>Protected Areas & Other Effective Area-based Conservation Measures (OECM)</p>", unsafe_allow_html=True)

with col_head_right:
    st.markdown("<p style='text-align: right; font-size: 0.85rem; color: #718096; margin-top: 20px;'>Using geospatial data to support<br>evidence-based conservation and<br>a nature-positive future.</p>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #1c2a4f; margin-bottom: 25px;'>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 4. 上段エリア (2カラムレイアウト)
# ------------------------------------------------------------
top_col1, top_col2 = st.columns(2)

# --- 左上: GIS-calculated Achievement Rate ---
with top_col1:
    with st.container(border=True):
        st.markdown("### 🎯 GIS-calculated Achievement Rate")
        st.caption("(Protected Area + OECM)")
        
        realms_order = ['marine', 'terrestrial']
        labels_order = ['Marine & coastal', 'Terrestrial & inland waters']
        colors_order = [COLOR_MARINE, COLOR_TERRESTRIAL]
        
        fig_achieve = go.Figure()
        
        for r_key, label, color in zip(realms_order, labels_order, colors_order):
            row = pa_oecm.loc[r_key]
            fig_achieve.add_trace(go.Bar(
                x=[label],
                y=[row['coverage_pct']],
                text=[f"<b>{row['coverage_pct']}%</b><br><br>{int(row['gis_area_km2']):,} km²<br><span style='font-size:10px; color:#a0aec0;'>(of {int(row['denominator_km2']):,} km²)</span>"],
                textposition='inside',
                marker_color=color,
                textfont=dict(size=14, color='white'),
                showlegend=False
            ))
        
        # ターゲットライン (30%)
        fig_achieve.add_shape(
            type="line", x0=-0.5, x1=1.5, y0=30, y1=30,
            line=dict(color="#e74c3c", width=2, dash="dash")
        )
        fig_achieve.add_annotation(
            x=1.3, y=33, text="Target (30%)", showarrow=False,
            font=dict(color="#e74c3c", size=12, family="sans-serif")
        )
        
        fig_achieve.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=COLOR_CARD_BG,
            yaxis=dict(title="Coverage Rate", range=[0, 35], gridcolor='#1c2a4f', ticksuffix="%"),
            xaxis=dict(gridcolor='rgba(0,0,0,0)', tickfont=dict(size=13)),
            margin=dict(l=40, r=40, t=30, b=20), height=380
        )
        st.plotly_chart(fig_achieve, use_container_width=True)
        
        # 注意書き（左上メッセージ）
        st.markdown('<p class="custom-caption">⚠️ <b>Note:</b> GIS-calculated figures include only validated polygons and multipolygons in the calculations.</p>', unsafe_allow_html=True)

# --- 右上: GIS-calculated Area ---
with top_col2:
    with st.container(border=True):
        st.markdown("### 🗺️ GIS-calculated Area")
        st.caption("(Protected Area + OECM)")
        
        vals = [pa_oecm.loc['marine', 'gis_area_km2'], pa_oecm.loc['terrestrial', 'gis_area_km2']]
        total_gis_area = sum(vals)
        
        fig_area_pie = go.Figure(data=[go.Pie(
            labels=labels_order,
            values=vals,
            hole=0.4,
            marker=dict(colors=[COLOR_MARINE, COLOR_TERRESTRIAL]),
            textinfo='label+percent',
            texttemplate="<b>%{label}</b><br>%{value:,} km²<br>(%{percent})",
            textfont=dict(size=12, color="white"),
            direction='clockwise',
            sort=False
        )])
        
        fig_area_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
            margin=dict(l=30, r=30, t=20, b=20), height=380
        )
        st.plotly_chart(fig_area_pie, use_container_width=True)
        
        st.markdown(f"<div style='text-align: center; margin-top: -10px;'><span style='color: #a0aec0;'>Total (PA + OECM)</span><br><b style='font-size: 1.8rem; color: #ffffff;'>{int(total_gis_area):,} km²</b></div>", unsafe_allow_html=True)
# ------------------------------------------------------------
# 5. 下段エリア (3カラムレイアウト)
# ------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
btm_col1, btm_col2, btm_col3 = st.columns([2, 1.5, 1.5])

# --- 左下: Reported Area vs GIS-calculated Area ---
with btm_col1:
    with st.container(border=True):
        st.markdown("### 📋 Reported Area vs GIS-calculated Area")
        st.caption("(Protected Area + OECM)")
        
        rep_terr_pct = (rep_map['reported_terrestrial_area'] / pa_oecm.loc['terrestrial', 'denominator_km2']) * 100
        rep_marine_pct = (rep_map['reported_marine_area'] / pa_oecm.loc['marine', 'denominator_km2']) * 100
        
        compare_labels = [
            'Terrestrial<br>(Reported area)', 
            'Terrestrial<br>(GIS-calculated)', 
            'Marine<br>(Reported area)', 
            'Marine<br>(GIS-calculated)'
        ]
        compare_values = [
            rep_terr_pct, 
            pa_oecm.loc['terrestrial', 'coverage_pct'], 
            rep_marine_pct, 
            pa_oecm.loc['marine', 'coverage_pct']
        ]
        
        # Reportedエリアのバーを少し暗めのトーンに変更
        compare_colors = [COLOR_TERRESTRIAL_DARK, COLOR_TERRESTRIAL, COLOR_MARINE_DARK, COLOR_MARINE]
        
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(
            x=compare_labels,
            y=compare_values,
            text=[f"<b>{v:.2f}%</b>" for v in compare_values],
            textposition='outside',
            marker_color=compare_colors,
            textfont=dict(color='white', size=11)
        ))
        
        fig_compare.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=COLOR_CARD_BG,
            yaxis=dict(gridcolor='#1c2a4f', ticksuffix="%", range=[0, max(compare_values) * 1.15]),
            xaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=30, r=30, t=30, b=20), height=300
        )
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # 注意書き（左下メッセージ）
        st.markdown('<p class="custom-caption">⚠️ <b>Note:</b> Reported Area does not account for overlaps between protected areas. Additionally, it includes Antarctica and areas outside the Exclusive Economic Zone (EEZ), which are not considered under the 30by30 target.</p>', unsafe_allow_html=True)

# --- 中下: PA Area by Realm ---
with btm_col2:
    with st.container(border=True):
        st.markdown("### 🛡️ PA Area by Realm")
        st.caption("(Protected Area only)")
        
        pa_vals = [pa_only.loc['marine', 'gis_area_km2'], pa_only.loc['terrestrial', 'gis_area_km2']]
        total_pa_area = sum(pa_vals)
        
        fig_pa = go.Figure(data=[go.Pie(
            labels=labels_order,
            values=pa_vals,
            marker=dict(colors=[COLOR_MARINE, COLOR_TERRESTRIAL]),
            textinfo='percent',
            textfont=dict(size=12, color="white"),
            sort=False
        )])
        
        fig_pa.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=20, b=20), height=250
        )
        st.plotly_chart(fig_pa, use_container_width=True)
        
        st.markdown(f"<div style='text-align: center; margin-top: 10px;'><span style='color: #a0aec0;'>Total PA Only</span><br><b style='font-size: 1.4rem; color: #ffffff;'>{int(total_pa_area):,} km²</b></div>", unsafe_allow_html=True)

# --- 右下: OECM Area by Realm ---
with btm_col3:
    with st.container(border=True):
        st.markdown("### 🌿 OECM Area by Realm")
        st.caption("(OECM only)")
        
        oecm_vals = [oecm_only.loc['marine', 'gis_area_km2'], oecm_only.loc['terrestrial', 'gis_area_km2']]
        total_oecm_area = sum(oecm_vals)
        
        fig_oecm = go.Figure(data=[go.Pie(
            labels=labels_order,
            values=oecm_vals,
            marker=dict(colors=[COLOR_MARINE, COLOR_TERRESTRIAL]),
            textinfo='percent',
            textfont=dict(size=12, color="white"),
            sort=False
        )])
        
        fig_oecm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=20, b=20), height=250
        )
        st.plotly_chart(fig_oecm, use_container_width=True)
        
        st.markdown(f"<div style='text-align: center; margin-top: 10px;'><span style='color: #a0aec0;'>Total OECM Only</span><br><b style='font-size: 1.4rem; color: #ffffff;'>{int(total_oecm_area):,} km²</b></div>", unsafe_allow_html=True)
