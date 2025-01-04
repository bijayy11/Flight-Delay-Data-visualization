import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Flight Metrics Time Series Analysis",
    page_icon="✈️",
    layout="wide"
)

# Title and Description
st.title("✈️ Flight Metrics Time Series Analysis")
st.markdown("""
Explore trends in flight metrics from 2009 to 2018 with interactive visualizations.  
Select a metric below to dive deeper into the data!
""")

# Metrics and corresponding files
metrics = {
    "Average Departure Delay (by Origin)": "airport_delays.csv",
    "Carrier Delays by Type": "carrier_delays.csv",
    "Average Departure Delay (by Hour)": "departure_delay_by_hour.csv",
    "Average Taxi Time (Hourly)": "taxi_hourly.csv",
    "Flight Count by State": "state_flight_counts.csv",
    "Top Flight Routes by Count": "origin_dest_counts.csv"
}

# Dropdown for metric selection
metric_selection = st.selectbox("Select a Metric for Analysis:", list(metrics.keys()))

# Function to load data
def load_data(metric_file, years=range(2009, 2019)):
    combined_data = pd.DataFrame()
    for year in years:
        file_path = f"./datasets/AGG_Datasets/{year}/{metric_file}"
        yearly_data = pd.read_csv(file_path)
        yearly_data['Year'] = year
        combined_data = pd.concat([combined_data, yearly_data], ignore_index=True)
    return combined_data

# Load data for the selected metric
data = load_data(metrics[metric_selection])

# Create visualizations
if metric_selection == "Average Departure Delay (by Origin)":
    st.subheader("📈 Average Departure Delay by Origin")
    fig = px.line(
        data,
        x="Year",
        y="Average Departure Delay",
        color="ORIGIN",
        title="Average Departure Delay by Origin (2009-2018)",
        labels={
            "Year": "Year",
            "Average Departure Delay": "Delay (minutes)",
            "ORIGIN": "Airport Origin"
        },
        template="plotly_dark",
        line_shape="spline"
    )
    fig.update_traces(mode="lines+markers", marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Carrier Delays by Type":
    st.subheader("📊 Carrier Delays by Type")
    delay_types = ["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]
    delay_data = data.melt(
        id_vars=["OP_CARRIER", "Year"],
        value_vars=delay_types,
        var_name="Delay Type",
        value_name="Delay (minutes)"
    )
    fig = px.area(
        delay_data,
        x="Year",
        y="Delay (minutes)",
        color="Delay Type",
        facet_col="OP_CARRIER",
        facet_col_wrap=3,
        title="Carrier Delays by Type (2009-2018)",
        labels={"Year": "Year", "Delay Type": "Type of Delay"},
        template="plotly_white"
    )
    fig.update_traces(mode="lines")
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Average Departure Delay (by Hour)":
    st.subheader("🕒 Average Departure Delay by Hour")
    fig = px.line(
        data,
        x="Hour",
        y="Average Departure Delay",
        title="Average Departure Delay by Hour",
        labels={"Hour": "Hour of the Day", "Average Departure Delay": "Delay (minutes)"},
        template="plotly_dark",
        line_shape="spline"
    )
    fig.update_traces(line=dict(color="blue", width=3), mode="lines+markers", marker=dict(size=8, color="red"))
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Average Taxi Time (Hourly)":
    st.subheader("🚖 Average Taxi Time by Hour")
    data['Average Taxi Time'] = data[['TAXI_IN', 'TAXI_OUT']].mean(axis=1)
    fig = px.bar(
        data,
        x="Hour",
        y="Average Taxi Time",
        color="Hour",
        title="Average Taxi Time by Hour",
        labels={"Hour": "Hour of the Day", "Average Taxi Time": "Minutes"},
        template="plotly_white",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Flight Count by State":
    st.subheader("🌍 Flight Count by State")
    fig = px.choropleth(
        data,
        locations="ORIGIN_STATE",
        locationmode="USA-states",
        color="Flight Count",
        scope="usa",
        title="Flight Count by State (2009-2018)",
        labels={"ORIGIN_STATE": "State", "Flight Count": "Number of Flights"},
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Top Flight Routes by Count":
    st.subheader("📍 Top 10 Flight Routes by Count")
    top_routes = data.groupby(['ORIGIN', 'DEST']).sum().reset_index().nlargest(10, 'Flight Count')
    fig = px.bar(
        top_routes,
        x="Flight Count",
        y=["ORIGIN", "DEST"],
        title="Top 10 Flight Routes by Count (2009-2018)",
        labels={"Flight Count": "Number of Flights", "ORIGIN": "Origin", "DEST": "Destination"},
        template="plotly_white",
        orientation="h"
    )
    fig.update_traces(marker=dict(color="orange"))
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.info("📌 Select different metrics using the dropdown menu above to explore various trends.")
