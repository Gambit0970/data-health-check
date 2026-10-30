import sys
from pathlib import Path

import pandas as pd


def clamp(value: float) -> float:
    """Keep a score between 0 and 100."""
    return max(0.0, min(100.0, value))


def score_dataset(
    df: pd.DataFrame,
    duplicate_count: int,
    whitespace_count: int,
    structural_issue_count: int,
) -> dict:
    total_cells = df.shape[0] * df.shape[1]
    total_missing = int(df.isna().sum().sum())

    # 1. Completeness
    if total_cells == 0:
        completeness = 0.0
    else:
        completeness = (
            1 - (total_missing / total_cells)
        ) * 100

    # 2. Uniqueness
    if len(df) == 0:
        uniqueness = 0.0
    else:
        uniqueness = (
            1 - (duplicate_count / len(df))
        ) * 100

    # 3. Consistency
    string_cells = 0

    for column in df.select_dtypes(include="str").columns:
        string_cells += df[column].notna().sum()

    if string_cells == 0:
        consistency = 100.0
    else:
        consistency = (
            1 - (whitespace_count / string_cells)
        ) * 100

    # 4. Structure
    #
    # Each structural issue costs 20 points.
    structure = 100 - (structural_issue_count * 20)

    completeness = clamp(completeness)
    uniqueness = clamp(uniqueness)
    consistency = clamp(consistency)
    structure = clamp(structure)

    overall = (
        completeness * 0.40
        + uniqueness * 0.25
        + consistency * 0.20
        + structure * 0.15
    )

    return {
        "overall": round(overall, 1),
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "consistency": round(consistency, 1),
        "structure": round(structure, 1),
    }


def score_label(score: float) -> str:
    if score >= 90:
        return "EXCELLENT"

    if score >= 75:
        return "GOOD"

    if score >= 50:
        return "NEEDS ATTENTION"

    return "POOR"


def analyse_csv(file_path: str) -> None:
    path = Path(file_path)

    if not path.exists():
        print(f"Error: file not found: {path}")
        return

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        print(f"Error reading CSV: {exc}")
        return

    print("\nDATA HEALTH CHECK")
    print("=" * 60)

    print(f"File: {path.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    print("\nCOLUMN TYPES")
    print("-" * 60)

    for column in df.columns:
        print(
            f"{column:<30} "
            f"{str(df[column].dtype):<15}"
        )

    print("\nMISSING VALUES")
    print("-" * 60)

    missing = df.isna().sum()
    missing_found = False

    for column, count in missing.items():
        if count > 0:
            missing_found = True
            percentage = (count / len(df)) * 100

            print(
                f"{column:<30} "
                f"{count:>6} missing "
                f"({percentage:>6.2f}%)"
            )

    if not missing_found:
        print("No missing values found.")

    print("\nDUPLICATE ROWS")
    print("-" * 60)

    duplicate_count = int(df.duplicated().sum())

    print(f"Duplicate rows: {duplicate_count:,}")

    print("\nBASIC DATA QUALITY CHECKS")
    print("-" * 60)

    issues = []
    structural_issues = 0
    whitespace_count = 0

    # Blank column names
    blank_column_names = [
        column
        for column in df.columns
        if str(column).strip() == ""
    ]

    if blank_column_names:
        issues.append(
            "One or more columns have blank names."
        )
        structural_issues += 1

    # Duplicate column names
    duplicate_columns = (
        df.columns[df.columns.duplicated()].tolist()
    )

    if duplicate_columns:
        issues.append(
            "Duplicate column names found: "
            f"{duplicate_columns}"
        )
        structural_issues += 1

    # Completely empty columns
    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if empty_columns:
        issues.append(
            "Completely empty columns: "
            + ", ".join(empty_columns)
        )
        structural_issues += len(empty_columns)

    # Leading/trailing whitespace
    for column in df.select_dtypes(include="str").columns:
        values = df[column].dropna().astype(str)

        column_whitespace_count = values.apply(
            lambda value: value != value.strip()
        ).sum()

        whitespace_count += int(
            column_whitespace_count
        )

        if column_whitespace_count > 0:
            issues.append(
                f"{column}: "
                f"{column_whitespace_count} values "
                "contain leading or trailing whitespace."
            )

    # Single-value columns are worth flagging,
    # but do not reduce the structural score.
    for column in df.columns:
        unique_count = df[column].nunique(
            dropna=True
        )

        if unique_count == 1:
            issues.append(
                f"{column}: contains only one unique "
                "non-null value."
            )

    if issues:
        for issue in issues:
            print(f"[!] {issue}")
    else:
        print(
            "No obvious basic data-quality "
            "problems found."
        )

    total_missing = int(df.isna().sum().sum())

    scores = score_dataset(
        df=df,
        duplicate_count=duplicate_count,
        whitespace_count=whitespace_count,
        structural_issue_count=structural_issues,
    )

    print("\nDATA HEALTH SCORE")
    print("=" * 60)

    print(
        f"Overall:      "
        f"{scores['overall']:>5.1f} / 100"
    )

    print(
        f"Completeness: "
        f"{scores['completeness']:>5.1f}%"
    )

    print(
        f"Uniqueness:   "
        f"{scores['uniqueness']:>5.1f}%"
    )

    print(
        f"Consistency:  "
        f"{scores['consistency']:>5.1f}%"
    )

    print(
        f"Structure:    "
        f"{scores['structure']:>5.1f}%"
    )

    print(
        f"\nRating: {score_label(scores['overall'])}"
    )

    print("\nSUMMARY")
    print("-" * 60)

    print(f"Missing values: {total_missing:,}")
    print(f"Duplicate rows: {duplicate_count:,}")
    print(f"Other issues: {len(issues):,}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage:")
        print(
            "  python src/main.py <csv-file>"
        )
        print()
        print("Example:")
        print(
            "  python src/main.py "
            "sample-data/customers.csv"
        )
        return

    analyse_csv(sys.argv[1])


if __name__ == "__main__":
    main()