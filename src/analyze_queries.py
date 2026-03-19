import argparse
import json
from pathlib import Path

import pandas as pd

from categorizer import classify_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Beastlife customer queries")
    parser.add_argument(
        "--input",
        default="data/sample_queries.csv",
        help="Path to input CSV",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for generated analytics files",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM-based fallback classification when API key is available",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    predictions = df["customer_message"].apply(
        lambda text: classify_message(str(text), use_llm=args.use_llm)
    )

    df["predicted_category"] = predictions.apply(lambda x: x.category)
    df["confidence"] = predictions.apply(lambda x: x.confidence)
    df["classification_method"] = predictions.apply(lambda x: x.method)

    if "true_category" in df.columns:
        accuracy = (df["predicted_category"] == df["true_category"]).mean()
    else:
        accuracy = None

    distribution = (
        df.groupby("predicted_category")
        .size()
        .reset_index(name="query_count")
        .sort_values("query_count", ascending=False)
    )
    distribution["percentage"] = (
        distribution["query_count"] / distribution["query_count"].sum() * 100
    ).round(2)

    weekly = (
        df.groupby(
            ["predicted_category", pd.Grouper(key="timestamp", freq="W")],
            observed=True,
        )
        .size()
        .reset_index(name="query_count")
    )

    monthly = (
        df.groupby(
            ["predicted_category", pd.Grouper(key="timestamp", freq="ME")],
            observed=True,
        )
        .size()
        .reset_index(name="query_count")
    )

    df.to_csv(output_dir / "classified_queries.csv", index=False)
    distribution.to_csv(output_dir / "issue_distribution.csv", index=False)
    weekly.to_csv(output_dir / "weekly_trends.csv", index=False)
    monthly.to_csv(output_dir / "monthly_trends.csv", index=False)

    summary = {
        "total_queries": int(len(df)),
        "categories_detected": int(distribution.shape[0]),
        "top_issue": distribution.iloc[0]["predicted_category"],
        "top_issue_percentage": float(distribution.iloc[0]["percentage"]),
        "classification_accuracy_vs_labels": round(float(accuracy), 4)
        if accuracy is not None
        else None,
    }

    with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("=== Beastlife Query Analysis ===")
    print(f"Total queries: {summary['total_queries']}")
    print(f"Top issue: {summary['top_issue']} ({summary['top_issue_percentage']}%)")
    if accuracy is not None:
        print(f"Accuracy against sample labels: {summary['classification_accuracy_vs_labels']}")


if __name__ == "__main__":
    main()
