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


def visualize_job_market_trends(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data and analyzes the trend of total job posts over
    time, saving the result as a line chart.

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

    # --- 2. Data Preparation for Time Series ---
    time_col = 'ActivationTime_YEAR_MONTH'
    if time_col not in df.columns:
        print(f"Error: Column '{time_col}' not found in the dataset.")
        return

    # Convert the time column to datetime objects for proper plotting and aggregation
    # 'coerce' will turn any parsing errors into NaT (Not a Time)
    df['Date'] = pd.to_datetime(df[time_col], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    
    # Set the 'Date' column as the index for time-based resampling
    df.set_index('Date', inplace=True)
    
    # Resample the data by month ('M') and count the number of job posts in each month
    monthly_counts = df['RawTitle'].resample('M').count()

    print("Monthly job post counts:\n", monthly_counts)

    # --- 3. 2D Visualization (Line Chart) ---
    fig, ax = plt.subplots(figsize=(18, 9))
    
    sns.lineplot(
        x=monthly_counts.index, 
        y=monthly_counts.values, 
        ax=ax, 
        marker='o', # Add markers to each data point
        linestyle='-',
        color='#023E7D'
    )

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'روند ماهانه آگهی‌های شغلی در طول زمان')
    config.set_labels(ax, xlabel='تاریخ', ylabel='تعداد آگهی‌ها')

    # Format the y-axis with Persian numerals
    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val):,}'))
    ax.yaxis.set_major_formatter(formatter)

    # Set font for all tick labels
    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)
        label.set_rotation(45)
    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "26_job_market_trends.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_job_market_trends(CLEANED_DATASET_PATH)
