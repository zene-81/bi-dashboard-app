import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Executive Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", end="2026-08-31", freq="D")
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
    categories = ["Enterprise", "Mid-Market", "SMB"]

    data = []
    for date in dates:
        for _ in range(np.random.randint(5, 15)):
            data.append(
                {
                    "Date": date,
                    "Region": np.random.choice(regions),
                    "Category": np.random.choice(categories),
                    "Revenue": np.random.uniform(100, 5000),
                    "User_ID": np.random.randint(1000, 9999),
                    "Is_Churned": np.random.choice([0, 1], p=[0.93, 0.07]),
                }
            )
    return pd.DataFrame(data)


df_raw = load_data()

st.sidebar.header("🔍 Dashboard Filters")
min_date = df_raw["Date"].min().date()
max_date = df_raw["Date"].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df_raw["Region"].unique(),
    default=df_raw["Region"].unique(),
)
selected_categories = st.sidebar.multiselect(
    "Select Category(ies)",
    options=df_raw["Category"].unique(),
    default=df_raw["Category"].unique(),
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (
        (df_raw["Date"].dt.date >= start_date)
        & (df_raw["Date"].dt.date <= end_date)
        & (df_raw["Region"].isin(selected_regions))
        & (df_raw["Category"].isin(selected_categories))
    )
    df = df_raw.loc[mask]
else:
    df = df_raw.copy()

st.title("📊 Business Intelligence Executive Overview")
st.markdown("---")

total_revenue = df["Revenue"].sum()
active_users = df["User_ID"].nunique()
churn_rate = (
    (df["Is_Churned"].sum() / len(df) * 100) if len(df) > 0 else 0.0
)
avg_ticket_size = df["Revenue"].mean() if len(df) > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Active Users", f"{active_users:,}")
col3.metric("Churn Rate", f"{churn_rate:.2f}%")
col4.metric("Avg Ticket Size", f"${avg_ticket_size:,.2f}")

st.markdown("---")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.subheader("📈 Revenue Trend Over Time")
    df_trend = (
        df.groupby(pd.Grouper(key="Date", freq="W"))["Revenue"]
        .sum()
        .reset_index()
    )
    fig_trend = px.line(
        df_trend,
        x="Date",
        y="Revenue",
        markers=True,
        labels={"Revenue": "Revenue ($)", "Date": "Week"},
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with row1_col2:
    st.subheader("🌍 Revenue by Region")
    df_region = (
        df.groupby("Region")["Revenue"]
        .sum()
        .reset_index()
        .sort_values(by="Revenue", ascending=False)
    )
    fig_region = px.bar(
        df_region,
        x="Region",
        y="Revenue",
        color="Region",
        text_auto=".2s",
        labels={"Revenue": "Revenue ($)"},
    )
    st.plotly_chart(fig_region, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.subheader("💼 Revenue Share by Category")
    df_category = df.groupby("Category")["Revenue"].sum().reset_index()
    fig_category = px.pie(df_category, names="Category", values="Revenue", hole=0.4)
    st.plotly_chart(fig_category, use_container_width=True)

with row2_col2:
    st.subheader("📊 Average Deal Size Heatmap")
    df_heatmap = df.groupby(["Region", "Category"])["Revenue"].mean().unstack()
    fig_heatmap = px.imshow(
        df_heatmap,
        text_auto=".0f",
        aspect="auto",
        labels=dict(x="Category", y="Region", color="Avg Ticket ($)"),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)