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


def visualize_age_requirements(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of required age,
    and saves the result as a histogram.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    NUM_BINS = 25

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
    age_cols = ['RequiredMinAge', 'RequiredMaxAge']
    if not all(col in df.columns for col in age_cols):
        print(f"Error: Required age columns not found in the dataset.")
        return

    df.dropna(subset=age_cols, how='all', inplace=True)
    df['AvgRequiredAge'] = df[age_cols].mean(axis=1)
    
    # Filter out invalid or outlier age entries
    df_filtered = df[(df['AvgRequiredAge'] >= 18) & (df['AvgRequiredAge'] <= 65)].copy()

    print("Distribution of average required age:\n", df_filtered['AvgRequiredAge'].describe())

    # --- 3. 2D Visualization (Histogram) ---
    fig, ax = plt.subplots(figsize=(16, 9))
    
    sns.histplot(df_filtered['AvgRequiredAge'], bins=NUM_BINS, kde=True, color="#5e548e", ax=ax)

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'توزیع بازه سنی مورد نیاز در آگهی‌ها')
    config.set_labels(ax, xlabel='میانگin سن مورد نیاز', ylabel='تعداد آگهی‌ها')

    formatter_x = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val)}'))
    ax.xaxis.set_major_formatter(formatter_x)
    
    formatter_y = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val):,}'))
    ax.yaxis.set_major_formatter(formatter_y)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "32_age_requirement_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_age_requirements(CLEANED_DATASET_PATH)
