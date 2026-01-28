import streamlit as st
import os
import re
from rapidfuzz import fuzz

# ========== CONFIG ==========
TXT_FOLDER = "txt"
NAME_THRESHOLD = 80
RELATIVE_THRESHOLD = 80
# ============================

st.set_page_config(page_title="Fuzzy Name Search", layout="wide")


def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@st.cache_data(show_spinner=False)
def load_all_lines():
    data = []
    for file in os.listdir(TXT_FOLDER):
        if file.endswith(".txt"):
            with open(os.path.join(TXT_FOLDER, file),
                      "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if len(line) > 15:
                        data.append({
                            "file": file,
                            "line_no": line_no,
                            "raw": line,
                            "norm": normalize(line)
                        })
    return data


data = load_all_lines()

# ================= UI =================
st.title("🔍 Fuzzy Name + Relative Search")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Enter Name")
with col2:
    relative = st.text_input("Enter Relative Name")

if st.button("Search"):
    if not name or not relative:
        st.warning("Please enter both Name and Relative Name")
    else:
        results = []

        n_name = normalize(name)
        n_rel = normalize(relative)

        for row in data:
            name_score = fuzz.partial_ratio(n_name, row["norm"])
            rel_score = fuzz.partial_ratio(n_rel, row["norm"])

            if name_score >= NAME_THRESHOLD and rel_score >= RELATIVE_THRESHOLD:
                results.append({
                    "file": row["file"],
                    "line_no": row["line_no"],
                    "name_score": name_score,
                    "relative_score": rel_score,
                    "text": row["raw"]
                })

        results.sort(
            key=lambda x: x["name_score"] + x["relative_score"],
            reverse=True
        )

        if not results:
            st.error("❌ No matches found")
        else:
            st.success(f"✅ {len(results)} match(es) found")

            for i, r in enumerate(results[:10], 1):
                st.markdown(
                    f"""
                    <div style="
                        padding:15px;
                        margin-bottom:15px;
                        border-left:6px solid #1f77b4;
                        box-shadow:0 2px 6px rgba(0,0,0,0.08);
                    ">
                        <b>{i}. File:</b> {r['file']}<br>
                        <b>Line No:</b> {r['line_no']}<br>
                        <b>Name %:</b> {r['name_score']}<br>
                        <b>Relative %:</b> {r['relative_score']}<br><br>
                        {r['text']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
