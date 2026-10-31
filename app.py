import html

import pandas as pd
import streamlit as st

from src.analyser import analyse_dataframe


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Data Health Check",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def rating_icon(rating: str) -> str:
    icons = {
        "EXCELLENT": "🟢",
        "GOOD": "🟢",
        "NEEDS ATTENTION": "🟠",
        "POOR": "🔴",
    }

    return icons.get(rating, "⚪")


def rating_message(rating: str) -> str:
    messages = {
        "EXCELLENT": (
            "This dataset is exceptionally clean. "
            "No significant quality problems were detected."
        ),
        "GOOD": (
            "This dataset is generally healthy, but a few "
            "issues should be reviewed before relying on it."
        ),
        "NEEDS ATTENTION": (
            "Several data-quality issues were detected. "
            "Review the recommendations before using this "
            "dataset for reporting or analysis."
        ),
        "POOR": (
            "Significant data-quality problems were detected. "
            "Cleaning and investigation are recommended before "
            "this dataset is used downstream."
        ),
    }

    return messages.get(
        rating,
        "Review the detected data-quality issues.",
    )


def severity_icon(severity: str) -> str:
    icons = {
        "CRITICAL": "🔴",
        "WARNING": "🟠",
        "INFO": "🔵",
        "SUCCESS": "🟢",
    }

    return icons.get(severity, "⚪")


def render_issue_card(recommendation: dict) -> None:
    severity = recommendation["severity"]
    title = recommendation["title"]
    message = recommendation["message"]

    icon = severity_icon(severity)

    with st.container(border=True):

        left, right = st.columns(
            [5, 1],
            vertical_alignment="center",
        )

        with left:
            st.markdown(
                f"### {icon} {title}"
            )

            st.write(message)

        with right:
            st.caption(severity)


# ---------------------------------------------------------
# BRAND / HERO
# ---------------------------------------------------------

st.html(
    """
    <div style="
        padding: 1.4rem 0 0.7rem 0;
    ">
        <div style="
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.16rem;
            opacity: 0.65;
        ">
            DATA HEALTH
        </div>

        <div style="
            font-size: 2.6rem;
            font-weight: 800;
            line-height: 1.1;
            margin-top: 0.25rem;
        ">
            Know the quality of your data
            <br>
            before you use it.
        </div>

        <div style="
            font-size: 1.05rem;
            opacity: 0.72;
            margin-top: 0.8rem;
            max-width: 720px;
        ">
            Upload a CSV and get an instant assessment of
            completeness, duplicates, consistency and structure.
        </div>
    </div>
    """
)


# ---------------------------------------------------------
# UPLOAD CARD
# ---------------------------------------------------------

with st.container(border=True):

    st.markdown("### 📄 Analyse your dataset")

    st.caption(
        "Upload a CSV file and Data Health Check will "
        "analyse it automatically."
    )

    uploaded_file = st.file_uploader(
        "Choose or drag and drop a CSV",
        type=["csv"],
        max_upload_size=10,
        help="Maximum file size: 10 MB",
    )

    if uploaded_file is None:

        st.caption(
            "CSV only • Maximum 10 MB • No account required"
        )


# ---------------------------------------------------------
# EMPTY STATE
# ---------------------------------------------------------

if uploaded_file is None:

    st.write("")

    st.subheader("What Data Health Check looks for")

    feature1, feature2, feature3, feature4 = st.columns(4)

    with feature1:
        with st.container(border=True):
            st.markdown("### ◻️ Completeness")
            st.caption(
                "Missing values and incomplete fields."
            )

    with feature2:
        with st.container(border=True):
            st.markdown("### ◻️ Uniqueness")
            st.caption(
                "Duplicate records and repeated rows."
            )

    with feature3:
        with st.container(border=True):
            st.markdown("### ◻️ Consistency")
            st.caption(
                "Formatting and whitespace problems."
            )

    with feature4:
        with st.container(border=True):
            st.markdown("### ◻️ Structure")
            st.caption(
                "Empty, unnamed or problematic columns."
            )

    st.stop()


# ---------------------------------------------------------
# READ CSV
# ---------------------------------------------------------

try:
    df = pd.read_csv(uploaded_file)

except Exception as exc:

    st.error(
        "We couldn't read this CSV file."
    )

    st.caption(str(exc))

    st.stop()


if df.empty:

    st.warning(
        "The uploaded CSV contains column headings "
        "but no data rows."
    )

    st.stop()


# ---------------------------------------------------------
# ANALYSE DATA
# ---------------------------------------------------------

results = analyse_dataframe(df)

scores = results["scores"]
rating = results["rating"]

issue_count = len(
    [
        item
        for item in results["recommendations"]
        if item["severity"] != "SUCCESS"
    ]
)


# ---------------------------------------------------------
# FILE SUMMARY
# ---------------------------------------------------------

