import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(
    page_icon="✈️",
    layout="wide"
)

@st.cache_data
def load_data(file_path):
    """Load pre-aggregated data from CSV."""
    return pd.read_csv(file_path)

@st.cache_data
def load_geojson(file_path):
    """Load GeoJSON data."""
    with open(file_path) as f:
        return json.load(f)

# Sidebar for Year Selection
st.sidebar.header("Year Selection")
years = [str(year) for year in range(2009, 2019)]  # List of available years (based on folder structure)
selected_year = st.sidebar.selectbox("Select a Year:", years)

# Function to load yearly datasets dynamically
@st.cache_data
def load_yearly_data(year, file_name):
    """Load dataset for the selected year."""
    file_path = f"datasets/AGG_Datasets/{year}/{file_name}"
    return pd.read_csv(file_path)

# Load datasets for the selected year
carrier_delays = load_yearly_data(selected_year, "carrier_delays.csv")
monthly_aggregates = load_yearly_data(selected_year, "monthly_aggregates.csv")
state_flight_counts = load_yearly_data(selected_year, "state_flight_counts.csv")
origin_dest_counts = load_yearly_data(selected_year, "origin_dest_counts.csv")
airport_delays = load_yearly_data(selected_year, "airport_delays.csv")
daily_delay_trend = load_yearly_data(selected_year, "daily_delay_trend.csv")
cancellation_reasons = load_yearly_data(selected_year, "cancellation_reasons.csv")
distance_vs_delay = load_yearly_data(selected_year, "distance_vs_delay.csv")
airport_bubble_map = load_yearly_data(selected_year, "airport_bubble_map.csv")
departure_delay_by_hour = load_yearly_data(selected_year, "departure_delay_by_hour.csv")
cancellation_percentage_by_carrier = load_yearly_data(selected_year, "cancellation_percentage_by_carrier.csv")
airlines_most_delays = load_yearly_data(selected_year, "airlines_most_delays.csv")
state_airport_count = load_yearly_data(selected_year, "state_airport_count.csv")
origin_state_data = load_yearly_data(selected_year, "origin_state_data.csv")
destination_state_data = load_yearly_data(selected_year, "destination_state_data.csv")
taxi_data = load_yearly_data(selected_year, "taxi_times.csv")

# Update title to reflect selected year
st.title(f"✈️ Flight Delay & Cancellation Analysis Dashboard ({selected_year})")

# Load GeoJSON for US states
us_states_geojson = load_geojson("datasets/us_states_geojson.json")

st.info(
    """
    This dashboard provides insights into flight cancellation and delay data. Visualizations include:
    - Bar Chart of Number of Airports in Each State
    - Geo heatmaps of flight origins
    - Sunburst Chart of Flight Destinations by State and Airport
    - Bar Graph of Average Delays by Carrier
    - Pie Chart of Flight Cancellations by Reason
    - Bar Graph of Average Departure Delays by Airport
    - Scatter Plot of Distance vs. Delay
    - Bubble Map of Arrival Delays by Airport in the US
    - Line plot of Monthly Delays and Cancellations (Average)
    - Scatter Plot of Taxi Out vs Taxi In Times
    - Bar Graph of Average Departure Delay by Time of Day
    - Bar Graph of Cancellations Percentage by Carrier
    - Horizontal Bar Graph of Airlines with the Most Delays
    - Line plot of Trend of Average Arrival Delay Over Time
    """
)

# Sidebar filters
st.sidebar.header("Filters")
carrier_filter = st.sidebar.multiselect(
    "Select Carrier(s):",
    options=carrier_delays["OP_CARRIER"].unique(),
    default=carrier_delays["OP_CARRIER"].unique()
)

origin_filter = st.sidebar.multiselect(
    "Select Origin(s):",
    options=origin_state_data["State"].unique(),
    default=origin_state_data["State"].unique()
)

# Apply filters
filtered_carrier_delays = carrier_delays[carrier_delays["OP_CARRIER"].isin(carrier_filter)]
filtered_origin_data = origin_state_data[origin_state_data["State"].isin(origin_filter)]

# Visualization 1: Bar Chart of Number of Airports in Each State
st.subheader("Bar Chart of Number of Airports in Each State")
fig0 = px.bar(
    state_airport_count,
    x="STATE",
    y="Airport Count",
    title="Number of Airports in Each State",
    labels={"STATE": "State", "Airport Count": "Number of Airports"},
    color="Airport Count",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig0)

# Visualization 2: Geo Heatmap of Flight Origins by State
st.subheader("Geo Heatmap")
# Create geo heatmap visualization using Plotly
fig1 = px.choropleth(
    origin_state_data,
    locations="State",
    locationmode="USA-states",
    color="Origin Count",
    hover_name="State",
    hover_data={"Airport Count": True},  # Add airport count to hover data
    color_continuous_scale="Viridis",
    scope="usa",
    geojson=us_states_geojson,
    labels={"Origin Count": "Total Flight Count"},
    title="Geo Heatmap of Flight Origins by State"
)

