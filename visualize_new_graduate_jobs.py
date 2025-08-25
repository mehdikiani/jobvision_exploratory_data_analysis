import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
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


def visualize_new_graduate_jobs(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes job opportunities for new graduates (0-2 years experience)
    and visualizes the top job categories for them.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_CATEGORIES = 10
    MAX_EXPERIENCE_FOR_JUNIOR = 2

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
    # Filter for entry-level positions
    df_junior = df[df['RequiredExperienceYears'] <= MAX_EXPERIENCE_FOR_JUNIOR].copy()
    
    category_col = 'MainJobCategory'
    if category_col not in df_junior.columns:
        print(f"Error: Column '{category_col}' not found in the dataset.")
        return
        
    # Count job categories within this entry-level subset
    junior_job_counts = df_junior[category_col].value_counts().head(TOP_N_CATEGORIES)

    print(f"Top {TOP_N_CATEGORIES} job categories for new graduates (<= {MAX_EXPERIENCE_FOR_JUNIOR} years experience):\n", junior_job_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 10))
    colors = sns.color_palette("viridis_r", len(junior_job_counts))
    sns.barplot(x=junior_job_counts.values, y=junior_job_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'فرصت‌های شغلی برای فارغ‌التحصیلان (کمتر از {config.to_persian_numerals(str(MAX_EXPERIENCE_FOR_JUNIOR))} سال سابقه)'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='دسته‌بندی شغلی')

    rtl_category_labels = [config.rtl_text(label.replace(' / ', '، ')) for label in junior_job_counts.index]
    ax.set_yticklabels(rtl_category_labels, fontproperties=config.nazanin_font)

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
    file_name = "25_new_graduate_jobs.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_new_graduate_jobs(CLEANED_DATASET_PATH)
