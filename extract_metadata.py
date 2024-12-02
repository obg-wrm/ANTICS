from pathlib import Path
import pandas as pd
from LISST_Holo_tools import HoloMetadata


def extract_metadata_and_save(folder_path):
    """
    Reads a folder path, extracts metadata from LISST-Holo holograms using HoloMetadata class,
    and saves the metadata as a CSV file in the same folder.
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path}")

    output_file = folder / "metadata_overview.csv"
    metadata_records = []

    for image_file in folder.glob("*.pgm"):
        try:
            metadata = HoloMetadata(str(image_file))
            metadata_records.append(metadata.metadata)
        except Exception as e:
            print(f"Failed to process {image_file}: {e}")

    if metadata_records:
        df = pd.DataFrame(metadata_records, columns=metadata.var_name)
        df.to_csv(output_file, index=False)
        print(f"Metadata saved to: {output_file}")
    else:
        print("No valid hologram files found.")


if __name__ == "__main__":
    # folder_path = input("Enter the path to the folder containing LISST-Holo holograms: ")
    folder_path = r'D:\mojmas\files\data\hologram\station_02'
    try:
        extract_metadata_and_save(folder_path)
    except Exception as e:
        print(f"An error occurred: {e}")
