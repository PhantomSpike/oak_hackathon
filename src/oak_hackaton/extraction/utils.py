import pandas as pd
import numpy as np
from oak_hackaton.utils import load_json

thread_to_unit_mapping = load_json("/Users/alex/Desktop/Code/Oak_hackathon/oak_hackathon/oak_data/thread_to_unit_mapping.json")

def process_student_data(student_data: pd.DataFrame, thread_to_unit_mapping: dict) -> pd.DataFrame:
    student_data["Answer"] = student_data["Answer"].map({"Correct": 1, "Incorrect":0})
    student_data_mean = student_data.groupby("Thread")["Answer"].mean()
    df = pd.DataFrame(columns=["Units", "Threads", "Score"])
    df["Units"] = thread_to_unit_mapping.keys()
    df["Threads"] = df["Units"].map(thread_to_unit_mapping)
    df["Score"] = df["Threads"].map(student_data_mean)
    df["Default_lesson_weights"] = 1-df["Score"]
    df["Default_lesson_weights"] = df["Default_lesson_weights"]/df["Default_lesson_weights"].sum()
    # Calculate weeks for each unit
    total_weeks = 36
    df['weeks'] = np.round(df['Default_lesson_weights'] * total_weeks).astype(int)

    # Adjust weeks to ensure total is exactly 36
    diff = total_weeks - df['weeks'].sum()
    df.loc[df['weeks'].idxmax(), 'weeks'] += diff
    return df