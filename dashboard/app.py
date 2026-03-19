from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Beastlife Customer Intelligence", layout="wide")

st.title("Beastlife AI Customer Intelligence Dashboard")
st.caption("Issue distribution, channel insights, and weekly/monthly trend monitoring")

base_dir = Path(__file__).resolve().parent.parent
output_dir = base_dir / "outputs"

classified_path = output_dir / "classified_queries.csv"
distribution_path = output_dir / "issue_distribution.csv"
weekly_path = output_dir / "weekly_trends.csv"
monthly_path = output_dir / "monthly_trends.csv"

if not all(p.exists() for p in [classified_path, distribution_path, weekly_path, monthly_path]):
    st.warning("Analytics files not found. Run: python src/analyze_queries.py")
    st.stop()

classified = pd.read_csv(classified_path)
distribution = pd.read_csv(distribution_path)
weekly = pd.read_csv(weekly_path)
monthly = pd.read_csv(monthly_path)

classified["timestamp"] = pd.to_datetime(classified["timestamp"])
weekly["timestamp"] = pd.to_datetime(weekly["timestamp"])
monthly["timestamp"] = pd.to_datetime(monthly["timestamp"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Queries", f"{len(classified):,}")
col2.metric("Top Issue", distribution.iloc[0]["predicted_category"])
col3.metric("Top Issue %", f"{distribution.iloc[0]['percentage']}%")

st.subheader("Issue Type Distribution")
left, right = st.columns([1, 1])

with left:
    pie = px.pie(
        distribution,
        names="predicted_category",
        values="query_count",
        hole=0.45,
        title="Share of total queries",
    )
    st.plotly_chart(pie, use_container_width=True)

with right:
    bar = px.bar(
        distribution,
        x="predicted_category",
        y="percentage",
        title="Issue percentage by category",
        labels={"predicted_category": "Issue Type", "percentage": "% of Queries"},
    )
    bar.update_xaxes(tickangle=-25)
    st.plotly_chart(bar, use_container_width=True)

st.subheader("Trend Monitoring")
granularity = st.radio("Time window", ["Weekly", "Monthly"], horizontal=True)
trend_df = weekly if granularity == "Weekly" else monthly

line = px.line(
    trend_df,
    x="timestamp",
    y="query_count",
    color="predicted_category",
    markers=True,
    title=f"{granularity} trend by issue type",
    labels={"timestamp": "Date", "query_count": "Query Count", "predicted_category": "Issue"},
)
st.plotly_chart(line, use_container_width=True)

st.subheader("Channel Mix")
channel_dist = (
    classified.groupby("channel").size().reset_index(name="query_count").sort_values("query_count", ascending=False)
)
channel_chart = px.bar(channel_dist, x="channel", y="query_count", title="Query volume by source channel")
st.plotly_chart(channel_chart, use_container_width=True)

st.subheader("Detailed Classified Queries")
st.dataframe(
    classified[["query_id", "timestamp", "channel", "customer_message", "predicted_category", "confidence"]],
    use_container_width=True,
)
