# app.py

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Pro Annotation Tool", page_icon="📝", layout="wide")

# --- 🔐 Password Protection ---
PASSWORDS = {
    "tianyang": "annotations/annotator_1.csv",
    "pracha": "annotations/annotator_2.csv",
    "andy": "annotations/annotator_3.csv",
}

# --- Login & Logout Logic ---


def login():
    st.header("Annotator Login")
    password = st.text_input("Enter your password:", type="password")
    if st.button("Login"):
        if password in PASSWORDS:
            st.session_state["logged_in"] = True
            st.session_state["annotator_file"] = PASSWORDS[password]
            st.session_state["current_index"] = 0
            st.rerun()
        else:
            st.error("Incorrect password.")


def logout():
    st.session_state["logged_in"] = False
    st.session_state.pop("annotator_file", None)
    st.session_state.pop("current_index", None)
    st.rerun()


# --- Main Annotation Interface ---


def main_app():
    annotation_file_path = Path(st.session_state["annotator_file"])

    try:
        df = pd.read_csv(annotation_file_path)
    except FileNotFoundError:
        st.error(f"Error: Annotation file '{annotation_file_path}' not found.")
        st.stop()

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    current_index = st.session_state.current_index
    current_annotation = df.loc[current_index, "annotation"]
    total_items = len(df)

    # --- 🕹️ Sidebar Controls ---
    with st.sidebar:
        st.title("Controls")
        st.write(f"File: `{annotation_file_path.name}`")
        if st.button("Logout"):
            logout()

        st.write("---")

        annotated_count = df["annotation"].notna().sum()
        progress = annotated_count / total_items
        st.metric(
            label="Annotation Progress", value=f"{annotated_count} / {total_items}"
        )
        st.progress(progress)

        st.write("---")

        st.subheader("Navigation")
        prev_col, next_col = st.columns(2)
        if prev_col.button("⬅️ Previous", use_container_width=True):
            if current_index > 0:
                st.session_state.current_index -= 1
                st.rerun()

        if next_col.button("Next ➡️", use_container_width=True):
            if current_index < total_items - 1:
                st.session_state.current_index += 1
                st.rerun()

        st.write("---")

        st.subheader("Current Item Status")
        if pd.notna(current_annotation):
            st.success(f"✅ Annotated as: **{current_annotation}**")
            if st.button("🗑️ Clear Annotation", use_container_width=True):
                df.loc[current_index, "annotation"] = np.nan
                df.to_csv(annotation_file_path, index=False)
                st.toast("Annotation cleared!")
                st.rerun()
        else:
            st.warning("🟡 Not annotated yet.")

    # --- Main Content ---
    st.title("📝 Text Annotation Tool")

    current_item = df.iloc[current_index]
    file_path = Path(current_item["file_path"])

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("🔑 Metadata")
        metadata_path = file_path.parent / "metadata.json"
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            st.metric(label="ID", value=metadata.get("id", "N/A"))
            st.metric(label="Diagram Type", value=metadata.get("diagram_type", "N/A"))
            st.subheader("User Query")
            st.markdown(f"> {metadata.get('user_query', 'No query provided.')}")
        except FileNotFoundError:
            st.warning("Metadata file not found.")

    with col2:
        st.header(f"Text to Annotate ({current_index + 1}/{total_items})")
        try:
            text_content = file_path.read_text()
            with st.container(border=True):
                st.markdown(text_content, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("Text file not found.")
            st.stop()

    st.write("---")
    st.subheader("Is this text description natural?")
    button_cols = st.columns([1, 1, 5])

    def annotate(annotation_value):
        df.loc[current_index, "annotation"] = annotation_value
        df.to_csv(annotation_file_path, index=False)
        st.toast(f"Saved as '{annotation_value}'!")
        if current_index < total_items - 1:
            st.session_state.current_index += 1
        st.rerun()

    # --- 🔘 Button Highlighting Logic ---
    # Determine button type based on the current item's annotation
    natural_button_type = "primary" if current_annotation == "Natural" else "secondary"
    not_natural_button_type = (
        "primary" if current_annotation == "Not Natural" else "secondary"
    )

    if button_cols[0].button(
        "👍 Natural", use_container_width=True, type=natural_button_type
    ):
        annotate("Natural")

    if button_cols[1].button(
        "👎 Not Natural", use_container_width=True, type=not_natural_button_type
    ):
        annotate("Not Natural")


# --- App Entry Point ---
if st.session_state.get("logged_in", False):
    main_app()
else:
    login()
