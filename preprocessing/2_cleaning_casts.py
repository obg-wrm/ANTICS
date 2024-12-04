import os
import pandas as pd


def filter_metadata(
    input_csv,
    output_csv,
    rolling_window=5,
    tolerance=0.15,
    depth_threshold=5
):
    """
    Filters metadata to include only Downcasting and Upcasting phases with depth >= threshold.

    Parameters:
    - input_csv (str): Path to the input CSV file.
    - output_csv (str): Path to save the filtered CSV file.
    - rolling_window (int): Window size for rolling mean to smooth depth data.
    - tolerance (float): Tolerance to handle minor sensor fluctuations in depth.
    - depth_threshold (float): Minimum depth value to include in the filtered data.
    """
    # Load metadata CSV
    metadata_df = pd.read_csv(input_csv)

    # Sort the data by Image column
    df_sorted = metadata_df.sort_values(by="Image").reset_index(drop=True)

    # Apply a rolling average to smooth depth data
    df_sorted['Smoothed_Depth'] = df_sorted['Depth'].rolling(
        window=rolling_window, center=True, min_periods=1).mean()

    # Initialize variables for phase tracking
    current_phase = "Initial"
    phases = []

    # Phase determination
    for i in range(len(df_sorted)):
        if i == 0:
            # Start with Phase 1 (Initial)
            current_phase = "Initial"
        else:
            depth_change = df_sorted.loc[i, "Smoothed_Depth"] - df_sorted.loc[i - 1, "Smoothed_Depth"]
            if current_phase == "Initial" and depth_change < -tolerance:
                # Transition from Initial to Phase 2 (Return Phase)
                current_phase = "Return"
            elif current_phase == "Return" and depth_change > tolerance:
                # Transition from Phase 2 (Return) to Phase 3 (Downcasting)
                current_phase = "Downcasting"
            elif current_phase == "Downcasting" and depth_change < -tolerance:
                # Transition from Phase 3 (Downcasting) to Phase 4 (Upcasting)
                current_phase = "Upcasting"

        # Append the current phase to the list
        phases.append(current_phase)

    # Add the phases as a new column in the dataframe
    df_sorted["Phase"] = phases

    # Filter to include only Downcasting (Phase 3) and Upcasting (Phase 4)
    filtered_data = df_sorted[df_sorted["Phase"].isin(["Downcasting", "Upcasting"])].reset_index(drop=True)

    # Further filter to include only data with depth >= threshold
    filtered_data = filtered_data[filtered_data["Smoothed_Depth"] >= depth_threshold].reset_index(drop=True)

    # Save the filtered data to the output CSV
    filtered_data.to_csv(output_csv, index=False)
    print(f"Filtered data saved to: {output_csv}")


# Example usage
folder_path = r'D:\mojmas\files\data\hologram\station_02'
input_csv = os.path.join(folder_path, "metadata_overview.csv")
output_csv = os.path.join(folder_path, "filtered_metadata.csv")

filter_metadata(
    input_csv=input_csv,
    output_csv=output_csv,
    rolling_window=5,      # Smoothing window
    tolerance=0.15,        # Tolerance for sensor fluctuations
    depth_threshold=5      # Depth threshold for filtering
)
