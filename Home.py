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
st.header(f"✈️ Flight Delay & Cancellation Analysis Dashboard ({selected_year})")

# Load GeoJSON for US states
us_states_geojson = load_geojson("datasets/us_states_geojson.json")

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
st.info(
    "The chart illustrates the number of airports per state, with states on the x-axis and airport counts on the y-axis. It uses a Viridis gradient, where lighter colors represent states with higher no of airports, effectively highlighting regional airport distribution."
)
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
st.info(
    "The chart displays a geo heatmap of flight origins by state in the United States, where states are color-coded based on total flight counts. Lighter colors indicate higher flight activity, offering a clear visualization of regional flight origins and their concentration across the country."
)
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

# Visualization 3: Sunburst Chart of Flight Origin and Destinations by State and Airport
st.subheader("Sunburst Chart of Flight Counts by State and Airport")
st.info(
    "The chart visualizes the breakdown of flight origins by state and airport, with a hierarchical structure. The first level shows the origin state, and the second level details individual airports. The size of each section represents flight count, and the color gradient indicates flight intensity, with lighter sections signifying higher activity. This chart provides a detailed view of flight distribution, highlighting key hubs and regions with significant flight traffic."
)
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

st.info(
    "The chart for flight destinations shows a hierarchical breakdown of flights by destination state and airport. The first level represents the destination state, while the second level breaks it down by individual airports. The size of each segment corresponds to the number of flights, with a color gradient indicating flight count intensity—lighter sections represent higher volumes. This visualization offers an in-depth look at the distribution of flights, highlighting major destinations and the scale of travel to each location."
)
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
st.info(
    "The graph presents a stacked comparison of delay types (Carrier, Weather, NAS, Security, and Late Aircraft delays) for different airlines. Each bar represents an airline, with segments showing the average delay time for each category. This chart allows for a clear comparison of the contributions of each delay type to the total delay time for each carrier."
)
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
st.info(
    "The chart visualizes the distribution of flight cancellations by cause. Each slice of the pie represents a different reason for cancellations, with the slice size corresponding to the number of cancellations. The reasons are: A for Air Carrier issues, B for Weather conditions, C for National Air System delays, and D for Security concerns."
)
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
st.info(
    "The graph visualizes the average delay times for departures from different airports. Each bar represents an airport, with the height indicating the average delay in minutes. This chart helps identify airports with longer delays, offering insights into operational challenges or areas for improvement."
)
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
st.info(
    "The plot illustrates the relationship between flight distance and arrival delay. Each point represents a flight, with the horizontal axis showing distance in miles and the vertical axis showing arrival delay in minutes. Points are color-coded by carrier, allowing users to distinguish delays by different airlines. This visualization helps identify trends, such as whether longer flights have more significant delays or if specific carriers experience longer delays over certain distances."
)
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
st.info(
    "The map shows the distribution of average arrival delays across airports in the US. Each airport is represented by a bubble, with the bubble size proportional to the average arrival delay, and the color indicating the delay magnitude. This visualization highlights regional patterns in delays, making it easy to identify airports with higher or lower average arrival delays."
)
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
st.subheader("Monthly Delays and Cancellations")
st.info(
    "The chart presents a line graph tracking the average delays for departures and arrivals, along with flight cancellations, for each month. It features three lines: red for departure delays, blue for arrival delays, and green for cancellations. This chart offers insights into monthly trends, helping identify patterns in delays and cancellations."
)
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
st.info(
    "The plot visualizes the relationship between taxi-out time (time taken for the aircraft to leave the gate) and taxi-in time (time taken to return to the gate after landing). Each data point represents a flight, with taxi-out time on the x-axis and taxi-in time on the y-axis. Points are color-coded by carrier. This chart helps identify any correlation between the two variables, such as whether longer taxi-out times are associated with longer taxi-in times."
)
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
st.info(
    "The graph shows the relationship between the hour of the day and the average departure delay. The x-axis represents different hours, and the y-axis displays the average departure delay in minutes. Each bar indicates the average delay for flights departing at a specific hour. This chart helps identify trends, such as whether delays are more frequent during certain times of the day, offering valuable insights for analyzing peak delay times."
)
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
st.info(
    "The graph shows the percentage of cancellations for each airline carrier. The x-axis represents different carriers, and the y-axis displays the cancellation rate as a percentage. Each bar is color-coded according to the cancellation rate, with the color scale indicating the magnitude. This visualization enables easy comparison of cancellation rates across carriers, highlighting those with higher or lower cancellation percentages and providing insights for identifying patterns and potential areas of improvement in the airline industry."
)
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
st.info(
    "The graph shows the airlines with the highest arrival delays. The x-axis represents arrival delay in minutes, while the y-axis lists the airlines. Each bar represents an airline, with the length corresponding to the average arrival delay. Bars are color-coded based on delay duration, with the color scale indicating the severity of delays. This visualization makes it easy to identify which airlines experience the most delays, offering insights into performance and potential areas for improvement."
)
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
st.info(
    "The plot visualizes how the average arrival delay has changed over time. The x-axis represents flight dates, and the y-axis shows the average arrival delay in minutes. Each data point corresponds to the average delay for a specific day, with lines connecting the points to highlight the trend. A range slider at the bottom lets users zoom into specific time frames, such as the past month, six months, or year. This chart helps identify trends in delays and track the impact of interventions or seasonal variations."
)

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
