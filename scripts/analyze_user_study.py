import os
import re

import pandas as pd

# --- Configuration ---
DATA_FOLDER = 'study_data'  # Folder where your CSVs are located
NUM_FORMS = 9
QUESTIONS_PER_FORM = 10
NUM_USERS_PER_FORM = 3  # As stated: 3 users answer all questions

# Output file names
PROCESSED_DATA_OUTPUT_CSV = 'processed_study_data.csv'
SUMMARY_STATS_OUTPUT_CSV = 'summary_statistics.csv'

# --- Mappings and Regular Expressions ---
# Maps the prefix of score columns to (Metric, LLM_Type)
# Based on: ✔️🔵 Q1.1: Correctness: ...
#           emoji_color Q<LocalNum>.<SubNum>: <Metric>: ...
SCORE_COLUMN_MAP = {
    '✔️🔵': ('Correctness', 'BASELINE'),
    'ℹ️🔵': ('Informativeness', 'BASELINE'),
    '📝🔵': ('Pertinence', 'BASELINE'),
    '✔️🟠': ('Correctness', 'XRAG'),
    'ℹ️🟠': ('Informativeness', 'XRAG'),
    '📝🟠': ('Pertinence', 'XRAG'),
}
# Regex to parse score column headers
# Example: "✔️🔵 Q1.1: Correctness: How much does the BASELINE explanation match expert reasoning?"
SCORE_COL_REGEX = re.compile(
    r"^(✔️🔵|ℹ️🔵|📝🔵|✔️🟠|ℹ️🟠|📝🟠) Q(\d+)\.\d+: (Correctness|Informativeness|Pertinence):.*$")

# Regex to parse comment column headers
# Example: "💡 Q1.7: Additional Comments"
COMMENT_COL_REGEX = re.compile(r"^(💡) Q(\d+)\.\d+: Additional Comments$")


def parse_score_column(col_name):
    """Parses a score column header to extract its properties."""
    match = SCORE_COL_REGEX.match(col_name)
    if match:
        prefix = match.group(1)
        local_q_num = int(match.group(2))
        # metric_explicit = match.group(3) # Can be used for validation if needed

        metric, llm_type = SCORE_COLUMN_MAP.get(prefix, (None, None))

        if metric and llm_type:
            return {
                'LocalQuestionNum': local_q_num,
                'Metric': metric,
                'LLM_Type': llm_type
            }
    return None


def parse_comment_column(col_name):
    """Parses a comment column header to extract its properties."""
    match = COMMENT_COL_REGEX.match(col_name)
    if match:
        local_q_num = int(match.group(2))
        return {'LocalQuestionNum': local_q_num}
    return None


