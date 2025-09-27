import random
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

# --- Define Paths ---
ORIGINAL_ROOT = Path("../../AutoDiagEval/experiments/first_dataset/")
DATA_ROOT = Path("data")
ANNOTATIONS_DIR = Path("annotations")

# --- 1. Reset and Prepare Data Directory ---
print(f"Resetting the '{DATA_ROOT}' directory...")

# Remove the existing data directory and its contents, if it exists
if DATA_ROOT.exists():
    shutil.rmtree(DATA_ROOT)

# Create a new, empty data directory
DATA_ROOT.mkdir()

# Find all relevant files in the original source directory
source_files = list(ORIGINAL_ROOT.glob("./*/*/task_description.txt"))
print(f"Found {len(source_files)} file pairs to copy from '{ORIGINAL_ROOT}'.")

# Copy each text file and its corresponding metadata.json
for src_txt_path in source_files:
    # Determine the relative path to preserve the folder structure
    relative_dir = src_txt_path.parent.relative_to(ORIGINAL_ROOT)
    dest_dir = DATA_ROOT / relative_dir

    # Create the destination sub-directory (e.g., data/diagram_1/item_A/)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy the text description file
    shutil.copy2(src_txt_path, dest_dir)

    # Find and copy the corresponding metadata file
    src_metadata_path = src_txt_path.parent / "metadata.json"
    if src_metadata_path.exists():
        shutil.copy2(src_metadata_path, dest_dir)

print("Copy complete.")
print("-" * 20)


# --- 2. Find and Split Files for Annotation ---
# Now, find the files from your clean local data directory
all_files = list(DATA_ROOT.glob("**/*/task_description.txt"))
random.shuffle(all_files)  # Shuffle for random distribution

print(f"Found {len(all_files)} local text files to annotate.")

# Create the annotations directory if it doesn't exist
ANNOTATIONS_DIR.mkdir(exist_ok=True)

# Split the file list into 3 parts
num_annotators = 3
split_files = np.array_split(all_files, num_annotators)

# Create a CSV for each annotator
for i, file_list in enumerate(split_files):
    annotator_id = i + 1
    output_path = ANNOTATIONS_DIR / f"annotator_{annotator_id}.csv"

    # Create a DataFrame to store the annotation tasks
    df = pd.DataFrame(
        {"file_path": [str(p) for p in file_list], "annotation": None, "notes": ""}
    )

    df.to_csv(output_path, index=False)
    print(f"Created {output_path} with {len(df)} files for annotator {annotator_id}.")
