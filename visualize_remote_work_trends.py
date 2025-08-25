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


def visualize_remote_work_trends(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data and analyzes the trend of remote job proportions
    over time, saving the result as a line chart.

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

    df['Date'] = pd.to_datetime(df[time_col], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df.set_index('Date', inplace=True)
    
    # Resample by month. The mean() of a boolean series gives the proportion of True values.
    # We multiply by 100 to get a percentage.
    monthly_remote_percentage = df['IsRemote'].resample('M').mean() * 100

    print("Monthly percentage of remote job posts:\n", monthly_remote_percentage)

    # --- 3. 2D Visualization (Line Chart) ---
    fig, ax = plt.subplots(figsize=(18, 9))
    
    sns.lineplot(
        x=monthly_remote_percentage.index, 
        y=monthly_remote_percentage.values, 
        ax=ax, 
        marker='o',
        linestyle='-',
        color='#4CAF50' # Green for remote work
    )

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'روند رواج موقعیت‌های شغلی دورکاری در طول زمان')
    config.set_labels(ax, xlabel='تاریخ', ylabel='درصد آگهی‌های دورکاری')

    # Format the y-axis to show a percentage sign
    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:.0f}%'))
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
    file_name = "27_remote_work_trends.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_remote_work_trends(CLEANED_DATASET_PATH)
