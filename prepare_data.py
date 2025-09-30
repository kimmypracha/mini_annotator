# prepare_data.py

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

if DATA_ROOT.exists():
    shutil.rmtree(DATA_ROOT)
DATA_ROOT.mkdir()

source_files = list(ORIGINAL_ROOT.glob("./*/*/task_description.txt"))
print(f"Found {len(source_files)} file pairs to copy from '{ORIGINAL_ROOT}'.")

for src_txt_path in source_files:
    relative_dir = src_txt_path.parent.relative_to(ORIGINAL_ROOT)
    dest_dir = DATA_ROOT / relative_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_txt_path, dest_dir)
    src_metadata_path = src_txt_path.parent / "metadata.json"
    if src_metadata_path.exists():
        shutil.copy2(src_metadata_path, dest_dir)

print("Copy complete.")
print("-" * 20)

# --- 2. Find and Split Files for Annotation ---
all_files = list(DATA_ROOT.glob("**/*/task_description.txt"))
random.shuffle(all_files)

print(f"Found {len(all_files)} local text files to annotate.")
ANNOTATIONS_DIR.mkdir(exist_ok=True)

num_annotators = 3
split_files = np.array_split(all_files, num_annotators)

for i, file_list in enumerate(split_files):
    annotator_id = i + 1
    output_path = ANNOTATIONS_DIR / f"annotator_{annotator_id}.csv"

    # Create a DataFrame with the new columns
    df = pd.DataFrame(
        {
            "file_path": [str(p) for p in file_list],
            "annotation": None,
            "comment": "",
            "revised_query": "",
            "category": "",
        }
    )

    # Fill NA to ensure consistency
    df.fillna("", inplace=True)

    df.to_csv(output_path, index=False)
    print(f"Created {output_path} with {len(df)} files for annotator {annotator_id}.")
