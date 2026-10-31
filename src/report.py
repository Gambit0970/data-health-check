import html
from datetime import datetime, timezone


def escape(value) -> str:
    return html.escape(str(value))


def build_html_report(
    file_name: str,
    results: dict,
) -> str:
    scores = results["scores"]

    generated_at = datetime.now(
        timezone.utc
    ).strftime("%d %B %Y at %H:%M UTC")

    # -------------------------------------------------
    # RECOMMENDATIONS
    # -------------------------------------------------

    recommendation_html = ""

    for recommendation in results["recommendations"]:

        severity = escape(
            recommendation["severity"]
        )

        title = escape(
            recommendation["title"]
        )

        message = escape(
            recommendation["message"]
        )

        severity_class = severity.lower()

        recommendation_html += f"""
        <div class="issue {severity_class}">
            <div class="issue-header">
                <span class="severity">
                    {severity}
                </span>

                <strong>
                    {title}
                </strong>
            </div>

            <div class="issue-message">
                {message}
            </div>
        </div>
        """

    # -------------------------------------------------
    # COLUMN HEALTH
    # -------------------------------------------------

    column_rows = ""

    for column in results["column_types"]:

        column_rows += f"""
        <tr>
            <td>{escape(column["Column"])}</td>
            <td>{escape(column["Type"])}</td>
            <td>{escape(column["Missing"])}</td>
            <td>{escape(column["Unique values"])}</td>
        </tr>
        """

    # -------------------------------------------------
    # MISSING DATA
    # -------------------------------------------------

    if results["missing_details"]:

        missing_rows = ""

        for item in results["missing_details"]:

            missing_rows += f"""
            <tr>
                <td>{escape(item["column"])}</td>
                <td>{escape(item["count"])}</td>
                <td>{escape(item["percentage"])}%</td>
            </tr>
            """

        missing_section = f"""
        <section>
            <h2>Missing Data</h2>

            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Missing values</th>
                        <th>Missing %</th>
                    </tr>
                </thead>

                <tbody>
                    {missing_rows}
                </tbody>
            </table>
        </section>
        """

    else:

        missing_section = """
        <section>
            <h2>Missing Data</h2>

            <div class="success-box">
                No missing values were detected.
            </div>
        </section>
        """

    # -------------------------------------------------
    # FINAL HTML
    # -------------------------------------------------

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
    Data Health Report - {escape(file_name)}
</title>

<style>

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        background: #f5f7fa;
        color: #172033;
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Arial,
            sans-serif;
        line-height: 1.5;
    }}

    .page {{
        max-width: 1050px;
        margin: 40px auto;
        background: white;
        padding: 48px;
        border-radius: 18px;
        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.08);
    }}

    .brand {{
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #667085;
    }}

    h1 {{
        margin-top: 8px;
        margin-bottom: 4px;
        font-size: 38px;
    }}

    h2 {{
        margin-top: 42px;
        margin-bottom: 16px;
    }}

    .subtitle {{
        color: #667085;
        margin-bottom: 30px;
    }}

    .file-details {{
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 30px;
    }}

    .score-card {{
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 28px;
    }}

    .score {{
        font-size: 54px;
        font-weight: 800;
        line-height: 1;
    }}

    .score-out-of {{
        color: #667085;
        font-size: 18px;
    }}

    .rating {{
        display: inline-block;
        margin-top: 14px;
        padding: 7px 14px;
        border-radius: 999px;
        background: #ecfdf3;
        color: #027a48;
        font-weight: 800;
    }}

    .grid {{
        display: grid;
        grid-template-columns:
            repeat(4, minmax(0, 1fr));
        gap: 14px;
    }}

    .metric {{
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px;
    }}

    .metric-label {{
        color: #667085;
        font-size: 13px;
        margin-bottom: 6px;
    }}

    .metric-value {{
        font-size: 25px;
        font-weight: 750;
    }}

    .issue {{
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        border-left: 5px solid;
    }}

    .issue-header {{
        margin-bottom: 6px;
    }}

    .issue-message {{
        color: #344054;
    }}

    .severity {{
        display: inline-block;
        font-size: 11px;
        font-weight: 800;
        margin-right: 8px;
    }}

    .critical {{
        background: #fef3f2;
        border-color: #d92d20;
    }}

    .warning {{
        background: #fffaeb;
        border-color: #f79009;
    }}

    .info {{
        background: #eff8ff;
        border-color: #2e90fa;
    }}

    .success {{
        background: #ecfdf3;
        border-color: #12b76a;
    }}

    .success-box {{
        background: #ecfdf3;
        padding: 16px;
        border-radius: 10px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
    }}

    th {{
        background: #f8fafc;
        text-align: left;
        font-size: 13px;
    }}

    th,
    td {{
        padding: 11px 12px;
        border-bottom: 1px solid #e5e7eb;
    }}

    .footer {{
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        color: #667085;
        font-size: 12px;
    }}

    .disclaimer {{
        margin-top: 20px;
        background: #f8fafc;
        padding: 14px;
        border-radius: 10px;
        color: #667085;
        font-size: 12px;
    }}

    @media print {{

        body {{
            background: white;
        }}

        .page {{
            margin: 0;
            max-width: none;
            box-shadow: none;
        }}
    }}

    @media (max-width: 750px) {{

        .page {{
            margin: 0;
            padding: 25px;
            border-radius: 0;
        }}

        .grid {{
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }}
    }}

