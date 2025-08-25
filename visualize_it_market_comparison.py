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


def visualize_it_market_comparison(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Compares the trend of IT job postings against all other job postings
    over time and saves the result as a multi-line chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    IT_JOB_CATEGORIES = [
        'توسعه نرم افزار و برنامه نویسی',
        'فناوری اطلاعات٬ نرم افزار و سخت افزار', # Using the cleaned version of the label
        'شبکه٬ امنیت و زیرساخت'
    ]

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

    # --- 2. Data Preparation for Time Series ---
    time_col = 'ActivationTime_YEAR_MONTH'
    if time_col not in df.columns:
        print(f"Error: Column '{time_col}' not found in the dataset.")
        return

    df['Date'] = pd.to_datetime(df[time_col], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df.set_index('Date', inplace=True)
    
    # --- 3. Data Aggregation ---
    # Create a boolean column to identify IT jobs
    df['IsIT'] = df['MainJobCategory'].isin(IT_JOB_CATEGORIES)
    
    # Resample and count for both IT and non-IT jobs
    monthly_counts = df.groupby('IsIT')['RawTitle'].resample('M').count().unstack(level=0)
    monthly_counts.columns = ['سایر مشاغل', 'مشاغل فناوری اطلاعات'] # Rename columns for the legend

    print("Monthly job post counts for IT vs. Non-IT sectors:\n", monthly_counts.head())

    # --- 4. 2D Visualization (Multi-line Chart) ---
    fig, ax = plt.subplots(figsize=(18, 9))
    
    sns.lineplot(data=monthly_counts, ax=ax, marker='o', dashes=False, palette=['#5bc0de', '#d9534f'])

    # --- 5. Styling and Labeling ---
    config.set_title(ax, 'مقایسه روند ماهانه مشاغل فناوری اطلاعات با سایر مشاغل')
    config.set_labels(ax, xlabel='تاریخ', ylabel='تعداد آگهی‌ها')

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val):,}'))
    ax.yaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)
        label.set_rotation(45)
    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    handles, labels = ax.get_legend_handles_labels()
    rtl_labels = [config.rtl_text(label) for label in labels]
    ax.legend(handles=handles, labels=rtl_labels, prop=config.nazanin_font, fontsize=16)
        
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "36_it_market_comparison_trends.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_it_market_comparison(CLEANED_DATASET_PATH)
