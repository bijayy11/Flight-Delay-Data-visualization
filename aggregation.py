import os
import pandas as pd

# Define the input and output directories
input_dir = "datasets/archive/"  # Folder containing all CSV files
output_base_dir = "../datasets/AGG_Datasets/"  # Base directory to save the yearly outputs

# Fill values for missing data
fill_values = {
    "CANCELLATION_CODE": "None",
    "CARRIER_DELAY": 0,
    "WEATHER_DELAY": 0,
    "NAS_DELAY": 0,
    "SECURITY_DELAY": 0,
    "LATE_AIRCRAFT_DELAY": 0,
    "TAXI_IN": 0,
    "TAXI_OUT": 0
}

# Load auxiliary airport data
airports_file = "datasets/airports.csv"
airports = pd.read_csv(airports_file)
airports = airports[['IATA', 'STATE', 'LATITUDE', 'LONGITUDE']]
airports_dict = airports.set_index("IATA")

# Function to process and aggregate data for a single year
def process_yearly_data(file_path, year):
    print(f"Processing {year} data from {file_path}")
    data = pd.read_csv(file_path)
    
    # Fill missing values
    data.fillna(fill_values, inplace=True)
    
    # Convert date column to datetime
    data['FL_DATE'] = pd.to_datetime(data['FL_DATE'])
    data['Month'] = data['FL_DATE'].dt.to_period('M')
    data['Hour'] = data['CRS_DEP_TIME'] // 100
    
    # Map state and geographic information to the flight data
    data["ORIGIN_STATE"] = data["ORIGIN"].map(airports_dict["STATE"])
    data["DEST_STATE"] = data["DEST"].map(airports_dict["STATE"])
    data["LATITUDE"] = data["ORIGIN"].map(airports_dict["LATITUDE"])
    data["LONGITUDE"] = data["ORIGIN"].map(airports_dict["LONGITUDE"])
    
    # Generate aggregated datasets
    carrier_delays = data.groupby("OP_CARRIER")[
        ["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]
    ].mean().reset_index()

    monthly_aggregates = data.groupby('Month')[['DEP_DELAY', 'ARR_DELAY', 'CANCELLED']].mean().reset_index()

    state_flight_counts = data.groupby("ORIGIN_STATE").size().reset_index(name="Flight Count")

    # Map state information to the dataset for both origin and destination airports
    origin_dest_counts = data.groupby(["ORIGIN", "DEST"]).size().reset_index(name="Flight Count")

    # Map state information from the airports dictionary
    origin_dest_counts["ORIGIN_STATE"] = origin_dest_counts["ORIGIN"].map(airports_dict["STATE"])
    origin_dest_counts["DEST_STATE"] = origin_dest_counts["DEST"].map(airports_dict["STATE"])


    airport_delays = data.groupby("ORIGIN")["DEP_DELAY"].mean().reset_index(name="Average Departure Delay")

    daily_delay_trend = data.groupby(data['FL_DATE'].dt.date)['ARR_DELAY'].mean().reset_index(name="Average Arrival Delay")

    cancellation_reasons = data["CANCELLATION_CODE"].value_counts().reset_index()
    cancellation_reasons.columns = ["Reason", "Count"]

    distance_vs_delay = data.groupby(["DISTANCE", "ARR_DELAY", "OP_CARRIER"]).size().reset_index(name="Count")

    airport_bubble_map = data.groupby(['ORIGIN', 'LATITUDE', 'LONGITUDE'])['ARR_DELAY'].mean().reset_index(name="Average Arrival Delay")

    departure_delay_by_hour = data.groupby("Hour")["DEP_DELAY"].mean().reset_index(name="Average Departure Delay")

    cancellation_percentage_by_carrier = data.groupby("OP_CARRIER")["CANCELLED"].mean().reset_index(name="Cancellation Rate")

    airlines_most_delays = data.groupby("OP_CARRIER")["ARR_DELAY"].mean().reset_index().sort_values("ARR_DELAY", ascending=False)

    taxi_times = data.groupby("OP_CARRIER")[["TAXI_IN", "TAXI_OUT"]].mean().reset_index()
    taxi_hourly = data.groupby("Hour")[["TAXI_IN", "TAXI_OUT"]].mean().reset_index()

    state_airport_count = airports.groupby("STATE").size().reset_index(name="Airport Count")

    origin_state_data = data["ORIGIN_STATE"].value_counts().reset_index()
    origin_state_data.columns = ["State", "Origin Count"]
    origin_state_data = origin_state_data.merge(state_airport_count, left_on="State", right_on="STATE", how="left")

    destination_state_data = data["DEST_STATE"].value_counts().reset_index()
    destination_state_data.columns = ["State", "Destination Count"]
    destination_state_data = destination_state_data.merge(state_airport_count, left_on="State", right_on="STATE", how="left")

    # Define all datasets to be saved
    all_datasets = {
        "carrier_delays": carrier_delays,
        "monthly_aggregates": monthly_aggregates,
        "state_flight_counts": state_flight_counts,
        "origin_dest_counts": origin_dest_counts,
        "airport_delays": airport_delays,
        "daily_delay_trend": daily_delay_trend,
        "cancellation_reasons": cancellation_reasons,
        "distance_vs_delay": distance_vs_delay,
        "airport_bubble_map": airport_bubble_map,
        "departure_delay_by_hour": departure_delay_by_hour,
        "cancellation_percentage_by_carrier": cancellation_percentage_by_carrier,
        "airlines_most_delays": airlines_most_delays,
        "state_airport_count": state_airport_count,
        "origin_state_data": origin_state_data,
        "destination_state_data": destination_state_data,
        "taxi_times": taxi_times,
        "taxi_hourly": taxi_hourly
    }
    
    # Create the output directory for the year
    output_dir = os.path.join(output_base_dir, str(year))
    os.makedirs(output_dir, exist_ok=True)
    
    # Save all datasets to CSV files
    for name, df in all_datasets.items():
        output_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved {name} to {output_path}")

# Process each file in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith(".csv"):
        year = file_name.split('.')[0]  # Extract the year from the file name
        file_path = os.path.join(input_dir, file_name)
        process_yearly_data(file_path, year)