</style>
</head>


<body>

<div class="page">

    <div class="brand">
        DATA HEALTH
    </div>

    <h1>
        Data Health Report
    </h1>

    <div class="subtitle">
        Automated data-quality assessment
    </div>


    <div class="file-details">

        <strong>
            {escape(file_name)}
        </strong>

        <br>

        {results["rows"]:,} rows
        &nbsp;•&nbsp;
        {results["columns"]:,} columns

        <br>

        <small>
            Report generated {generated_at}
        </small>

    </div>


    <div class="score-card">

        <div class="score">
            {scores["overall"]:.1f}
            <span class="score-out-of">
                / 100
            </span>
        </div>

        <div class="rating">
            {escape(results["rating"])}
        </div>

    </div>


    <h2>
        Quality Breakdown
    </h2>

    <div class="grid">

        <div class="metric">
            <div class="metric-label">
                Completeness
            </div>

            <div class="metric-value">
                {scores["completeness"]:.1f}%
            </div>
        </div>


        <div class="metric">
            <div class="metric-label">
                Uniqueness
            </div>

            <div class="metric-value">
                {scores["uniqueness"]:.1f}%
            </div>
        </div>


        <div class="metric">
            <div class="metric-label">
                Consistency
            </div>

            <div class="metric-value">
                {scores["consistency"]:.1f}%
            </div>
        </div>


        <div class="metric">
            <div class="metric-label">
                Structure
            </div>

            <div class="metric-value">
                {scores["structure"]:.1f}%
            </div>
        </div>

    </div>


    <h2>
        Dataset Overview
    </h2>

    <div class="grid">

        <div class="metric">
            <div class="metric-label">
                Rows
            </div>

            <div class="metric-value">
                {results["rows"]:,}
            </div>
        </div>


        <div class="metric">
            <div class="metric-label">
                Columns
            </div>

            <div class="metric-value">
                {results["columns"]:,}
            </div>
        </div>


        <div class="metric">
            <div class="metric-label">
                Missing values
            </div>

            <div class="metric-value">
                {results["total_missing"]:,}
            </div>
        </div>


        <div class="metric">
            <div class="metric-label">
                Duplicate rows
            </div>

            <div class="metric-value">
                {results["duplicates"]:,}
            </div>
        </div>

    </div>


    <section>

        <h2>
            Recommended Actions
        </h2>

        {recommendation_html}

    </section>


    <section>

        <h2>
            Column Health
        </h2>

        <table>

            <thead>

                <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Missing</th>
                    <th>Unique values</th>
                </tr>

            </thead>

            <tbody>
                {column_rows}
            </tbody>

        </table>

    </section>


    {missing_section}


    <div class="disclaimer">

        This report is an automated data-quality assessment.
        It identifies common quality indicators but does not
        guarantee that a dataset is correct or suitable for a
        particular business, regulatory or analytical purpose.

    </div>


    <div class="footer">

        Data Health Check
        &nbsp;•&nbsp;
        Generated with Python + Pandas

    </div>

</div>

</body>
</html>
"""