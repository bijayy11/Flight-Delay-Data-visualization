import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(
    page_title="Flight Delay Visualization",
    page_icon="✈️",
    layout="wide"
)

# Cache data loading function
@st.cache_data
def load_sampled_data(file_path, sample_fraction=0.1):
    """
    Loads and samples flight delay data from a CSV file.
    :param file_path: Path to the dataset file.
    :param sample_fraction: Fraction of data to sample.
    :return: Sampled DataFrame.
    """
    data = pd.read_csv(file_path).sample(frac=sample_fraction, random_state=42)
    return data

# Cache function to load airports data
@st.cache_data
def load_airports_data(file_path):
    """
    Loads the airport data.
    :param file_path: Path to the airport data file.
    :return: DataFrame containing airport details.
    """
    return pd.read_csv(file_path)

# Load the US States GeoJSON
@st.cache_data
def load_geojson(file_path):
    """
    Loads a GeoJSON file for US states.
    :param file_path: Path to the geojson file.
    :return: Loaded GeoJSON data.
    """
    with open(file_path) as f:
        return json.load(f)

# Title and description
st.title("✈️ Flight Delay & Cancellation Analysis Dashboard")
st.info(
    """
    This dashboard provides insights into flight cancellation and delay data. Visualizations include:
    - Bar Chart of Number of Airports in Each State
    - Geo heatmaps of flight origins
    - Sunburst Chart of Flight Destinations by State and Airport
    - Delay and cancellation statistics
    - Distance vs. Delay Scatter Plot
    - Distribution of flight delays by carrier and airports
    """
)

# Load and preprocess data
data = load_sampled_data("../datasets/2009.csv", sample_fraction=0.1)
airports_data = load_airports_data("../datasets/airports.csv")
us_states_geojson = load_geojson("../datasets/us_states_geojson.json")

# Fill missing data
data.fillna({
    "CANCELLATION_CODE": "None",
    "CARRIER_DELAY": 0,
    "WEATHER_DELAY": 0,
    "NAS_DELAY": 0,
    "SECURITY_DELAY": 0,
    "LATE_AIRCRAFT_DELAY": 0
}, inplace=True)

# Sidebar filters
st.sidebar.header("Filters")
carrier_filter = st.sidebar.multiselect(
    "Select Carrier(s)",
    options=data["OP_CARRIER"].unique(),
    default=data["OP_CARRIER"].unique()
)
origin_filter = st.sidebar.multiselect(
    "Select Origin Airport(s)",
    options=data["ORIGIN"].unique(),
    default=data["ORIGIN"].unique()
)

# Filter data based on selections
filtered_data = data[(
    data["OP_CARRIER"].isin(carrier_filter)) & 
    (data["ORIGIN"].isin(origin_filter)) &
    (data["DEST"].isin(origin_filter))
]
st.markdown("---")

# Display filtered data
st.markdown("### Data Table")
st.dataframe(filtered_data)

# Merge airport data to get state information for origins only
airports_dict = airports_data.set_index("IATA")[["STATE"]].to_dict()["STATE"]
filtered_data["ORIGIN_STATE"] = filtered_data["ORIGIN"].map(airports_dict)
filtered_data["DEST_STATE"] = filtered_data["DEST"].map(airports_dict)

# Aggregate data by state for origins only
origin_state_data = filtered_data["ORIGIN_STATE"].value_counts().reset_index()
origin_state_data.columns = ["State", "Origin Count"]

# Aggregate data by state for destinations
destination_state_data = filtered_data["DEST_STATE"].value_counts().reset_index()
destination_state_data.columns = ["State", "Destination Count"]

# Count number of airports in each state
state_airport_count = airports_data.groupby("STATE").size().reset_index(name="Airport Count")

# Merge airport count into the state data for visualization
origin_state_data = origin_state_data.merge(state_airport_count, left_on="State", right_on="STATE", how="left")

# Merge airport count into the destination state data
destination_state_data = destination_state_data.merge(state_airport_count, left_on="State", right_on="STATE", how="left")

st.markdown("---")
# Visualization 1: Bar Chart of Number of Airports in Each State
st.subheader("Bar Chart")

# Create bar chart to show number of airports by state
fig0 = px.bar(
    state_airport_count,
    x="STATE",
    y="Airport Count",
    labels={"STATE": "State", "Airport Count": "Number of Airports"},
    title="Number of Airports in Each State",
    color="Airport Count",
    color_continuous_scale="Viridis",
)

# Customize the layout for the bar chart
fig0.update_layout(
    xaxis_title="State",
    yaxis_title="Number of Airports",
    xaxis_tickangle=-45,
    height=600
)

# Show the bar chart
st.plotly_chart(fig0)

