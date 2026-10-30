import pandas as pd
import streamlit as st

from src.analyser import analyse_dataframe


st.set_page_config(
    page_title="Data Health Check",
    page_icon="🩺",
    layout="wide",
)


st.title("🩺 Data Health Check")

st.write(
    "Upload a CSV file to identify missing data, "
    "duplicate records, consistency problems and "
    "structural data-quality issues."
)

st.caption(
    "Your dataset is analysed automatically and "
    "given a Data Health Score out of 100."
)


uploaded_file = st.file_uploader(
    "Drag and drop your CSV file here",
    type=["csv"],
    max_upload_size=10,
)


if uploaded_file is None:
    st.info(
        "Upload a CSV file above to begin."
    )

    st.stop()


try:
    df = pd.read_csv(uploaded_file)

except Exception as exc:
    st.error(
        f"Unable to read this CSV file: {exc}"
    )
    st.stop()


if df.empty:
    st.warning(
        "The uploaded CSV contains no data rows."
    )
    st.stop()


results = analyse_dataframe(df)

scores = results["scores"]


st.divider()

st.subheader("Data Health Score")


score_column, rating_column = st.columns(
    [2, 1]
)

with score_column:
    st.metric(
        label="Overall score",
        value=f"{scores['overall']} / 100",
    )

    st.progress(
        int(round(scores["overall"]))
    )

with rating_column:
    st.metric(
        label="Rating",
        value=results["rating"],
    )


st.subheader("Quality Breakdown")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Completeness",
        f"{scores['completeness']}%",
    )

with col2:
    st.metric(
        "Uniqueness",
        f"{scores['uniqueness']}%",
    )

with col3:
    st.metric(
        "Consistency",
        f"{scores['consistency']}%",
    )

with col4:
    st.metric(
        "Structure",
        f"{scores['structure']}%",
    )


st.divider()

st.subheader("Dataset Overview")

overview1, overview2, overview3, overview4 = (
    st.columns(4)
)

overview1.metric(
    "Rows",
    f"{results['rows']:,}",
)

overview2.metric(
    "Columns",
    f"{results['columns']:,}",
)

overview3.metric(
    "Missing values",
    f"{results['total_missing']:,}",
)

overview4.metric(
    "Duplicate rows",
    f"{results['duplicates']:,}",
)


st.divider()

st.subheader("Recommendations")

for number, recommendation in enumerate(
    results["recommendations"],
    start=1,
):
    st.warning(
        f"{number}. {recommendation}"
    )


st.divider()

st.subheader("Column Health")

column_df = pd.DataFrame(
    results["column_types"]
)

st.dataframe(
    column_df,
    width="stretch",
    hide_index=True,
)


if results["missing_details"]:

    st.subheader("Missing Data")

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


if results["issues"]:

    with st.expander(
        "Technical issues detected"
    ):
        for issue in results["issues"]:
            st.write(f"⚠️ {issue}")


with st.expander("Preview uploaded data"):

    st.dataframe(
        df.head(100),
        width="stretch",
        hide_index=True,
    )


st.divider()

st.caption(
    "Data Health Check — prototype"
)