def process_study_data():
    """
    Reads all form CSVs, processes them, and aggregates the data.
    """
    all_forms_data_processed = []

    for form_num in range(1, NUM_FORMS + 1):
        file_path = os.path.join(DATA_FOLDER, f'form_{form_num}.csv')
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue

        try:
            raw_df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        if raw_df.shape[0] != NUM_USERS_PER_FORM:
            print(
                f"Warning: {file_path} has {raw_df.shape[0]} rows, expected {NUM_USERS_PER_FORM}. Skipping or needs review.")
            # Decide how to handle: skip, error, or try to process
            # For now, let's try to process what's there, but UserID assignment might be off.
            # A better approach might be to add a UserID column manually to CSVs or ensure consistency.

        # Assign UserID assuming order is consistent within each file
        raw_df['UserID'] = [f'User_{i + 1}' for i in range(raw_df.shape[0])]
        raw_df['FormNum'] = form_num

        # Identify id_vars for melting (columns that are not scores or comments)
        id_vars = ['UserID', 'FormNum', 'Timestamp']  # Timestamp is assumed to be the first col

        # Separate score columns and comment columns
        score_columns = []
        comment_columns = []

        for col in raw_df.columns:
            if col not in id_vars:  # Avoid re-processing id_vars
                if SCORE_COL_REGEX.match(col):
                    score_columns.append(col)
                elif COMMENT_COL_REGEX.match(col):
                    comment_columns.append(col)

        # Melt scores
        melted_scores_df = pd.melt(raw_df,
                                   id_vars=id_vars,
                                   value_vars=score_columns,
                                   var_name='Question_Raw_Score',
                                   value_name='Score')

        # Parse score details
        score_details = melted_scores_df['Question_Raw_Score'].apply(lambda x: pd.Series(parse_score_column(x)))
        melted_scores_df = pd.concat([melted_scores_df, score_details], axis=1)
        melted_scores_df.dropna(subset=['LocalQuestionNum', 'Metric', 'LLM_Type'],
                                inplace=True)  # Drop rows where parsing failed
        melted_scores_df['LocalQuestionNum'] = melted_scores_df['LocalQuestionNum'].astype(int)

        # Melt comments
        if comment_columns:  # Only melt if comment columns exist
            melted_comments_df = pd.melt(raw_df,
                                         id_vars=id_vars,
                                         value_vars=comment_columns,
                                         var_name='Question_Raw_Comment',
                                         value_name='Comment')
            comment_details = melted_comments_df['Question_Raw_Comment'].apply(
                lambda x: pd.Series(parse_comment_column(x)))
            melted_comments_df = pd.concat([melted_comments_df, comment_details], axis=1)
            melted_comments_df.dropna(subset=['LocalQuestionNum'], inplace=True)
            melted_comments_df['LocalQuestionNum'] = melted_comments_df['LocalQuestionNum'].astype(int)

            # Merge scores and comments
            # Ensure LocalQuestionNum is of the same type for merging if it came from different parsing
            processed_df = pd.merge(melted_scores_df,
                                    melted_comments_df[['UserID', 'FormNum', 'LocalQuestionNum', 'Comment']],
                                    on=['UserID', 'FormNum', 'LocalQuestionNum'],
                                    how='left')  # Left join to keep all scores, add comments where they match
        else:
            processed_df = melted_scores_df
            processed_df['Comment'] = None  # Add empty comment column if no comment columns found

        # Calculate GlobalQuestionID
        # GlobalQuestionSetStart is the first global question number for this form
        global_q_start_offset = (form_num - 1) * QUESTIONS_PER_FORM
        processed_df['GlobalQuestionID'] = global_q_start_offset + processed_df['LocalQuestionNum']

        all_forms_data_processed.append(processed_df)

    if not all_forms_data_processed:
        print("No data processed. Exiting.")
        return None, None

    final_processed_df = pd.concat(all_forms_data_processed, ignore_index=True)

    # Reorder columns for clarity
    final_columns_order = [
        'UserID', 'FormNum', 'GlobalQuestionID', 'LocalQuestionNum',
        'LLM_Type', 'Metric', 'Score', 'Comment', 'Timestamp',
        'Question_Raw_Score'  # Keeping raw column name for reference/debugging
    ]
    # Add Question_Raw_Comment if it exists from merging
    if 'Question_Raw_Comment' in final_processed_df.columns:
        final_columns_order.append('Question_Raw_Comment')

    # Filter to only include existing columns in final_columns_order
    final_columns_order = [col for col in final_columns_order if col in final_processed_df.columns]
    final_processed_df = final_processed_df[final_columns_order]

    # Ensure Score is numeric
    final_processed_df['Score'] = pd.to_numeric(final_processed_df['Score'], errors='coerce')

    return final_processed_df


def calculate_summary_statistics(processed_df):
    """Calculates summary statistics from the processed data."""
    if processed_df is None or processed_df.empty:
        return None

    summary_stats = processed_df.groupby(['LLM_Type', 'Metric'])['Score'].agg(
        Mean='mean',
        StdDev='std',
        Count='count',
        Min='min',
        Max='max'
    ).reset_index()
    return summary_stats


if __name__ == '__main__':
    print("Starting data processing...")

    if not os.path.exists(DATA_FOLDER):
        print(f"Error: Data folder '{DATA_FOLDER}' not found. Please create it and place your CSV files inside.")
    else:
        processed_data = process_study_data()

        if processed_data is not None and not processed_data.empty:
            try:
                processed_data.to_csv(PROCESSED_DATA_OUTPUT_CSV, index=False)
                print(f"\nSuccessfully processed data saved to: {PROCESSED_DATA_OUTPUT_CSV}")
            except Exception as e:
                print(f"\nError saving processed data: {e}")

            summary_stats = calculate_summary_statistics(processed_data)
            if summary_stats is not None and not summary_stats.empty:
                try:
                    summary_stats.to_csv(SUMMARY_STATS_OUTPUT_CSV, index=False)
                    print(f"Successfully calculated summary statistics saved to: {SUMMARY_STATS_OUTPUT_CSV}")
                except Exception as e:
                    print(f"Error saving summary statistics: {e}")
            else:
                print("No summary statistics generated.")
        else:
            print("No data was processed, so no output files were generated.")
    print("\nProcessing complete.")
