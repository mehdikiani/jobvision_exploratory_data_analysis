import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from matplotlib.ticker import FuncFormatter

# --- Configuration Import ---
try:
    import config
except ImportError:
    print("Error: config.py not found.")
    # Define dummy functions
    class DummyFont:
        def get_name(self): return "Arial"
    class config:
        titr_font = nazanin_font = DummyFont()
        def rtl_text(t): return t
        def set_title(ax, t): ax.set_title(t)
        def set_labels(ax, x, y): ax.set_xlabel(x); ax.set_ylabel(y)
        def to_persian_numerals(n): return str(n)


def parse_degree_level(academic_json: str):
    """
    Parses the JSON string from the 'AcademicFields' column and extracts
    the first listed degree level.
    """
    if pd.isna(academic_json) or not isinstance(academic_json, str):
        return 'نامشخص'
    try:
        # Load the JSON data
        data = json.loads(academic_json.replace("'", '"'))
        if isinstance(data, list) and len(data) > 0 and 'DegreeLevel' in data[0]:
            return data[0]['DegreeLevel']
    except (json.JSONDecodeError, TypeError):
        return 'نامشخص'
    return 'نامشخص'


def visualize_experience_vs_education(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the relationship between required education level and years of
    experience, saving the result as a box plot.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    EXPERIENCE_OUTLIER_QUANTILE = 0.98 # Remove top 2% of experience requirements

    try:
        # --- 1. Data Loading ---
        df = pd.read_csv(cleaned_file_path)
        print("Cleaned dataset loaded successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{cleaned_file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return

    # --- 2. Data Preparation ---
    # Apply the parsing function to create a 'DegreeLevel' column
    df['DegreeLevel'] = df['AcademicFields'].apply(parse_degree_level)

    # Filter out data that is not useful for this specific analysis
    df_filtered = df[
        (df['DegreeLevel'] != 'نامشخص') &
        (df['RequiredExperienceYears'] > 0)
    ].copy()

    # --- 3. Outlier Handling ---
    experience_cap = df_filtered['RequiredExperienceYears'].quantile(EXPERIENCE_OUTLIER_QUANTILE)
    df_filtered = df_filtered[df_filtered['RequiredExperienceYears'] <= experience_cap]
    
    print(f"Analysis includes jobs with known degree levels and > 0 experience years.")
    print(f"Experience requirements capped at {experience_cap} years for visualization.")
    
    # Define a logical order for educational degrees
    degree_order = ['کاردانی', 'کارشناسی', 'کارشناسی ارشد', 'دکتری']
    df_filtered['DegreeLevel'] = pd.Categorical(df_filtered['DegreeLevel'], categories=degree_order, ordered=True)
    df_filtered.dropna(subset=['DegreeLevel'], inplace=True) # Drop any degrees not in our order

    # --- 4. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    
    sns.boxplot(
        x='RequiredExperienceYears',
        y='DegreeLevel',
        data=df_filtered,
        order=degree_order,
        palette='crest',
        ax=ax,
        orient='h'
    )

    # --- 5. Styling and Labeling ---
    config.set_title(ax, 'رابطه سطح تحصیلات و سابقه کار مورد نیاز')
    config.set_labels(ax, xlabel='سابقه کار مورد نیاز (سال)', ylabel='سطح تحصیلات')

    # Apply RTL processing to the y-axis (degree names)
    rtl_degree_labels = [config.rtl_text(label) for label in degree_order]
    ax.set_yticklabels(rtl_degree_labels, fontproperties=config.nazanin_font)

    # Format x-axis with Persian numerals
    formatter_x = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val)}'))
    ax.xaxis.set_major_formatter(formatter_x)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)

    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "04_experience_vs_education.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_experience_vs_education(CLEANED_DATASET_PATH)