# Update layout and geo settings for better fit and no background
fig1.update_geos(
    visible=True,           
    projection_type="albers usa", 
    projection_scale=1,
    center={"lat": 38, "lon": -95.7129},
    showcoastlines=True,
    coastlinecolor="Green",
    bgcolor='rgba(0,0,0,0)',
)

# Update layout to remove white background and increase map width
fig1.update_layout(
    width=1200,
    height=600 
)

# Show the plot
st.plotly_chart(fig1)

st.markdown("---")

# Visualization 3: Sunburst Chart of Flight Destinations by State and Airport
st.subheader("Sunburst Chart of Flight Counts by State and Airport")
cleaned_sunbrust = origin_dest_counts.dropna(subset=["ORIGIN_STATE", "ORIGIN","DEST_STATE","DEST"])

fig_origin = px.sunburst(
    cleaned_sunbrust,
    path=["ORIGIN_STATE", "ORIGIN"],  # Path for hierarchy: State -> Airport
    values="Flight Count",  # Values represent the flight count
    title="Flight Origins Breakdown by State and Airport",
    color="Flight Count",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig_origin)

# Sunburst Chart for Destinations
fig_dest = px.sunburst(
    cleaned_sunbrust,
    path=["DEST_STATE", "DEST"],  # Path for hierarchy: State -> Airport
    values="Flight Count",  # Values represent the flight count
    title="Flight Destinations Breakdown by State and Airport",
    color="Flight Count",
    color_continuous_scale="Cividis"
)
st.plotly_chart(fig_dest)

# Visualization 4: Bar Graph of Average Delays by Carrier
st.subheader("Bar Graph of Average Delays by Carrier")
fig3 = px.bar(
    filtered_carrier_delays,
    x="OP_CARRIER",
    y=["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"],
    title="Average Delays by Carrier",
    labels={"value": "Average Delay (minutes)", "variable": "Delay Type"},
    barmode="stack"
)
st.plotly_chart(fig3)

# Visualization 5: Pie Chart of Flight Cancellations by Reason
st.subheader("Pie Chart of Flight Cancellations by Reason")
fig4 = px.pie(
    cancellation_reasons,
    names="Reason",
    values="Count",
    title="Flight Cancellations by Reason",
    hole=0.4,
    template="plotly_white"
)
st.plotly_chart(fig4)

# Visualization 6: Bar Graph of Average Departure Delays by Airport
st.subheader("Bar Graph of Average Departure Delays by Airport")
fig5 = px.bar(
    airport_delays,
    x="ORIGIN",
    y="Average Departure Delay",
    title="Average Departure Delays by Airport",
    labels={"Average Departure Delay": "Delay (minutes)", "ORIGIN": "Origin Airport"}
)
st.plotly_chart(fig5)

# Visualization 7: Scatter Plot of Distance vs. Delay
st.subheader("Scatter Plot of Distance vs. Delay")
fig6 = px.scatter(
    distance_vs_delay,
    x="DISTANCE",
    y="ARR_DELAY",
    color="OP_CARRIER",
    title="Distance vs. Arrival Delay",
    labels={"DISTANCE": "Distance (miles)", "ARR_DELAY": "Arrival Delay (minutes)"}
)
st.plotly_chart(fig6)

# Ensure all size values in the bubble map are non-negative
airport_bubble_map["Average Arrival Delay"] = airport_bubble_map["Average Arrival Delay"].clip(lower=0)

# Visualization 8: Bubble Map of Arrival Delays by Airport in the US
st.subheader("Bubble Map of Arrival Delays by Airport in the US")
fig7 = px.scatter_geo(
    airport_bubble_map,
    lat="LATITUDE",
    lon="LONGITUDE",
    size="Average Arrival Delay",
    color="Average Arrival Delay",
    hover_name='ORIGIN', 
    size_max=10,    
    title="Arrival Delays by Airport in the US",
    scope="usa",
    color_continuous_scale="Viridis",
    template='plotly_white'
)
fig7.update_geos(
    visible=True,           
    projection_type="albers usa", 
    projection_scale=1,
    center={"lat": 38, "lon": -95.7129},
    showcoastlines=True,
    coastlinecolor="Green",
    bgcolor='rgba(0,0,0,0)',
)

# Update layout to remove white background and increase map width
fig7.update_layout(
    width=1200,
    height=600 
)


st.plotly_chart(fig7)

# Visualization 9: Monthly Delays and Cancellations
# Visualization 9: Monthly Delays and Cancellations
st.subheader("Monthly Delays and Cancellations")

