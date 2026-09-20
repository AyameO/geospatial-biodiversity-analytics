import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

# ------------------------------------------------------------
# 1. Page configuration and dark theme
# ------------------------------------------------------------
st.set_page_config(
    page_title="Global 30 by 30 Progress",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #060b19;
        color: #ffffff;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    .stMarkdown p {
        color: #a0aec0;
    }

    /* Card-style containers */
    div[data-testid="stVBlock"] > div {
        background-color: #0b132b;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #1c2a4f;
        margin-bottom: 16px;
    }

    /* Explanatory notes */
    .custom-caption {
        color: #a0aec0;
        font-size: 0.85rem;
        margin-top: 12px;
        line-height: 1.5;
    }

    .custom-caption b {
        color: #dbe4f0;
    }
    </style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# 2. Data loading and preprocessing
# ------------------------------------------------------------
gis_path = "data/dashboard/visualization_results.csv"
reported_path = "data/dashboard/reported_area_results.csv"
metadata_path = "data/dashboard/metadata.json"


def get_wdpca_retrieval_date():
    """Load the WDPCA retrieval date from metadata.json."""

    try:
        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as f:
            metadata = json.load(f)

        retrieval_date = metadata.get(
            "wdpca_retrieval_date"
        )

        if not retrieval_date:
            return None

        return pd.to_datetime(
            retrieval_date
        ).to_pydatetime()

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
        TypeError
    ):
        return None


wdpca_retrieval_date = get_wdpca_retrieval_date()


@st.cache_data
def load_and_process_data():

    # GIS-derived visualization data
    gis_df = pd.read_csv(gis_path)

    # Raw WDPCA reported-area data
    reported_df = pd.read_csv(reported_path)

    # Category filtering
    pa_oecm = (
        gis_df[gis_df["category"] == "pa_oecm"]
        .set_index("realm")
    )

    pa_only = (
        gis_df[gis_df["category"] == "pa_only"]
        .set_index("realm")
    )

    oecm_only = (
        gis_df[gis_df["category"] == "oecm_only"]
        .set_index("realm")
    )

    # Raw reported-area values
    rep_map = (
        reported_df
        .set_index("metric")["area_km2"]
        .to_dict()
    )

    return pa_oecm, pa_only, oecm_only, rep_map


pa_oecm, pa_only, oecm_only, rep_map = load_and_process_data()


# ------------------------------------------------------------
# 3. Color palette
# ------------------------------------------------------------

# GIS-calculated:
# bright colors are used to emphasize the spatial-analysis results.
COLOR_MARINE = "#00a8ff"
COLOR_TERRESTRIAL = "#2ecc71"

# Raw Reported Area:
# darker colors distinguish raw attribute sums from GIS-calculated values.
COLOR_MARINE_RAW = "#315f73"
COLOR_TERRESTRIAL_RAW = "#356044"

# UI colors
COLOR_CARD_BG = "#0b132b"
COLOR_GRID = "#1c2a4f"
COLOR_TEXT_MUTED = "#a0aec0"
COLOR_TARGET = "#e74c3c"


# ------------------------------------------------------------
# 4. Header
# ------------------------------------------------------------
col_head_left, col_head_right = st.columns([7, 3])

with col_head_left:

    st.caption("Geospatial Biodiversity Analytics")

    st.markdown(
        "<h1 style='font-size: 2.5rem; margin-top: -10px;'>"
        "Global 30 by 30 Progress"
        "</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='font-size: 1.1rem; color: #a0aec0;'>"
        "Protected Areas & Other Effective Area-based Conservation Measures "
        "(OECM)"
        "</p>",
        unsafe_allow_html=True
    )

    if wdpca_retrieval_date is not None:
        st.markdown(
            f"<p style='font-size: 0.82rem; color: #cbd5e1; margin-top: -4px;'>"
            f"WDPCA data retrieved: "
            f"<b>{wdpca_retrieval_date.strftime('%B, %Y')}</b>"
            f"</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<p style='font-size: 0.82rem; color: #e74c3c; margin-top: -4px;'>"
            "WDPCA data retrieval date: not detected"
            "</p>",
            unsafe_allow_html=True
        )


with col_head_right:

    st.markdown(
        "<p style='text-align: right; font-size: 0.85rem; "
        "color: #718096; margin-top: 20px;'>"
        "Using geospatial data to support<br>"
        "evidence-based conservation and<br>"
        "a nature-positive future."
        "</p>",
        unsafe_allow_html=True
    )


