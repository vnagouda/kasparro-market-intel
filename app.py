
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

if os.path.exists("phase5_d2c_insights.json"):
    st.subheader("📦 Phase 5: D2C Funnel & SEO Insights")

    phase5 = json.load(open("phase5_d2c_insights.json"))
    st.json(phase5, expanded=False)

    if "sample_creatives" in phase5:
        st.subheader("🎨 Sample AI-Generated Creatives")
        st.write("**Ad Headline:**", phase5["sample_creatives"].get("ad_headline"))
        st.write("**SEO Meta:**", phase5["sample_creatives"].get("seo_meta"))
        st.write("**Product Description:**", phase5["sample_creatives"].get("pdp_text"))