# Create the figure
fig8 = go.Figure()

# Add trace for Departure Delay
fig8.add_trace(go.Scatter(
    x=monthly_aggregates["Month"],
    y=monthly_aggregates["DEP_DELAY"],
    mode="lines+markers",
    name="Departure Delay",
    line=dict(color='crimson', width=3),
    marker=dict(size=8, color='crimson', symbol='circle'),
    hovertemplate='Month: %{x}<br>Departure Delay: %{y} minutes'
))

# Add trace for Arrival Delay
fig8.add_trace(go.Scatter(
    x=monthly_aggregates["Month"],
    y=monthly_aggregates["ARR_DELAY"],
    mode="lines+markers",
    name="Arrival Delay",
    line=dict(color='royalblue', width=3),
    marker=dict(size=8, color='royalblue', symbol='circle'),
    hovertemplate='Month: %{x}<br>Arrival Delay: %{y} minutes'
))

# Add trace for Cancellations
fig8.add_trace(go.Scatter(
    x=monthly_aggregates["Month"],
    y=monthly_aggregates["CANCELLED"],
    mode="lines+markers",
    name="Cancellations",
    line=dict(color='green', width=3),
    marker=dict(size=8, color='green', symbol='circle'),
    hovertemplate='Month: %{x}<br>Cancellations: %{y}'
))

# Update layout for the figure
fig8.update_layout(
    title="Monthly Delays and Cancellations",
    xaxis_title="Month",
    yaxis_title="Average Delay (minutes) / Cancellations",
    template="plotly_dark",
    hovermode="x unified",   # Hover mode to show data for all traces at once
    legend_title="Delay Types",
    legend=dict(x=0.75, y=1),  # Position the legend
    margin=dict(l=40, r=40, t=40, b=40)  # Adjust margins for better readability
)

# Display the plot in Streamlit
st.plotly_chart(fig8)

# Visualization 10: Scatter Plot of Taxi Out vs Taxi In Times
st.subheader("Scatter Plot of Taxi Out vs Taxi In Times")
fig9 = px.scatter(
    taxi_data,
    x="TAXI_OUT",
    y="TAXI_IN",
    color="OP_CARRIER",
    title="Taxi Out vs Taxi In Times",
    labels={"TAXI_OUT": "Taxi Out Time (minutes)", "TAXI_IN": "Taxi In Time (minutes)"}
)
st.plotly_chart(fig9)

# Visualization 11: Bar Graph of Average Departure Delay by Time of Day
st.subheader("Bar Graph of Average Departure Delay by Time of Day")
fig10 = px.bar(
    departure_delay_by_hour,
    x="Hour",
    y="Average Departure Delay",
    title="Average Departure Delay by Time of Day",
    labels={"Hour": "Hour of Day", "Average Departure Delay": "Delay (minutes)"}
)
st.plotly_chart(fig10)

# Visualization 12: Bar Graph of Cancellations Percentage by Carrier
st.subheader("Bar Graph of Cancellations Percentage by Carrier")
fig11 = px.bar(
    cancellation_percentage_by_carrier,
    x="OP_CARRIER",
    y="Cancellation Rate",
    title="Cancellations Percentage by Carrier",
    labels={"Cancellation Rate": "Rate (%)", "OP_CARRIER": "Carrier"},
    color="Cancellation Rate",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig11)

# Visualization 13: Horizontal Bar Graph of Airlines with the Most Delays
st.subheader("Horizontal Bar Graph of Airlines with the Most Delays")
fig12 = px.bar(
    airlines_most_delays,
    x="ARR_DELAY",
    y="OP_CARRIER",
    orientation="h",
    title="Airlines with the Most Delays",
    labels={"ARR_DELAY": "Arrival Delay (minutes)", "OP_CARRIER": "Airline"},
    color="ARR_DELAY",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig12)

# Visualization 14: Line Plot of Trend of Average Arrival Delay Over Time
st.subheader("Line Plot of Trend of Average Arrival Delay Over Time")

daily_delay_trend['FL_DATE'] = pd.to_datetime(daily_delay_trend['FL_DATE'])

fig13 = px.line(
    daily_delay_trend,
    x="FL_DATE",
    y="Average Arrival Delay",
    title="Trend of Average Arrival Delay Over Time",
    labels={"FL_DATE": "Date", "Average Arrival Delay": "Delay (minutes)"},
    template="plotly_dark"
)
fig13.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True),
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
        type="date"  # Ensure x-axis is recognized as a date type
    )
)
fig13.update_traces(mode='lines+markers', hovertemplate='Date: %{x}<br>Avg Delay: %{y:.2f} mins')
st.plotly_chart(fig13)
st.write("---")
st.markdown("Dashboard built using pre-aggregated datasets for faster loading and interactive exploration.")
