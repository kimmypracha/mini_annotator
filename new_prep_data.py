# prepare_data.py

import random
from pathlib import Path

import numpy as np
import pandas as pd

# --- Define Paths ---
DATA_ROOT = Path("data")
ANNOTATIONS_DIR = Path("annotations")
NUM_ANNOTATORS = 3

# --- 2. Find and Split Files by Diagram Type ---

print(f"Splitting data by diagram type for {NUM_ANNOTATORS} annotators...")
ANNOTATIONS_DIR.mkdir(exist_ok=True)

# 1. Find all diagram types (the top-level directories in DATA_ROOT)
all_diagram_types = [d.name for d in DATA_ROOT.iterdir() if d.is_dir()]
print(f"Found {len(all_diagram_types)} diagram types: {all_diagram_types}")

# 2. Randomize the list of diagram types
random.shuffle(all_diagram_types)
print(f"Shuffled types: {all_diagram_types}")

# 3. Split the list of *types* among the annotators
# np.array_split handles uneven splits (e.g., 7 types -> [3, 2, 2])
annotator_type_assignments = np.array_split(all_diagram_types, NUM_ANNOTATORS)

# 4. Create a CSV for each annotator based on their assigned types
for i, assigned_types in enumerate(annotator_type_assignments):
    annotator_id = i + 1
    output_path = ANNOTATIONS_DIR / f"annotator_{annotator_id}.csv"

    # Get all files that belong to the assigned diagram types
    annotator_files = []
    for diagram_type in assigned_types:
        type_dir = DATA_ROOT / diagram_type
        # Find all 'task_description.txt' files within this type's directory
        files_for_this_type = list(type_dir.glob("**/task_description.txt"))
        annotator_files.extend(files_for_this_type)

    # Optional: Shuffle the files *within* the annotator's list
    # This prevents them from annotating one full diagram type at a time.
    random.shuffle(annotator_files)

    # Create a DataFrame with the new columns
    df = pd.DataFrame(
        {
            "file_path": [str(p) for p in annotator_files],
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
    print(f"  > Assigned types: {list(assigned_types)}\n")

print("All annotation files created.")
