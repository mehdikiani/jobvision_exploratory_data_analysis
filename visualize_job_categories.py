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
    # Define dummy functions to prevent crashes
    class DummyFont:
        def get_name(self): return "Arial"
    class config:
        titr_font = nazanin_font = DummyFont()
        def rtl_text(t): return t
        def set_title(ax, t): ax.set_title(t)
        def set_labels(ax, x, y): ax.set_xlabel(x); ax.set_ylabel(y)
        def to_persian_numerals(n): return str(n)


def visualize_job_category_distribution(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads the cleaned job data, analyzes the distribution of main job
    categories, and saves a 2D bar chart of the most in-demand roles.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N = 10

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

    # --- 2. Data Aggregation ---
    category_col = 'MainJobCategory'
    if category_col not in df.columns:
        print(f"Error: Column '{category_col}' not found in the cleaned dataset.")
        return

    # Drop rows where the category is 'نامشخص' (Unknown) or missing
    df_filtered = df[df[category_col] != 'نامشخص'].dropna(subset=[category_col])
    
    category_counts = df_filtered[category_col].value_counts()
    top_categories = category_counts.head(TOP_N)
    
    print(f"Top {TOP_N} job categories by post count:\n", top_categories)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(20, 14))
    colors = sns.color_palette("plasma_r", len(top_categories))
    sns.barplot(x=top_categories.values, y=top_categories.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'پرتقاضاترین دسته‌بندی‌های شغلی (بر اساس {config.to_persian_numerals(str(TOP_N))} مورد برتر)'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='دسته‌بندی شغلی')

    # Some category names can be long; this wraps them for better display.
    rtl_category_labels = [config.rtl_text(label.replace(' / ', '، ')) for label in top_categories.index]
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
    file_name = "02_job_category_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_job_category_distribution(CLEANED_DATASET_PATH)
