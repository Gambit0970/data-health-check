import pandas as pd


def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def score_label(score: float) -> str:
    if score >= 98:
        return "EXCELLENT"

    if score >= 90:
        return "GOOD"

    if score >= 75:
        return "NEEDS ATTENTION"

    return "POOR"

def score_dataset(
    df: pd.DataFrame,
    duplicate_count: int,
    whitespace_count: int,
    structural_issue_count: int,
    missing_column_count: int,
    whitespace_column_count: int,
) -> dict:

    row_count = len(df)
    column_count = len(df.columns)
    total_cells = row_count * column_count
    total_missing = int(df.isna().sum().sum())

    # -------------------------------------------------
    # COMPLETENESS
    #
    # Penalise both:
    # - percentage of missing cells
    # - percentage of columns affected
    # -------------------------------------------------

    if total_cells == 0:
        completeness = 0.0
    else:
        missing_cell_rate = (
            total_missing / total_cells
        )

        missing_column_rate = (
            missing_column_count / column_count
            if column_count > 0
            else 0
        )

        completeness_penalty = (
            missing_cell_rate * 150
            + missing_column_rate * 12
        )

        completeness = (
            100 - min(
                completeness_penalty,
                50,
            )
        )

    # -------------------------------------------------
    # UNIQUENESS
    #
    # Duplicates get:
    # - a rate-based penalty
    # - an additional count penalty
    #
    # This stops one duplicate being almost invisible
    # in a medium-sized dataset.
    # -------------------------------------------------

    if row_count == 0:
        uniqueness = 0.0
    else:
        duplicate_rate = (
            duplicate_count / row_count
        )

        duplicate_penalty = (
            duplicate_rate * 100
            + min(
                duplicate_count * 3,
                12,
            )
        )

        uniqueness = (
            100 - min(
                duplicate_penalty,
                40,
            )
        )

    # -------------------------------------------------
    # CONSISTENCY
    #
    # Penalise:
    # - individual whitespace problems
    # - how many string columns are affected
    # -------------------------------------------------

    string_columns = list(
        df.select_dtypes(
            include="str"
        ).columns
    )

    string_cells = 0

    for column in string_columns:
        string_cells += int(
            df[column].notna().sum()
        )

    if string_cells == 0:
        consistency = 100.0

    else:
        whitespace_rate = (
            whitespace_count / string_cells
        )

        whitespace_column_rate = (
            whitespace_column_count
            / len(string_columns)
            if string_columns
            else 0
        )

        consistency_penalty = (
            whitespace_rate * 100
            + whitespace_column_rate * 10
        )

        consistency = (
            100 - min(
                consistency_penalty,
                40,
            )
        )

    # -------------------------------------------------
    # STRUCTURE
    #
    # Structural problems are more serious.
    # Each one removes 15 points.
    # -------------------------------------------------

    structure = (
        100 - structural_issue_count * 15
    )

    completeness = clamp(completeness)
    uniqueness = clamp(uniqueness)
    consistency = clamp(consistency)
    structure = clamp(structure)

    # Weighted overall score

    overall = (
        completeness * 0.40
        + uniqueness * 0.25
        + consistency * 0.20
        + structure * 0.15
    )

    return {
        "overall": round(overall, 1),
        "completeness": round(
            completeness,
            1,
        ),
        "uniqueness": round(
            uniqueness,
            1,
        ),
        "consistency": round(
            consistency,
            1,
        ),
        "structure": round(
            structure,
            1,
        ),
    }

