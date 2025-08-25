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


def visualize_company_activity(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of job posts by
    company activity type, and saves the result as a bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
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
    activity_col = 'Company_ActivityTypeFa'
    if activity_col not in df.columns:
        print(f"Error: Column '{activity_col}' not found in the cleaned dataset.")
        return

    # Filter out entries where activity type is not specified
    df_filtered = df.dropna(subset=[activity_col])
    
    activity_counts = df_filtered[activity_col].value_counts()

    print("Job post count by company activity type:\n", activity_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    
    colors = sns.color_palette("viridis", len(activity_counts))
    sns.barplot(x=activity_counts.values, y=activity_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'توزیع آگهی‌های شغلی بر اساس نوع فعالیت شرکت')
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='نوع فعالیت')

    # Wrap long labels for better readability
    rtl_activity_labels = [config.rtl_text('\n'.join(label.split(' '))) for label in activity_counts.index]
    ax.set_yticklabels(rtl_activity_labels, fontproperties=config.nazanin_font)

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
    file_name = "19_company_activity_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_company_activity(CLEANED_DATASET_PATH)