st.write("")

file_left, file_right = st.columns(
    [4, 1],
    vertical_alignment="center",
)

with file_left:

    st.caption("ANALYSING")

    st.markdown(
        f"### 📄 {html.escape(uploaded_file.name)}"
    )

with file_right:

    st.caption(
        f"{results['rows']:,} rows • "
        f"{results['columns']:,} columns"
    )


# ---------------------------------------------------------
# SCORE CARD
# ---------------------------------------------------------

st.subheader("Data Health Score")

with st.container(border=True):

    score_left, score_right = st.columns(
        [1.2, 2],
        vertical_alignment="center",
    )

    with score_left:

        st.metric(
            "Overall score",
            f"{scores['overall']:.1f} / 100",
            border=False,
        )

        st.progress(
            int(round(scores["overall"]))
        )

    with score_right:

        st.markdown(
            f"## {rating_icon(rating)} {rating}"
        )

        st.write(
            rating_message(rating)
        )

        if issue_count == 0:
            st.success(
                "No immediate corrective actions detected."
            )

        elif issue_count == 1:
            st.info(
                "1 issue should be reviewed."
            )

        else:
            st.info(
                f"{issue_count} issues should be reviewed."
            )


# ---------------------------------------------------------
# QUALITY BREAKDOWN
# ---------------------------------------------------------

st.subheader("Quality Breakdown")

quality1, quality2, quality3, quality4 = st.columns(4)

quality1.metric(
    "Completeness",
    f"{scores['completeness']:.1f}%",
    border=True,
)

quality2.metric(
    "Uniqueness",
    f"{scores['uniqueness']:.1f}%",
    border=True,
)

quality3.metric(
    "Consistency",
    f"{scores['consistency']:.1f}%",
    border=True,
)

quality4.metric(
    "Structure",
    f"{scores['structure']:.1f}%",
    border=True,
)


# ---------------------------------------------------------
# DATASET OVERVIEW
# ---------------------------------------------------------

st.subheader("Dataset Overview")

overview1, overview2, overview3, overview4 = st.columns(4)

overview1.metric(
    "Rows",
    f"{results['rows']:,}",
    border=True,
)

overview2.metric(
    "Columns",
    f"{results['columns']:,}",
    border=True,
)

overview3.metric(
    "Missing values",
    f"{results['total_missing']:,}",
    border=True,
)

overview4.metric(
    "Duplicate rows",
    f"{results['duplicates']:,}",
    border=True,
)


# ---------------------------------------------------------
# ISSUES / RECOMMENDATIONS
# ---------------------------------------------------------

st.subheader("Issues to Review")

for recommendation in results["recommendations"]:
    render_issue_card(recommendation)


# ---------------------------------------------------------
# SEVERITY GUIDE
# ---------------------------------------------------------

with st.expander("How to interpret issue severity"):

    guide1, guide2 = st.columns(2)

    with guide1:

        st.markdown(
            "**🔴 Critical**  \n"
            "Structural problem that could affect "
            "downstream processing."
        )

        st.markdown(
            "**🟠 Warning**  \n"
            "Data-quality problem worth correcting."
        )

    with guide2:

        st.markdown(
            "**🔵 Info**  \n"
            "Minor consistency or cleanup issue."
        )

        st.markdown(
            "**🟢 Success**  \n"
            "No detected action required."
        )


# ---------------------------------------------------------
# COLUMN HEALTH
# ---------------------------------------------------------

st.subheader("Column Health")

column_df = pd.DataFrame(
    results["column_types"]
)

st.dataframe(
    column_df,
    width="stretch",
    hide_index=True,
)


# ---------------------------------------------------------
# MISSING DATA
# ---------------------------------------------------------

if results["missing_details"]:

    with st.expander(
        "Missing data details",
        expanded=False,
    ):

        missing_df = pd.DataFrame(
            results["missing_details"]
        )

        missing_df.columns = [
            "Column",
            "Missing values",
            "Missing %",
        ]

        st.dataframe(
            missing_df,
            width="stretch",
            hide_index=True,
        )


# ---------------------------------------------------------
# TECHNICAL DETAILS
# ---------------------------------------------------------

if results["issues"]:

    with st.expander(
        "Technical issues detected",
        expanded=False,
    ):

        for issue in results["issues"]:
            st.write(f"• {issue}")


# ---------------------------------------------------------
# DATA PREVIEW
# ---------------------------------------------------------

with st.expander(
    "Preview uploaded data",
    expanded=False,
):

    st.caption(
        "Showing the first 100 rows."
    )

    st.dataframe(
        df.head(100),
        width="stretch",
        hide_index=True,
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

footer_left, footer_right = st.columns(
    [3, 1]
)

with footer_left:
    st.caption(
        "Data Health Check • Prototype"
    )

with footer_right:
    st.caption(
        "Built with Python + Pandas"
    )