def analyse_dataframe(df: pd.DataFrame) -> dict:
    duplicate_count = int(
        df.duplicated().sum()
    )

    missing = df.isna().sum()

    missing_details = []

    for column, count in missing.items():
        if count > 0:
            percentage = (
                count / len(df) * 100
                if len(df) > 0
                else 0
            )

            missing_details.append(
                {
                    "column": column,
                    "count": int(count),
                    "percentage": round(
                        percentage, 2
                    ),
                }
            )

    issues = []
    structural_issues = 0
    whitespace_count = 0
    whitespace_issues = {}

    # Detect unnamed/blank columns
    unnamed_columns = [
        column
        for column in df.columns
        if str(column).strip() == ""
        or str(column).startswith("Unnamed:")
    ]

    if unnamed_columns:
        issues.append(
            "Unnamed or blank columns found: "
            + ", ".join(
                map(str, unnamed_columns)
            )
        )

        structural_issues += len(
            unnamed_columns
        )

    # Duplicate column names
    duplicate_columns = (
        df.columns[
            df.columns.duplicated()
        ].tolist()
    )

    if duplicate_columns:
        issues.append(
            "Duplicate column names found: "
            + ", ".join(
                map(str, duplicate_columns)
            )
        )

        structural_issues += 1

    # Empty columns
    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if empty_columns:
        issues.append(
            "Completely empty columns: "
            + ", ".join(
                map(str, empty_columns)
            )
        )

        structural_issues += len(
            empty_columns
        )

    # Whitespace problems
    for column in df.select_dtypes(
        include="str"
    ).columns:

        values = (
            df[column]
            .dropna()
            .astype(str)
        )

        count = int(
            values.apply(
                lambda value:
                value != value.strip()
            ).sum()
        )

        if count > 0:
            whitespace_count += count
            whitespace_issues[column] = count

            issues.append(
                f"{column}: {count} value(s) "
                "contain leading or trailing "
                "whitespace."
            )

    # Low-information columns
    for column in df.columns:
        unique_count = df[column].nunique(
            dropna=True
        )

        if unique_count == 1:
            issues.append(
                f"{column}: contains only one "
                "unique non-null value."
            )

    scores = score_dataset(
        df=df,
        duplicate_count=duplicate_count,
        whitespace_count=whitespace_count,
        structural_issue_count=structural_issues,
        missing_column_count=len(
            missing_details
        ),
        whitespace_column_count=len(
            whitespace_issues
        ),
        )

    total_missing = int(missing.sum())

    recommendations = []

    if total_missing > 0:
        columns = [
            item["column"]
            for item in missing_details
        ]

        recommendations.append(
            {
                "severity": "WARNING",
                "title": "Missing data",
                "message": (
                    f"Review {total_missing} missing "
                    "value(s) across: "
                    + ", ".join(map(str, columns))
                    + "."
                ),
            }
        )

    if duplicate_count > 0:
        recommendations.append(
            {
                "severity": "WARNING",
                "title": "Duplicate records",
                "message": (
                    f"Remove or review "
                    f"{duplicate_count} duplicate row(s)."
                ),
            }
        )

    for column, count in whitespace_issues.items():
        recommendations.append(
            {
                "severity": "INFO",
                "title": "Formatting inconsistency",
                "message": (
                    f"Trim leading/trailing whitespace "
                    f"in '{column}' "
                    f"({count} value(s))."
                ),
            }
        )

    if empty_columns:
        recommendations.append(
            {
                "severity": "CRITICAL",
                "title": "Empty columns",
                "message": (
                    "Remove completely empty columns "
                    "unless required downstream: "
                    + ", ".join(
                        map(str, empty_columns)
                    )
                    + "."
                ),
            }
        )

    if unnamed_columns:
        recommendations.append(
            {
                "severity": "CRITICAL",
                "title": "Unnamed columns",
                "message": (
                    "Rename or remove unnamed columns "
                    "so every field has a meaningful name."
                ),
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "severity": "SUCCESS",
                "title": "No action required",
                "message": (
                    "No immediate data-quality actions "
                    "are required."
                ),
            }
        )
        
    column_types = [
        {
            "Column": column,
            "Type": str(df[column].dtype),
            "Missing": int(
                df[column].isna().sum()
            ),
            "Unique values": int(
                df[column].nunique(
                    dropna=True
                )
            ),
        }
        for column in df.columns
    ]

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "scores": scores,
        "rating": score_label(
            scores["overall"]
        ),
        "duplicates": duplicate_count,
        "total_missing": total_missing,
        "missing_details": missing_details,
        "issues": issues,
        "recommendations": recommendations,
        "column_types": column_types,
    }