import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Coffee Quality Explorer", page_icon="☕", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "coffee.csv")

# Theme
COFFEE_COLORS = ["#C08552", "#DDB892", "#7F5539", "#9C6644", "#B08968", "#E6CCB2", "#603813"]
CHART_TEMPLATE = "plotly_dark"
PLOT_BG = "#1B120E"

st.markdown(
    """
    <style>
    .stApp { background-color: #1B120E; }
    h1, h2, h3 { font-family: 'Georgia', serif; color: #F5E9DA !important; }
    [data-testid="stMetric"] {
        background-color: #2B1B12;
        border: 1px solid #4A2E1F;
        border-radius: 10px;
        padding: 14px 10px;
    }
    [data-testid="stMetricLabel"] { color: #DDB892 !important; }
    [data-testid="stMetricValue"] { color: #F5E9DA !important; }
    section[data-testid="stSidebar"] { background-color: #150D09; border-right: 1px solid #4A2E1F; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #7F5539 !important; }
    hr { border-color: #4A2E1F !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df
    
ISO3 = {
    "Brazil": "BRA", "Burundi": "BDI", "China": "CHN", "Colombia": "COL",
    "Costa Rica": "CRI", "Cote d?Ivoire": "CIV", "Ecuador": "ECU", "El Salvador": "SLV",
    "Ethiopia": "ETH", "Guatemala": "GTM", "Haiti": "HTI", "Honduras": "HND",
    "India": "IND", "Indonesia": "IDN", "Japan": "JPN", "Kenya": "KEN",
    "Laos": "LAO", "Malawi": "MWI", "Mauritius": "MUS", "Mexico": "MEX",
    "Myanmar": "MMR", "Nicaragua": "NIC", "Panama": "PAN", "Papua New Guinea": "PNG",
    "Peru": "PER", "Philippines": "PHL", "Rwanda": "RWA", "Taiwan": "TWN",
    "Tanzania, United Republic Of": "TZA", "Thailand": "THA", "Uganda": "UGA",
    "United States": "USA", "United States (Hawaii)": "USA",
    "United States (Puerto Rico)": "PRI", "Vietnam": "VNM", "Zambia": "ZMB",
}

df = load_data()
df["iso3"] = df["country"].map(ISO3)

# Header
st.title("☕ Coffee Quality Explorer")
st.markdown(
    "Explore **1,300+ Arabica coffees** professionally graded by the "
    "[Coffee Quality Institute](https://www.coffeeinstitute.org/). "
    "Filter by origin and processing method, hover the map, and see what actually drives a great cup."
)

# Sidebar
st.sidebar.header("☕ Filters")

countries = sorted(df["country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Country of origin", countries, default=["Ethiopia", "Colombia", "Brazil", "Guatemala"]
)

methods = sorted(df["processing_method"].dropna().unique())
selected_methods = st.sidebar.multiselect(
    "Processing method", methods, default=methods
)

score_range = st.sidebar.slider(
    "Total quality score range", float(df["total_score"].min()), float(df["total_score"].max()),
    (75.0, float(df["total_score"].max()))
)

filtered = df[
    (df["country"].isin(selected_countries) if selected_countries else True)
    & (df["processing_method"].isin(selected_methods) if selected_methods else True)
    & (df["total_score"].between(*score_range))
]

st.sidebar.markdown(f"**{len(filtered)} coffees** match your filters")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Coffees shown", len(filtered))
col2.metric("Avg. score", f"{filtered['total_score'].mean():.1f}" if len(filtered) else "–")
col3.metric("Avg. altitude (m)", f"{filtered['altitude_m'].mean():.0f}" if filtered['altitude_m'].notna().any() else "–")
col4.metric("Countries", filtered["country"].nunique())

st.divider()

# World Map
st.subheader("🗺️ Where the coffee comes from")
st.caption("Hover any country to see its average score, coffee count, and top variety. This map always shows the full dataset, regardless of sidebar filters.")

map_data = (
    df.groupby(["country", "iso3"])
    .agg(
        avg_score=("total_score", "mean"),
        coffee_count=("total_score", "count"),
        avg_altitude=("altitude_m", "mean"),
    )
    .reset_index()
)
top_variety = (
    df.groupby("country")["variety"]
    .agg(lambda x: x.value_counts().idxmax() if x.notna().any() else "N/A")
    .reset_index(name="top_variety")
)
map_data = map_data.merge(top_variety, on="country")

fig_map = go.Figure(
    go.Choropleth(
        locations=map_data["iso3"],
        z=map_data["avg_score"],
        text=map_data["country"],
        customdata=map_data[["coffee_count", "avg_altitude", "top_variety"]],
        colorscale=[[0, "#3B2415"], [0.5, "#C08552"], [1, "#F5E9DA"]],
        colorbar_title="Avg. score",
        marker_line_color="#1B120E",
        marker_line_width=0.5,
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Avg. score: %{z:.1f}<br>"
            "Coffees reviewed: %{customdata[0]}<br>"
            "Avg. altitude: %{customdata[1]:.0f} m<br>"
            "Most common variety: %{customdata[2]}"
            "<extra></extra>"
        ),
    )
)
fig_map.update_layout(
    geo=dict(
        bgcolor=PLOT_BG,
        showframe=False,
        showcoastlines=False,
        projection_type="natural earth",
        landcolor="#2B1B12",
        oceancolor=PLOT_BG,
        lakecolor=PLOT_BG,
    ),
    paper_bgcolor=PLOT_BG,
    plot_bgcolor=PLOT_BG,
    margin=dict(l=0, r=0, t=10, b=0),
    height=420,
    font_color="#F5E9DA",
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Score distribution by country")
    if len(filtered):
        fig = px.box(
            filtered, x="country", y="total_score", color="country",
            points="outliers", template=CHART_TEMPLATE, color_discrete_sequence=COFFEE_COLORS
        )
        fig.update_layout(
            showlegend=False, xaxis_title="", yaxis_title="Total cup score",
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for current filters.")

with right:
    st.subheader("Altitude vs. quality score")
    if filtered["altitude_m"].notna().any():
        fig2 = px.scatter(
            filtered, x="altitude_m", y="total_score", color="country",
            hover_data=["variety", "processing_method"], template=CHART_TEMPLATE,
            trendline="ols", color_discrete_sequence=COFFEE_COLORS
        )
        fig2.update_layout(
            xaxis_title="Altitude (meters)", yaxis_title="Total cup score",
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No altitude data for current filters.")

st.subheader("Flavor profile comparison")
attributes = ["aroma", "flavor", "aftertaste", "acidity", "body", "balance", "sweetness"]
if selected_countries and len(filtered):
    radar_df = filtered.groupby("country")[attributes].mean().reset_index()
    fig3 = px.line_polar(
        radar_df.melt(id_vars="country", var_name="attribute", value_name="score"),
        r="score", theta="attribute", color="country", line_close=True,
        template=CHART_TEMPLATE, color_discrete_sequence=COFFEE_COLORS
    )
    fig3.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Select at least one country to compare flavor profiles.")

st.divider()

# Leaderboard
st.subheader("🏆 Top-rated coffees (current filters)")
top = filtered.sort_values("total_score", ascending=False).head(10)
st.dataframe(
    top[["country", "variety", "processing_method", "altitude_m", "total_score"]]
    .rename(columns={
        "country": "Country", "variety": "Variety", "processing_method": "Processing",
        "altitude_m": "Altitude (m)", "total_score": "Score"
    }),
    use_container_width=True, hide_index=True
)

st.caption("Data source: Coffee Quality Institute, via jldbc/coffee-quality-database on GitHub.")
