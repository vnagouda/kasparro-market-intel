
import json, os, traceback, pandas as pd, streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title='Kasparro Market Intelligence', layout='wide')
st.title('📊 Kasparro — AI-Powered Market Intelligence')

# ---------- Helpers ----------
def load_json(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f'File not found: {path}')
    except json.JSONDecodeError as e:
        st.error(f'JSON parse error in {path}: {e}')
        with st.expander("Details"):
            st.code(traceback.format_exc())
    except Exception as e:
        st.error(f'Unexpected error loading {path}: {e}')
        with st.expander("Details"):
            st.code(traceback.format_exc())
    return {}

def load_csv(path: str):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error(f'File not found: {path}')
    except Exception as e:
        st.error(f'Error loading CSV {path}: {e}')
        with st.expander("Details"):
            st.code(traceback.format_exc())
    return pd.DataFrame()

def safe_dataframe(df: pd.DataFrame, *, fallback_msg: str):
    try:
        if df is None or df.empty:
            st.info(fallback_msg)
        else:
            st.dataframe(df)
    except Exception as e:
        st.error(f'Failed to display table: {e}')
        with st.expander("Details"):
            st.code(traceback.format_exc())

def safe_image(path: str, caption: str):
    try:
        if os.path.exists(path):
            st.image(path, caption=caption, use_column_width=True)
        else:
            st.info(f'Image not found: {path}')
    except Exception as e:
        st.error(f'Failed to render image {path}: {e}')
        with st.expander("Details"):
            st.code(traceback.format_exc())

def validate_insights_schema(ins: dict) -> dict:
    
    #Return a normalized insights dict and report any issues.
   
    issues = []
    if not isinstance(ins, dict):
        issues.append("insights.json is not an object")
        ins = {}
    if "top_categories" not in ins or not isinstance(ins.get("top_categories"), list):
        issues.append("Missing or invalid 'top_categories' (expected list)")
        ins["top_categories"] = []
    if "llm_summary" not in ins or not isinstance(ins.get("llm_summary"), str):
        issues.append("Missing or invalid 'llm_summary' (expected string)")
        ins["llm_summary"] = ""
    # Optional structured block
    if "llm_structured" in ins and not isinstance(ins.get("llm_structured"), dict):
        issues.append("Invalid 'llm_structured' (expected object)")
        ins["llm_structured"] = None
    if issues:
        with st.expander("Insights schema notes"):
            for i in issues:
                st.write("•", i)
    return ins


def safe_bar_chart_top_categories(top_df: pd.DataFrame):
    try:
        if top_df is None or top_df.empty:
            st.info("No top categories available to plot.")
            return
        required = {"primary_category", "opportunity_score"}
        if not required.issubset(set(map(str, top_df.columns))):
            st.info("Plot skipped: 'primary_category' or 'opportunity_score' not found.")
            return
        # Plot
        sorted_df = top_df.sort_values("opportunity_score", ascending=True)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(sorted_df["primary_category"], sorted_df["opportunity_score"])
        ax.set_title("Top Categories by Opportunity Score")
        ax.set_xlabel("Opportunity Score")
        ax.set_ylabel("Category")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Could not render chart: {e}")
        with st.expander("Details"):
            st.code(traceback.format_exc())

# ---------- Load artifacts (guarded) ----------
ins = load_json('insights.json')
df  = load_csv('combined_apps.csv')
ins = validate_insights_schema(ins)

# ---------- Sidebar (downloads) ----------
with st.sidebar:
    st.header("Artifacts")
    for path, label in [
        ("insights.json", "insights.json"),
        ("combined_apps.csv", "combined_apps.csv"),
        ("top_categories.png", "top_categories.png"),
        ("report.html", "report.html"),
    ]:
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(label=f"Download {label}", data=f, file_name=label)
            else:
                st.caption(f"Missing: {label}")
        except Exception as e:
            st.caption(f"Download error: {label}")
            with st.expander(f"Details: {label}"):
                st.code(str(e))

# ---------- Executive Summary ----------
st.subheader('Executive Recommendations')
try:
    summary = ins.get('llm_summary') or ""
    if summary.strip():
        st.write(summary)
    else:
        st.info('No LLM summary found. Re-run the notebook to generate insights.')
except Exception as e:
    st.error(f"Failed to render executive recommendations: {e}")
    with st.expander("Details"):
        st.code(traceback.format_exc())

# ---------- Structured Recommendations (bonus) ----------
st.subheader("Structured Recommendations (JSON)")
try:
    llm_struct = ins.get("llm_structured")
    if llm_struct and isinstance(llm_struct, dict) and "recommendations" in llm_struct:
        safe_dataframe(pd.DataFrame(llm_struct["recommendations"]),
                       fallback_msg="Structured recommendations present but empty.")
    else:
        st.info("No structured recommendations found. Re-run the notebook to regenerate insights.")
except Exception as e:
    st.error(f"Failed to render structured recommendations: {e}")
    with st.expander("Details"):
        st.code(traceback.format_exc())

# ---------- Top Categories ----------
st.subheader('Top Categories by Opportunity Score')
try:
    top_cats = pd.DataFrame(ins.get('top_categories', []))
    safe_dataframe(top_cats, fallback_msg='Top categories not available in insights.json.')
except Exception as e:
    st.error(f"Failed to render top categories: {e}")
    with st.expander("Details"):
        st.code(traceback.format_exc())

# ---------- Visualization (image + safe plot) ----------
st.subheader('Visualization')
safe_image('top_categories.png', caption='Top Categories by Opportunity Score')
st.caption("If the image is missing or outdated, the plot below is generated directly from insights.json:")
try:
    top_cats = pd.DataFrame(ins.get('top_categories', []))
    safe_bar_chart_top_categories(top_cats)
except Exception as e:
    st.error(f"Failed to plot top categories: {e}")
    with st.expander("Details"):
        st.code(traceback.format_exc())

# ---------- Dataset Browser ----------
st.subheader('Browse Combined Dataset')
try:
    safe_dataframe(df.head(200) if not df.empty else df,
                   fallback_msg='combined_apps.csv is empty or missing.')
except Exception as e:
    st.error(f"Failed to display dataset: {e}")
    with st.expander("Details"):
        st.code(traceback.format_exc())

# ---------- Footer ----------
st.markdown('---')
st.caption(f"Generated at: {ins.get('generated_at_utc', 'N/A')}")
