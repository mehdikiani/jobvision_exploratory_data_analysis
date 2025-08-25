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


def parse_academic_fields(academic_json: str):
    """
    Parses the JSON string from the 'AcademicFields' column and returns a
    list of all academic field types mentioned.
    """
    if pd.isna(academic_json) or not isinstance(academic_json, str):
        return []
    try:
        data = json.loads(academic_json.replace("'", '"'))
        if isinstance(data, list):
            fields = [
                item.get('FieldType', '').strip() 
                for item in data 
                if item.get('FieldType') and item.get('FieldType').strip()
            ]
            return fields
    except (json.JSONDecodeError, TypeError):
        return []
    return []


def visualize_academic_fields(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the most frequently requested academic fields and saves the
    result as a horizontal bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_FIELDS = 15

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

    # --- 2. Data Preparation & Aggregation ---
    fields_col = 'AcademicFields'
    if fields_col not in df.columns:
        print(f"Error: Column '{fields_col}' not found in the cleaned dataset.")
        return

    df['FieldList'] = df[fields_col].apply(parse_academic_fields)
    df_exploded = df.explode('FieldList')
    df_exploded.dropna(subset=['FieldList'], inplace=True)
    
    field_counts = df_exploded['FieldList'].value_counts().head(TOP_N_FIELDS)

    print(f"Top {TOP_N_FIELDS} most in-demand academic fields:\n", field_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 12))
    colors = sns.color_palette("mako", len(field_counts))
    sns.barplot(x=field_counts.values, y=field_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'{config.to_persian_numerals(str(TOP_N_FIELDS))} رشته تحصیلی پرتقاضا در بازار کار'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد تکرار در آگهی‌ها', ylabel='رشته تحصیلی')

    rtl_field_labels = [config.rtl_text(label) for label in field_counts.index]
    ax.set_yticklabels(rtl_field_labels, fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val):,}'))
    ax.xaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[config.to_persian_numerals(f'{v:,}') for v in container.datavalues],
            fontproperties=config.nazanin_font,
            fontsize=14,
            padding=5
        )

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "24_academic_fields_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_academic_fields(CLEANED_DATASET_PATH)