st.markdown(
    "<hr style='border-color: #1c2a4f; margin-bottom: 25px;'>",
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# 5. Top section
# ------------------------------------------------------------
top_col1, top_col2 = st.columns(2)


# ============================================================
# 5-1. GIS-calculated Achievement Rate
# ============================================================
with top_col1:

    st.markdown("### 🎯 GIS-calculated Achievement Rate")
    st.caption("(Protected Area + OECM)")

    realms_order = ["marine", "terrestrial"]

    labels_order = [
        "Marine & coastal",
        "Terrestrial & inland waters"
    ]

    colors_order = [
        COLOR_MARINE,
        COLOR_TERRESTRIAL
    ]

    fig_achieve = go.Figure()

    for r_key, label, color in zip(
        realms_order,
        labels_order,
        colors_order
    ):

        row = pa_oecm.loc[r_key]

        fig_achieve.add_trace(
            go.Bar(
                x=[label],
                y=[row["coverage_pct"]],

                text=[
                    f"<b>{row['coverage_pct']:.2f}%</b>"
                    f"<br><br>"
                    f"{int(row['gis_area_km2']):,} km²"
                    f"<br>"
                    f"<span style='font-size:10px; "
                    f"color:#a0aec0;'>"
                    f"(of {int(row['denominator_km2']):,} km²)"
                    f"</span>"
                ],

                textposition="inside",

                marker_color=color,

                textfont=dict(
                    size=14,
                    color="white"
                ),

                showlegend=False
            )
        )

    # 30% Target line
    fig_achieve.add_shape(
        type="line",
        x0=-0.5,
        x1=1.5,
        y0=30,
        y1=30,
        line=dict(
            color=COLOR_TARGET,
            width=2,
            dash="dash"
        )
    )

    fig_achieve.add_annotation(
        x=1.3,
        y=33,
        text="Target (30%)",
        showarrow=False,
        font=dict(
            color=COLOR_TARGET,
            size=12,
            family="sans-serif"
        )
    )

    fig_achieve.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=COLOR_CARD_BG,

        yaxis=dict(
            title="Coverage Rate",
            range=[0, 35],
            gridcolor=COLOR_GRID,
            ticksuffix="%"
        ),

        xaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(
                size=13,
                color="#dbe4f0"
            )
        ),

        margin=dict(
            l=40,
            r=40,
            t=30,
            b=20
        ),

        height=380
    )

    st.plotly_chart(
        fig_achieve,
        use_container_width=True
    )

    st.markdown(
        '<p class="custom-caption">'
        'ℹ️ <b>GIS-calculated:</b> Includes only spatially validated '
        'Polygon and MultiPolygon geometries. Overlapping areas are '
        'spatially dissolved before calculating unique area. '
        'Antarctica and areas beyond national EEZs are excluded '
        'from the Target 3 calculation. Areas are calculated using '
        'the equal-area projection EPSG:6933.'
        '</p>',
        unsafe_allow_html=True
    )


