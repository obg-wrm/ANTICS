import os.path
import pandas as pd


# Example usage
folder_path = r'D:\mojmas\files\data\hologram\station_02'

metadata_csv = os.path.join(folder_path, "metadata_overview.csv")
output_csv = os.path.join(folder_path, "filtered_metadata.csv")

metadata_df = pd.read_csv(metadata_csv)

df_sorted = metadata_df.sort_values(by="Image").reset_index(drop=True)

# Apply a rolling average to smooth depth data
df_sorted['Smoothed_Depth'] = df_sorted['Depth'].rolling(window=5, center=True, min_periods=1).mean()

# Initialize variables for phase tracking
current_phase = "Initial"
phases = []

# ignores minor depth changes caused by sensor inaccuracies.
tolerance = 0.15  # Set a tolerance to handle minor sensor fluctuations

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

filtered_data = filtered_data[filtered_data["Smoothed_Depth"] >= 5].reset_index(drop=True)


filtered_data.to_csv(output_csv, index=False)
print(f"Filtered data saved to: {output_csv}")

