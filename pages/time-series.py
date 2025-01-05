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
    st.subheader("🌟 Average Departure Delay by Origin (Interactive & Intuitive)")

    # Aggregate data into a pivot table
    delay_pivot = data.pivot_table(
        index="ORIGIN",
        columns="Year",
        values="Average Departure Delay",
        aggfunc="mean",
        fill_value=0
    )

    # Melt the pivot table for easier visualization
    delay_melted = delay_pivot.reset_index().melt(
        id_vars="ORIGIN", var_name="Year", value_name="Average Delay"
    )

    # Replace negative delays with 0 (or handle separately if necessary)
    delay_melted["Average Delay"] = delay_melted["Average Delay"].clip(lower=0)

    # Filterable Year Selector
    years = sorted(delay_melted["Year"].unique())
    selected_year = st.slider("Select Year for Visualization", min_value=years[0], max_value=years[-1], value=years[0])

    # Filter data by selected year
    filtered_data = delay_melted[delay_melted["Year"] == selected_year]

    # Create a dynamic bar chart for the selected year
    fig = px.bar(
        filtered_data.sort_values("Average Delay", ascending=False).head(10),
        x="Average Delay",
        y="ORIGIN",
        orientation="h",
        color="Average Delay",
        title=f"Top 10 Origins by Average Departure Delay ({selected_year})",
        labels={"ORIGIN": "Airport Origin", "Average Delay": "Avg Delay (minutes)"},
        color_continuous_scale="Viridis",
        template="plotly_dark",  # Dark theme for the plot
    )

    # Update layout for improved readability
    fig.update_layout(
        xaxis_title="Average Delay (minutes)",
        yaxis_title="Airport Origin",
        coloraxis_colorbar=dict(title="Avg Delay (mins)", len=0.5),
        title_font=dict(size=24),
        font=dict(color="white"),  # Ensure text is visible on dark background
        paper_bgcolor="#222222",  # Dark background for the whole chart
        plot_bgcolor="#222222",  # Dark plot area background
        height=600,
    )

    # Display the chart with Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Add dynamic storytelling: Show trends over all years for the selected origin
    st.subheader(f"Yearly Trends for Top Delayed Airports ({selected_year})")
    selected_airport = st.selectbox("Select an Airport Origin", options=filtered_data["ORIGIN"].unique())

    airport_trend = delay_melted[delay_melted["ORIGIN"] == selected_airport]

    # Line chart for trends over years
    trend_fig = px.line(
        airport_trend,
        x="Year",
        y="Average Delay",
        title=f"Yearly Average Departure Delay for {selected_airport}",
        labels={"Year": "Year", "Average Delay": "Avg Delay (minutes)"},
        template="plotly_dark",  # Dark theme for the plot
        markers=True,
    )

    trend_fig.update_traces(line=dict(color="cyan", width=3), marker=dict(size=8))

    trend_fig.update_layout(
        xaxis=dict(title="Year", tickmode="linear", dtick=1),
        yaxis=dict(title="Avg Delay (minutes)"),
        title_font=dict(size=22),
        font=dict(color="white"),  # Ensure text is visible
        paper_bgcolor="#222222",  # Dark background
        plot_bgcolor="#222222",  # Dark plot area background
        height=400,
    )

    st.plotly_chart(trend_fig, use_container_width=True)



