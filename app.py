import streamlit as st
import os
import re
from rapidfuzz import fuzz

# ================= CONFIG =================
TXT_FOLDER = "txt"

PDF_BASE_URL = "https://sakshamo5.github.io/electoral-pdfs"

NAME_THRESHOLD = 80
RELATIVE_THRESHOLD = 80
# =========================================

st.set_page_config(
    page_title="Electoral Roll Search",
    layout="wide"
)

# ---------------- HELPERS ----------------
def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@st.cache_data(show_spinner=False)
def load_all_lines():
    rows = []
    for file in os.listdir(TXT_FOLDER):
        if file.endswith(".txt"):
            path = os.path.join(TXT_FOLDER, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if len(line) > 15:
                        rows.append({
                            "file": file,
                            "line_no": line_no,
                            "raw": line,
                            "norm": normalize(line)
                        })
    return rows


data = load_all_lines()

# ---------------- SESSION STATE ----------------
if "results" not in st.session_state:
    st.session_state.results = []

# ---------------- UI ----------------
st.title("🔍 Electoral Roll Search")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    relative = st.text_input("Relative Name")

# ---------------- SEARCH ----------------
if st.button("Search"):
    if not name or not relative:
        st.warning("Please enter both Name and Relative Name")
    else:
        matches = []

        n_name = normalize(name)
        n_rel = normalize(relative)

        for row in data:
            name_score = fuzz.partial_ratio(n_name, row["norm"])
            rel_score = fuzz.partial_ratio(n_rel, row["norm"])

            if name_score >= NAME_THRESHOLD and rel_score >= RELATIVE_THRESHOLD:
                matches.append({
                    "file": row["file"],
                    "line_no": row["line_no"],
                    "name_score": name_score,
                    "relative_score": rel_score,
                    "text": row["raw"]
                })

        matches.sort(
            key=lambda x: x["name_score"] + x["relative_score"],
            reverse=True
        )

        st.session_state.results = matches

# ---------------- RESULTS ----------------
if st.session_state.results:
    st.success(f"✅ {len(st.session_state.results)} match(es) found")

    for i, r in enumerate(st.session_state.results[:10], 1):
        st.markdown(f"### {i}. Match")

        st.write(f"**File:** {r['file']}")
        st.write(f"**Line No:** {r['line_no']}")
        st.write(f"**Name %:** {r['name_score']}")
        st.write(f"**Relative %:** {r['relative_score']}")
        st.write(r["text"])

        pdf_name = r["file"].replace(".txt", ".pdf")
        pdf_url = f"{PDF_BASE_URL}/{pdf_name}"

        st.link_button("📄 View PDF", pdf_url)

        st.divider()