st.markdown("---")

# Visualization 1: Geo Heatmap of Flight Origins by State
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

# Visualization: Sunburst Chart of Flight Destinations by State and Airport
st.subheader("Sunburst Chart")
destination_airport_data = filtered_data.groupby(["DEST_STATE", "DEST"]).size().reset_index(name="Destination Count")

fig = px.sunburst(
    destination_airport_data,
    path=["DEST_STATE", "DEST"],
    values="Destination Count",
    title="Flight Destinations Breakdown by State and Airport",
    color="Destination Count",
    color_continuous_scale="Viridis",
)
st.plotly_chart(fig)

st.markdown("---")
# Visualization 2: Delays by Carrier
st.subheader("Bar Chart")
carrier_delays = filtered_data.groupby("OP_CARRIER")[["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]].mean().reset_index()

fig2 = px.bar(
    carrier_delays,
    x="OP_CARRIER",
    y=["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"],
    title="Average Delays by Carrier",
    labels={"value": "Average Delay (minutes)", "variable": "Delay Type"},
    barmode="group",
    template="plotly_white"
)
st.plotly_chart(fig2)

st.markdown("---")
# Visualization 3: Cancellations by Reason
st.subheader("Pie Chart")
cancellation_reasons = filtered_data["CANCELLATION_CODE"].value_counts().reset_index()
cancellation_reasons.columns = ["Reason", "Count"]

fig3 = px.pie(
    cancellation_reasons,
    names="Reason",
    values="Count",
    title="Flight Cancellations by Reason",
    hole=0.4,
    template="plotly_white"
)
st.plotly_chart(fig3)

st.markdown("---")
# Visualization 4: Delay Distribution by Airport
st.subheader("Bar Chart")
delay_data = filtered_data.groupby("ORIGIN")["DEP_DELAY"].mean().reset_index()
delay_data.columns = ["Airport", "Average Departure Delay"]

fig4 = px.bar(
    delay_data,
    x="Airport",
    y="Average Departure Delay",
    title="Average Departure Delays by Airport",
    labels={"Average Departure Delay": "Delay (minutes)", "Airport": "Origin Airport"},
    template="plotly_white"
)
st.plotly_chart(fig4)

st.markdown("---")
# Visualization 5: Distance vs. Delay Scatter Plot
st.subheader("Scatter Plot")
fig5 = px.scatter(
    filtered_data,
    x="DISTANCE",
    y="ARR_DELAY",
    color="OP_CARRIER",
    title="Distance vs. Arrival Delay",
    labels={"DISTANCE": "Distance (miles)", "ARR_DELAY": "Arrival Delay (minutes)", "OP_CARRIER": "Carrier"},
    hover_data=["ORIGIN", "DEST"],
    template="plotly_dark"
)
st.plotly_chart(fig5)

st.markdown("---")
#Visualization fig 6
# Fill missing arrival delays with 0
data['ARR_DELAY'] = data['ARR_DELAY'].fillna(0)

# Handle negative arrival delays (either set to 0 or take absolute values)
data['ARR_DELAY'] = data['ARR_DELAY'].apply(lambda x: max(0, x))  # Replace negative delays with 0

# Merge airport data with your flight data
data = data.merge(airports_data[['IATA', 'LATITUDE', 'LONGITUDE']], how='left', left_on='ORIGIN', right_on='IATA')

# Rename LATITUDE and LONGITUDE to lat and lon for Plotly
data.rename(columns={'LATITUDE': 'lat', 'LONGITUDE': 'lon'}, inplace=True)

# Aggregate data by airport (origin) for average arrival delay
airport_delay_data = data.groupby(['ORIGIN', 'lat', 'lon'])['ARR_DELAY'].mean().reset_index()
st.subheader("Bubble Map")
# Create a bubble map using Plotly
fig6 = px.scatter_geo(
    airport_delay_data,
    lat='lat',  # Use 'lat' for the airport location
    lon='lon',  # Use 'lon' for the airport location
    size='ARR_DELAY',  # Size of bubbles based on arrival delay
    hover_name='ORIGIN',  # Show airport IATA code on hover
    size_max=10,  # Maximum bubble size
    color='ARR_DELAY',  # Color based on arrival delay
    color_continuous_scale='Viridis',  # Color scale
    title='Bubble Map of Arrival Delays by Airport in the US',
    template='plotly_white',  # Dark template for contrast
)

# Update layout for better fit and appearance
fig6.update_geos(
    scope='usa',
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    bgcolor='rgba(0,0,0,0)',
)
# Update layout to remove white background and increase map width
fig6.update_layout(
    width=1200,
    height=600 
)

# Display the map
st.plotly_chart(fig6)
st.markdown("---")