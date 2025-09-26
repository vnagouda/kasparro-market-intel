
import json
import pandas as pd
import streamlit as st
import os

st.set_page_config(page_title="Kasparro Market Intelligence", layout="wide")
st.title("📊 Kasparro — AI-Powered Market Intelligence")

# Load files
df = pd.read_csv("combined_apps.csv")
ins = json.load(open("insights.json"))

# --- Section 1: Executive Summary ---
st.subheader("Executive Recommendations")
st.write(ins.get("llm_summary", "No summary available."))

# --- Section 2: Top Categories Table ---
st.subheader("Top Categories by Opportunity Score")
top_df = pd.DataFrame(ins["top_categories"])
st.dataframe(top_df)

# --- Section 3: Visualization ---
if os.path.exists("top_categories.png"):
    st.subheader("Visualization")
    st.image("top_categories.png", caption="Top Categories by Opportunity Score")

# --- Section 4: Browse Dataset ---
st.subheader("Browse Combined Dataset")
st.dataframe(df.head(200))

# --- Section 5: Metadata ---
st.markdown("---")
st.caption(f"Generated at: {ins.get('generated_at_utc', 'N/A')}")

