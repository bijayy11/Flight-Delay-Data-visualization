import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache
def load_sampled_data(file_path, sample_fraction=0.1):
    # Read a random sample of the data (10% in this case)
    data = pd.read_csv(file_path).sample(frac=sample_fraction, random_state=42)
    return data

# Title and Description
st.title("Flight Cancellation Analysis Dashboard")
st.markdown(
    """
    This dashboard provides insights into flight cancellation and delay data. Visualizations include:
    - Geo heatmaps of flight origins and destinations
    - Delay and cancellation statistics
    - Distribution of flight delays by carrier and airports
    """
)

# Load Data
data = load_sampled_data("../Datasets/archive/2009.csv",sample_fraction=0.1)
# Preprocessing
# Replace missing values for better visualization
data.fillna({"CANCELLATION_CODE": "None", "CARRIER_DELAY": 0, "WEATHER_DELAY": 0, "NAS_DELAY": 0, 
            "SECURITY_DELAY": 0, "LATE_AIRCRAFT_DELAY": 0}, inplace=True)

# Sidebar Filters
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

destination_filter = st.sidebar.multiselect(
    "Select Destination Airport(s)",
    options=data["DEST"].unique(),
    default=data["DEST"].unique()
)

# Filter Data Based on Sidebar
filtered_data = data[(data["OP_CARRIER"].isin(carrier_filter)) &
                     (data["ORIGIN"].isin(origin_filter)) &
                     (data["DEST"].isin(destination_filter))]

# Visualization 1: Geo Heatmap for Flight Locations
st.subheader("Geo Heatmap of Flight Locations")

# Create location frequency dataset
location_data = filtered_data["ORIGIN"].value_counts().reset_index()
location_data.columns = ["Airport", "Count"]

fig = px.scatter_geo(
    location_data,
    locations="Airport",
    locationmode="USA-states",
    size="Count",
    title="Flight Origins Geo Heatmap",
    projection="natural earth"
)
st.plotly_chart(fig)

# Visualization 2: Delays by Carrier
st.subheader("Average Delays by Carrier")
carrier_delays = filtered_data.groupby("OP_CARRIER")[
    ["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]
].mean().reset_index()

fig2 = px.bar(
    carrier_delays,
    x="OP_CARRIER",
    y=["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"],
    title="Average Delays by Carrier",
    labels={"value": "Average Delay (minutes)", "variable": "Delay Type"},
    barmode="group"
)
st.plotly_chart(fig2)

# Visualization 3: Cancellations by Reason
st.subheader("Flight Cancellations by Reason")
cancellation_reasons = filtered_data["CANCELLATION_CODE"].value_counts().reset_index()
cancellation_reasons.columns = ["Reason", "Count"]

fig3 = px.pie(
    cancellation_reasons,
    names="Reason",
    values="Count",
    title="Flight Cancellations by Reason",
    hole=0.4
)
st.plotly_chart(fig3)

# Visualization 4: Delay Distribution by Airport
st.subheader("Delay Distribution by Airport")
delay_data = filtered_data.groupby("ORIGIN")["DEP_DELAY"].mean().reset_index()
delay_data.columns = ["Airport", "Average Departure Delay"]

fig4 = px.bar(
    delay_data,
    x="Airport",
    y="Average Departure Delay",
    title="Average Departure Delays by Airport",
    labels={"Average Departure Delay": "Delay (minutes)", "Airport": "Origin Airport"}
)
st.plotly_chart(fig4)

# Visualization 5: Distance vs Delay Scatter Plot
st.subheader("Distance vs. Delay")
fig5 = px.scatter(
    filtered_data,
    x="DISTANCE",
    y="ARR_DELAY",
    color="OP_CARRIER",
    title="Distance vs. Arrival Delay",
    labels={"DISTANCE": "Distance (miles)", "ARR_DELAY": "Arrival Delay (minutes)", "OP_CARRIER": "Carrier"},
    hover_data=["ORIGIN", "DEST"]
)
st.plotly_chart(fig5)

st.markdown("---")
st.markdown("### Data Table")
st.dataframe(filtered_data)
