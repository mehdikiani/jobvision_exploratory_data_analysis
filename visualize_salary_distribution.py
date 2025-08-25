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


def visualize_salary_distribution(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the salary distribution, and saves a
    histogram of average salaries.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    OUTLIER_QUANTILE = 0.99
    NUM_BINS = 40

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

    # --- 2. Data Preparation & Cleaning ---
    df.dropna(subset=['MinSalary', 'MaxSalary'], how='all', inplace=True)
    df['AvgSalary'] = df[['MinSalary', 'MaxSalary']].mean(axis=1)
    df_filtered = df[df['AvgSalary'] > 0].copy()

    # --- 3. Outlier Handling ---
    salary_cap = df_filtered['AvgSalary'].quantile(OUTLIER_QUANTILE)
    df_filtered = df_filtered[df_filtered['AvgSalary'] <= salary_cap]
    
    print(f"Salaries are capped at the {int(OUTLIER_QUANTILE*100)}th percentile for visualization.")
    # FIX: Updated the log to reflect the correct unit.
    print(f"Max salary shown in plot: {salary_cap:,.0f} Million Toman")

    # --- 4. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    sns.histplot(df_filtered['AvgSalary'], bins=NUM_BINS, kde=True, color="#2a9d8f", ax=ax)

    # --- 5. Styling and Labeling ---
    title_text = 'تحلیل توزیع حقوق پیشنهادی (میلیون تومان)'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='میانگین حقوق ماهانه (میلیون تومان)', ylabel='تعداد آگهی‌ها')

    # FIX: Removed the division by 1,000,000. The data is already in millions.
    # We format it as a whole number (e.g., '5' instead of '5.0').
    formatter_x = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:,.0f}'))
    ax.xaxis.set_major_formatter(formatter_x)
    
    formatter_y = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val):,}'))
    ax.yaxis.set_major_formatter(formatter_y)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)

    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "03_salary_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_salary_distribution(CLEANED_DATASET_PATH)