elif metric_selection == "Carrier Delays by Type":
    st.subheader("📊 Carrier Delays by Type")
    
    # Delay types for reshaping data
    delay_types = ["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]
    
    # Reshape the data
    delay_data = data.melt(
        id_vars=["OP_CARRIER", "Year"],
        value_vars=delay_types,
        var_name="Delay Type",
        value_name="Delay (minutes)"
    )
    
    # Create the stacked area chart using Plotly
    fig = px.area(
        delay_data,
        x="Year",
        y="Delay (minutes)",
        color="Delay Type",  # Differentiate delay types by color
        line_group="OP_CARRIER",  # Group by carrier to see trends
        title="Carrier Delays by Type (2009-2018)",
        labels={"Year": "Year", "Delay Type": "Type of Delay", "Delay (minutes)": "Delay Duration (minutes)"},
        template="plotly_dark",  # Dark theme for modern look
        height=500
    )

    # Update layout for better clarity
    fig.update_layout(
        title_x=0.5,  # Center the title
        title_font=dict(size=18, color='white'),
        xaxis_title="Year",
        yaxis_title="Delay Duration (minutes)",
        legend_title="Delay Type",
        plot_bgcolor="black",  # Dark background
        paper_bgcolor="black",
        margin=dict(t=50, b=50, l=50, r=50),  # Adjust margins for readability
        xaxis=dict(tickmode="linear", tick0=2009, dtick=1),  # Show yearly ticks
    )
    
    # Render the chart
    st.plotly_chart(fig, use_container_width=True)


elif metric_selection == "Average Departure Delay (by Hour)":
    st.subheader("🕒 Average Departure Delay by Hour")
    fig = px.line(
    data,
    x="Hour",
    y="Average Departure Delay",
    color="Year",  # Each year gets a separate line and color
    title="Average Departure Delay by Hour (2009-2018)",
    labels={
        "Hour": "Hour of the Day",
        "Average Departure Delay": "Delay (minutes)",
        "Year": "Year"
    },
    template="plotly_dark",
    line_shape="spline"
    )
    
    # Enhance visual design: update line styles and markers
    fig.update_traces(mode="lines+markers", marker=dict(size=7))
    
    # Update legend to appear on the right-hand side
    fig.update_layout(
        legend=dict(
            title="Year",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05  # Adjust position of the legend
        )
    )
    
    # Render the chart
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Average Taxi Time (Hourly)":
    st.subheader("🚖 Average Taxi Time by Hour")

    # Calculate Average Taxi Time
    data['Average Taxi Time'] = data[['TAXI_IN', 'TAXI_OUT']].mean(axis=1)
    
    # Plot the line chart with grouping by Year
    fig = px.line(
        data,
        x="Hour",
        y="Average Taxi Time",
        color="Year",  # Different color for each year
        title="Average Taxi Time by Hour (2009-2018)",
        labels={
            "Hour": "Hour of the Day",
            "Average Taxi Time": "Taxi Time (minutes)",
            "Year": "Year"
        },
        template="plotly_dark",
        line_shape="spline"  # Smooth lines
    )

    # Enhance the visualization
    fig.update_traces(mode="lines+markers", marker=dict(size=6))  # Add markers to lines
    fig.update_layout(
        legend=dict(
            title="Year",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05  # Position the legend on the right
        ),
        xaxis=dict(tickmode="linear", tick0=0, dtick=1)  # Ensure all hours are displayed
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

elif metric_selection == "Flight Count by State":
    st.subheader("🌍 Year-over-Year Flight Count Change by State (Button Navigation)")

    # Group the data by year and state, and sum the flight counts
    yearly_data = data.groupby(['Year', 'ORIGIN_STATE'])['Flight Count'].sum().reset_index()

    # Calculate Year-over-Year (YoY) change for each state
    yearly_data['Flight Count Change'] = yearly_data.groupby('ORIGIN_STATE')['Flight Count'].diff()

    # Classify the change into positive, negative, or constant categories
    def change_category(change):
        if change > 0:
            return 'Positive Change'
        elif change < 0:
            return 'Negative Change'
        else:
            return 'Constant Change'
    
    yearly_data['Change Category'] = yearly_data['Flight Count Change'].apply(change_category)
    
    # Create year-to-year transitions (2009-2010, 2010-2011, ...)
    year_pairs = [(year, year + 1) for year in range(2009, 2018)]

    # Create a button for each year transition
    year_transition = st.selectbox("Select Year Transition (e.g., 2009-2010):", [f"{year}-{year + 1}" for year, _ in year_pairs])

    # Extract the selected year range
    start_year, end_year = map(int, year_transition.split('-'))

    # Filter the data for the selected year range
    selected_year_data = yearly_data[
        (yearly_data['Year'] == start_year) | (yearly_data['Year'] == end_year)
    ]

    # Create the choropleth map for the selected year-to-year transition
    fig = px.choropleth(
        selected_year_data,
        locations="ORIGIN_STATE",
        locationmode="USA-states",
        color="Change Category",
        scope="usa",
        title=f"Flight Count Change from {start_year} to {end_year}",
        labels={"Change Category": "Change in Flight Count"},
        color_discrete_map={
            'Positive Change': 'green',  # Positive change in green
            'Negative Change': 'red',    # Negative change in red
            'Constant Change': 'gray'    # Constant change in gray
        },
        template="plotly_dark",  # Dark background for modern look
        hover_name="ORIGIN_STATE",  # Show state name on hover
        hover_data=["Flight Count Change", "Change Category"],  # Show change details on hover
        width=800,
        height=600
    )

    # Customize the map layout
    fig.update_layout(
        geo=dict(
            showcoastlines=True,  # Show coastlines
            coastlinecolor="Black",  # Make coastline black for contrast
            projection_type="albers usa",  # Adjust map projection for better visibility of US states
            showland=True,
            landcolor="gray",  # Background color of land to make states stand out
        ),
        title_x=0.5,  # Center the title
        title_font=dict(size=18, color='white'),
        paper_bgcolor="black",  # Dark background for consistency
        plot_bgcolor="black",  # Dark plot background for consistency
        margin={"r":0,"t":50,"l":0,"b":0}  # Remove extra margins
    )

    # Render the choropleth map for the selected year transition
    st.plotly_chart(fig, use_container_width=True)


elif metric_selection == "Top Flight Routes by Count":
    st.subheader("📍 Top 10 Flight Routes by Count")
    
    # Group by origin and destination and get top 10 by flight count
    top_routes = data.groupby(['ORIGIN', 'DEST']).sum().reset_index().nlargest(10, 'Flight Count')
    
    # Create the treemap using Plotly
    fig = px.treemap(
        top_routes,
        path=['ORIGIN', 'DEST'],  # Hierarchical path (Origin -> Destination)
        values='Flight Count',  # Size of each rectangle
        title="Top 10 Flight Routes by Count (2009-2018)",
        labels={"Flight Count": "Number of Flights", "ORIGIN": "Origin", "DEST": "Destination"},
        template="plotly_dark",  # Dark template for a modern look
        color='Flight Count',  # Color based on the number of flights
        color_continuous_scale="Viridis"  # Color gradient for better distinction
    )

    # Update layout for better readability
    fig.update_layout(
        title_x=0.5,  # Center the title
        title_font=dict(size=18, color='white'),
        margin=dict(t=50, b=50, l=50, r=50),  # Adjust margins for better spacing
        paper_bgcolor="black",  # Black background for modern look
    )

    # Render the treemap
    st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown("---")
st.info("📌 Select different metrics using the dropdown menu above to explore various trends.")
