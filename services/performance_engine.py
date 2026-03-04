import pandas as pd
import numpy as np


def compute_performance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["raw_score"] = (
        df["projects_handled"] * 2
        + df["clients_managed"] * 3
        + df["tasks_completed"] * 0.5
        + df["on_time_delivery_rate"] * 5
    )
    min_score = df["raw_score"].min()
    max_score = df["raw_score"].max()
    df["performance_score"] = (
        (df["raw_score"] - min_score) / (max_score - min_score) * 100
    ).round(2)

    def classify(score):
        if score >= 85:
            return "Elite"
        elif score >= 65:
            return "High"
        elif score >= 45:
            return "Moderate"
        else:
            return "Needs Improvement"

    df["performance_tier"] = df["performance_score"].apply(classify)
    df["badge"] = df["performance_tier"].map({
        "Elite": " Elite",
        "High": " High",
        "Moderate": " Moderate",
        "Needs Improvement": " Needs Improvement",
    })
    return df


def get_top_performer(df: pd.DataFrame) -> dict:
    scored = compute_performance(df)
    top = scored.loc[scored["performance_score"].idxmax()]
    return top.to_dict()
