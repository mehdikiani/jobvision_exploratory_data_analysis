import pandas as pd
import numpy as np
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


def visualize_province_distribution(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads the CLEANED job post data, visualizes the geographic
    distribution using a 2D horizontal bar chart, and saves the plot.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    # CLEAN CODE: Define the number of top items to show in one place.
    TOP_N = 12

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
    location_col = 'ProvinceFa'
    if location_col not in df.columns:
        print(f"Error: Column '{location_col}' not found in the cleaned dataset.")
        return

    province_counts = df[location_col].value_counts()
    top_provinces = province_counts.head(TOP_N)
    
    # Use the TOP_N variable in the log message.
    print(f"Top {TOP_N} provinces by job post count:\n", top_provinces)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = sns.color_palette("viridis_r", len(top_provinces))
    sns.barplot(x=top_provinces.values, y=top_provinces.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    # CLEAN CODE: Use the TOP_N variable to dynamically create the title.
    title_text = f'توزیع جغرافیایی موقعیت‌های شغلی در {config.to_persian_numerals(str(TOP_N))} استان برتر'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='استان')

    rtl_province_labels = [config.rtl_text(label) for label in top_provinces.index]
    ax.set_yticklabels(rtl_province_labels, fontproperties=config.nazanin_font)

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
    file_name = "01_province_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_province_distribution(CLEANED_DATASET_PATH)