# ============================================================
# 5-2. GIS-calculated Area
# ============================================================
with top_col2:

    st.markdown("### 🗺️ GIS-calculated Area")
    st.caption("(Protected Area + OECM)")

    vals = [
        pa_oecm.loc["marine", "gis_area_km2"],
        pa_oecm.loc["terrestrial", "gis_area_km2"]
    ]

    total_gis_area = sum(vals)

    fig_area_pie = go.Figure(
        data=[
            go.Pie(
                labels=labels_order,
                values=vals,
                hole=0.4,

                marker=dict(
                    colors=[
                        COLOR_MARINE,
                        COLOR_TERRESTRIAL
                    ]
                ),

                textinfo="label+percent",

                texttemplate=(
                    "<b>%{label}</b>"
                    "<br>%{value:,} km²"
                    "<br>(%{percent})"
                ),

                textfont=dict(
                    size=12,
                    color="white"
                ),

                direction="clockwise",
                sort=False
            )
        ]
    )

    fig_area_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,

        margin=dict(
            l=30,
            r=30,
            t=20,
            b=20
        ),

        height=380
    )

    st.plotly_chart(
        fig_area_pie,
        use_container_width=True
    )

    st.markdown(
        f"""
        <div style='text-align: center; margin-top: -10px;'>
            <span style='color: #a0aec0;'>Total (PA + OECM)</span>
            <br>
            <b style='font-size: 1.8rem; color: #ffffff;'>
                {int(total_gis_area):,} km²
            </b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# 6. Bottom section
# ------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

btm_col1, btm_col2, btm_col3 = st.columns(
    [2, 1.5, 1.5]
)


# ============================================================
# 6-1. Raw Reported Area vs GIS-calculated Area
# ============================================================
with btm_col1:

    st.markdown(
        "### 📋 Raw Reported Area vs GIS-calculated Area"
    )

    st.caption(
        "(WDPCA attribute sum vs spatially calculated area)"
    )

    # --------------------------------------------------------
    # Raw reported area converted to the same denominator
    # for visual comparison only.
    #
    # IMPORTANT:
    # These are NOT Target 3 achievement rates.
    # --------------------------------------------------------

    rep_terr_pct = (
        rep_map["reported_terrestrial_area"]
        / pa_oecm.loc["terrestrial", "denominator_km2"]
    ) * 100

    rep_marine_pct = (
        rep_map["reported_marine_area"]
        / pa_oecm.loc["marine", "denominator_km2"]
    ) * 100

    compare_labels = [
        "Terrestrial<br>(Raw reported)",
        "Terrestrial<br>(GIS-calculated)",
        "Marine<br>(Raw reported)",
        "Marine<br>(GIS-calculated)"
    ]

    compare_values = [
        rep_terr_pct,
        pa_oecm.loc["terrestrial", "coverage_pct"],
        rep_marine_pct,
        pa_oecm.loc["marine", "coverage_pct"]
    ]

    compare_colors = [
        COLOR_TERRESTRIAL_RAW,
        COLOR_TERRESTRIAL,
        COLOR_MARINE_RAW,
        COLOR_MARINE
    ]

    fig_compare = go.Figure()

    fig_compare.add_trace(
        go.Bar(
            x=compare_labels,
            y=compare_values,

            text=[
                f"<b>{v:.2f}%</b>"
                for v in compare_values
            ],

            textposition="outside",

            marker_color=compare_colors,

            textfont=dict(
                color="white",
                size=11
            )
        )
    )

    fig_compare.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=COLOR_CARD_BG,

        yaxis=dict(
            title="Share of Target 3 denominator",
            gridcolor=COLOR_GRID,
            ticksuffix="%",
            range=[
                0,
                max(compare_values) * 1.15
            ]
        ),

        xaxis=dict(
            tickfont=dict(
                size=10,
                color="#dbe4f0"
            )
        ),

        margin=dict(
            l=45,
            r=30,
            t=30,
            b=20
        ),

        height=300
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

    st.markdown(
        '<p class="custom-caption">'
        '⚠️ <b>Raw Reported Area:</b> Simple sum of area attributes '
        'reported in the WDPCA records. Spatial overlaps between '
        'protected areas are not removed, and the sum may include '
        'Antarctica and areas outside national EEZs. Therefore, '
        'it is not suitable for measuring progress toward the '
        '30 by 30 target.'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="custom-caption">'
        'ℹ️ <b>Interpretation:</b> Raw reported values are shown '
        'for methodological comparison only. The percentages above '
        'are not Target 3 achievement rates.'
        '</p>',
        unsafe_allow_html=True
    )


# ============================================================
# 6-2. PA Area by Realm
# ============================================================
with btm_col2:

    st.markdown("### 🛡️ PA Area by Realm")
    st.caption("(Protected Area only)")

    pa_vals = [
        pa_only.loc["marine", "gis_area_km2"],
        pa_only.loc["terrestrial", "gis_area_km2"]
    ]

    total_pa_area = sum(pa_vals)

    fig_pa = go.Figure(
        data=[
            go.Pie(
                labels=labels_order,
                values=pa_vals,

                marker=dict(
                    colors=[
                        COLOR_MARINE,
                        COLOR_TERRESTRIAL
                    ]
                ),

                textinfo="percent",

                textfont=dict(
                    size=12,
                    color="white"
                ),

                sort=False
            )
        ]
    )

    fig_pa.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#dbe4f0",
                size=11
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=55
        ),

        height=250
    )

    st.plotly_chart(
        fig_pa,
        use_container_width=True
    )

    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 10px;'>
            <span style='color: #a0aec0;'>Total PA Only</span>
            <br>
            <b style='font-size: 1.4rem; color: #ffffff;'>
                {int(total_pa_area):,} km²
            </b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 6-3. OECM Area by Realm
# ============================================================
with btm_col3:

    st.markdown("### 🌿 OECM Area by Realm")
    st.caption("(OECM only)")

    oecm_vals = [
        oecm_only.loc["marine", "gis_area_km2"],
        oecm_only.loc["terrestrial", "gis_area_km2"]
    ]

    total_oecm_area = sum(oecm_vals)

    fig_oecm = go.Figure(
        data=[
            go.Pie(
                labels=labels_order,
                values=oecm_vals,

                marker=dict(
                    colors=[
                        COLOR_MARINE,
                        COLOR_TERRESTRIAL
                    ]
                ),

                textinfo="percent",

                textfont=dict(
                    size=12,
                    color="white"
                ),

                sort=False
            )
        ]
    )

    fig_oecm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#dbe4f0",
                size=11
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=55
        ),

        height=250
    )

    st.plotly_chart(
        fig_oecm,
        use_container_width=True
    )

    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 10px;'>
            <span style='color: #a0aec0;'>Total OECM Only</span>
            <br>
            <b style='font-size: 1.4rem; color: #ffffff;'>
                {int(total_oecm_area):,} km²
            </b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# 7. Methodology footer
# ------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <hr style='border-color: #1c2a4f; margin-top: 20px;'>
    <p style='text-align: center; color: #718096; font-size: 0.78rem;'>
        WDPCA-derived spatial analysis · EPSG:6933 equal-area projection ·
        Target 3 eligibility mask excludes Antarctica and areas beyond
        national EEZs · Official Target 3 denominators from
        Protected Planet Report 2024
    </p>
    """,
    unsafe_allow_html=True
)