from pathlib import Path
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
	page_title="Netflix | Audience overview",
	page_icon="N",
	layout="wide",
	initial_sidebar_state="expanded",
)

DATA_FILES = ("netflix.csv.csv", "netflix.csv")
REQUIRED_COLUMNS = {
	"Customer_ID",
	"Region",
	"Subscription_Plan",
	"Title",
	"Category",
	"Type",
	"Rating",
	"Watch_Count",
	"Watch_Date",
	"Watch_Time_Minutes",
	"Monthly_Revenue",
}


@st.cache_data(show_spinner=False)
def load_data(csv_bytes):
	data = pd.read_csv(BytesIO(csv_bytes))
	data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
	return data


def format_number(value):
	return f"{value:,.0f}"


st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
	:root {
		--ink: #f5f5f1;
		--muted: #a1a1a1;
		--paper: #080808;
		--line: #2b2b2b;
		--coral: #e50914;
		--teal: #48c7b1;
		--gold: #e5a93b;
	}
	html, body, [class*="st-"], button, input {
		font-family: 'DM Sans', sans-serif;
	}
	.stApp { background: var(--paper); color: var(--ink); }
	[data-testid="stHeader"] { background: transparent; }
	[data-testid="stSidebar"] {
		background: #111111;
		border-right: 1px solid var(--line);
	}
	[data-testid="stSidebar"] > div { padding-top: 1.35rem; }
	.block-container { max-width: 1440px; padding-top: 2.4rem; padding-bottom: 3rem; }
	.masthead {
		display: flex; justify-content: space-between; align-items: flex-end;
		gap: 1.5rem; padding: 0 0 1.55rem; border-bottom: 1px solid var(--line);
		margin-bottom: 1.5rem;
	}
	.eyebrow {
		color: var(--coral); font-size: .72rem; font-weight: 700;
		letter-spacing: .12em; text-transform: uppercase; margin-bottom: .55rem;
	}
	.masthead h1 {
		color: var(--ink); font-family: 'Manrope', sans-serif; font-size: 2.15rem;
		font-weight: 800; line-height: 1.1; margin: 0;
	}
	.masthead p { color: var(--muted); font-size: .94rem; margin: .5rem 0 0; }
	.brand-mark {
		color: var(--coral); font-family: 'Manrope', sans-serif;
		font-size: 1.6rem; font-weight: 800; white-space: nowrap;
	}
	.section-label {
		color: var(--muted); font-size: .72rem; font-weight: 700;
		letter-spacing: .1em; text-transform: uppercase; margin: .25rem 0 .75rem;
	}
	[data-testid="stMetric"] {
		background: #151515; border: 1px solid var(--line); border-radius: 5px;
		padding: .85rem .9rem; min-height: 100px;
	}
	[data-testid="stMetricLabel"] { color: var(--muted); font-size: .8rem; }
	[data-testid="stMetricValue"] {
		color: var(--ink); font-family: 'Manrope', sans-serif;
		font-size: 1.5rem; font-weight: 700;
	}
	[data-testid="stPlotlyChart"] {
		background: #151515; border: 1px solid var(--line); border-radius: 5px;
		padding: .45rem .55rem .1rem;
	}
	div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 5px; }
	.sidebar-heading {
		color: var(--coral); font-family: 'Manrope', sans-serif;
		font-size: 1.35rem; font-weight: 800; margin-bottom: .15rem;
	}
	.sidebar-caption { color: var(--muted); font-size: .82rem; margin-bottom: 1.4rem; }
	[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
	[data-testid="stDateInput"] input,
	[data-testid="stTextInput"] input {
		background: #1b1b1b; color: var(--ink); border-color: #393939;
	}
	[data-testid="stFileUploader"] [data-testid="stIconMaterial"] { display: none; }
	@media (max-width: 700px) {
		.block-container { padding: 1.3rem 1rem 2rem; }
		.masthead h1 { font-size: 1.75rem; }
	}
	</style>
	""",
	unsafe_allow_html=True,
)

data_path = next(
	(Path(__file__).resolve().parent / filename for filename in DATA_FILES
	 if (Path(__file__).resolve().parent / filename).exists()),
	None,
)

st.sidebar.markdown('<div class="sidebar-heading">NETFLIX</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-caption">Audience overview</div>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload a CSV dataset", type="csv")

if uploaded_file is None and data_path is None:
	st.error("No dataset found. Upload a CSV with the expected Netflix viewing columns.")
	st.stop()

try:
	csv_bytes = uploaded_file.getvalue() if uploaded_file else data_path.read_bytes()
	netflix = load_data(csv_bytes)
except Exception as error:
	st.error(f"The dataset could not be loaded: {error}")
	st.stop()

missing_columns = REQUIRED_COLUMNS.difference(netflix.columns)
if missing_columns:
	st.error(f"The dataset is missing required columns: {', '.join(sorted(missing_columns))}")
	st.stop()

valid_dates = netflix["Watch_Date"].dropna()
if valid_dates.empty:
	st.error("No valid dates were found in the Watch_Date column.")
	st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)
regions = sorted(netflix["Region"].dropna().unique().tolist())
plans = sorted(netflix["Subscription_Plan"].dropna().unique().tolist())
categories = sorted(netflix["Category"].dropna().unique().tolist())
content_types = sorted(netflix["Type"].dropna().unique().tolist())

selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_plans = st.sidebar.multiselect("Subscription plan", plans, default=plans)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
selected_types = st.sidebar.multiselect("Content type", content_types, default=content_types)
date_range = st.sidebar.date_input(
	"Watch date",
	value=(valid_dates.min().date(), valid_dates.max().date()),
	min_value=valid_dates.min().date(),
	max_value=valid_dates.max().date(),
)
search = st.sidebar.text_input("Search title", placeholder="Start typing a title")

filtered = netflix[
	netflix["Region"].isin(selected_regions)
	& netflix["Subscription_Plan"].isin(selected_plans)
	& netflix["Category"].isin(selected_categories)
	& netflix["Type"].isin(selected_types)
]
if len(date_range) == 2:
	filtered = filtered[
		filtered["Watch_Date"].dt.date.between(date_range[0], date_range[1])
	]
if search.strip():
	filtered = filtered[filtered["Title"].str.contains(search.strip(), case=False, na=False)]

st.markdown(
	"""
	<div class="masthead">
		<div>
			<div class="eyebrow">Audience intelligence</div>
			<h1>Audience overview</h1>
			<p>A closer look at what people watch, where they watch, and how they subscribe.</p>
		</div>
		<div class="brand-mark">NETFLIX</div>
	</div>
	""",
	unsafe_allow_html=True,
)

st.markdown('<div class="section-label">At a glance</div>', unsafe_allow_html=True)
metric_columns = st.columns(4)
metric_values = [
	("Records", format_number(len(filtered))),
	("Customers", format_number(filtered["Customer_ID"].nunique())),
	("Revenue", f"{filtered['Monthly_Revenue'].sum() / 1000:.1f}K"),
	("Avg rating", f"{filtered['Rating'].mean():.1f}" if not filtered.empty else "—"),
]
for column, (label, value) in zip(metric_columns, metric_values):
	column.metric(label, value)

if filtered.empty:
	st.info("No records match these filters. Adjust the selections in the sidebar.")
	st.stop()

st.markdown('<div class="section-label">Viewing trends</div>', unsafe_allow_html=True)
px.defaults.template = "plotly_dark"
trend_data = filtered.assign(Month=filtered["Watch_Date"].dt.to_period("M").dt.to_timestamp())
monthly_revenue = trend_data.groupby("Month", as_index=False)["Monthly_Revenue"].sum()
monthly_sessions = trend_data.groupby("Month", as_index=False).size().rename(columns={"size": "Viewing records"})
monthly = monthly_revenue.merge(monthly_sessions, on="Month")
left_chart, right_chart = st.columns([1.45, 1])
with left_chart:
	chart = px.area(
		monthly, x="Month", y="Monthly_Revenue", markers=True,
		color_discrete_sequence=["#48c7b1"],
	)
	chart.update_traces(line_width=3, fillcolor="rgba(72, 199, 177, 0.13)", hovertemplate="%{x|%b %Y}<br>Revenue: %{y:,.0f}<extra></extra>")
	chart.update_layout(title="Monthly revenue", height=330, showlegend=False, xaxis_title=None, yaxis_title=None)
	st.plotly_chart(chart, width="stretch")
with right_chart:
	plan_data = filtered.groupby("Subscription_Plan", as_index=False)["Customer_ID"].nunique()
	plan_data = plan_data.rename(columns={"Customer_ID": "Customers"})
	chart = px.bar(
		plan_data, x="Customers", y="Subscription_Plan", orientation="h",
		color="Subscription_Plan",
		color_discrete_map={"Basic": "#e50914", "Premium": "#48c7b1", "Standard": "#e5a93b"},
	)
	chart.update_layout(title="Customers by plan", height=330, showlegend=False, xaxis_title=None, yaxis_title=None)
	st.plotly_chart(chart, width="stretch")

st.markdown('<div class="section-label">Audience and content</div>', unsafe_allow_html=True)
region_data = filtered.groupby("Region", as_index=False)["Monthly_Revenue"].sum().sort_values("Monthly_Revenue")
category_data = filtered.groupby("Category", as_index=False).agg(
	Average_rating=("Rating", "mean"), Viewing_records=("Customer_ID", "size")
).sort_values("Average_rating")
region_chart, category_chart = st.columns(2)
with region_chart:
	chart = px.bar(
		region_data, x="Monthly_Revenue", y="Region", orientation="h",
		color="Monthly_Revenue", color_continuous_scale=["#b9d9d3", "#16877e"],
	)
	chart.update_layout(title="Revenue by region", height=330, coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
	st.plotly_chart(chart, width="stretch")
with category_chart:
	chart = px.bar(
		category_data, x="Average_rating", y="Category", orientation="h",
		color="Average_rating", color_continuous_scale=["#f2d79f", "#e34d43"],
		range_x=[0, 5], hover_data={"Viewing_records": True, "Average_rating": ":.2f"},
	)
	chart.update_layout(title="Average rating by category", height=330, coloraxis_showscale=False, xaxis_title="Rating out of 5", yaxis_title=None)
	st.plotly_chart(chart, width="stretch")

st.markdown('<div class="section-label">Viewing records</div>', unsafe_allow_html=True)
table_columns = [
	"Watch_Date", "Title", "Category", "Type", "Region", "Subscription_Plan",
	"Rating", "Watch_Count", "Watch_Time_Minutes", "Monthly_Revenue",
]
display_data = filtered[table_columns].sort_values("Watch_Date", ascending=False).rename(
	columns={
		"Watch_Date": "Watch date", "Category": "Category", "Type": "Format",
		"Subscription_Plan": "Plan", "Rating": "Rating", "Watch_Count": "Watch count",
		"Watch_Time_Minutes": "Minutes watched", "Monthly_Revenue": "Monthly revenue",
	}
)
st.dataframe(display_data, width="stretch", hide_index=True)
st.download_button(
	"Download filtered records",
	data=display_data.to_csv(index=False).encode("utf-8"),
	file_name="netflix_filtered_records.csv",
	mime="text/csv",
)

