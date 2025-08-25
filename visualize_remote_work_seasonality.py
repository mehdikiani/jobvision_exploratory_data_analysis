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


def visualize_remote_work_seasonality(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the seasonal trend of remote job postings by month of the year.

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

    # --- 2. Data Preparation ---
    time_col = 'ActivationTime_YEAR_MONTH'
    if time_col not in df.columns:
        print(f"Error: Column '{time_col}' not found in the dataset.")
        return

    df['Date'] = pd.to_datetime(df[time_col], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    
    # Extract the month number (1-12) from the date
    df['Month'] = df['Date'].dt.month
    
    # --- 3. Data Aggregation ---
    # Group by month and calculate the average percentage of remote jobs
    monthly_remote_percentage = df.groupby('Month')['IsRemote'].mean() * 100

    print("Average percentage of remote jobs by month of the year:\n", monthly_remote_percentage)

    # --- 4. 2D Visualization (Line Chart) ---
    fig, ax = plt.subplots(figsize=(18, 9))
    
    sns.lineplot(
        x=monthly_remote_percentage.index, 
        y=monthly_remote_percentage.values, 
        ax=ax, 
        marker='o',
        linestyle='-',
        color='#2a9d8f'
    )

    # --- 5. Styling and Labeling ---
    config.set_title(ax, 'روند فصلی تقاضا برای مشاغل دورکاری (بر اساس ماه)')
    config.set_labels(ax, xlabel='ماه', ylabel='درصد آگهی‌های دورکاری')

    # Create Persian month labels for the x-axis
    persian_months = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([config.rtl_text(m) for m in persian_months], fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:.1f}%'))
    ax.yaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_rotation(45)
    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "38_remote_work_seasonality.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_remote_work_seasonality(CLEANED_DATASET_PATH)
