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


def visualize_it_remote_comparison(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Compares the percentage of remote jobs in the IT sector versus all
    other sectors combined.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    IT_JOB_CATEGORIES = [
        'توسعه نرم افزار و برنامه نویسی',
        'فناوری اطلاعات٬ نرم افزار و سخت افزار',
        'شبکه٬ امنیت و زیرساخت',
        'دواپس و ادمین سیستم'
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

    # --- 2. Data Preparation & Aggregation ---
    df['Sector'] = df['MainJobCategory'].apply(
        lambda x: 'فناوری اطلاعات' if x in IT_JOB_CATEGORIES else 'سایر مشاغل'
    )
    
    # Calculate the percentage of remote jobs in each sector
    remote_percentage = df.groupby('Sector')['IsRemote'].mean() * 100
    remote_percentage = remote_percentage.sort_values(ascending=False)

    print("Percentage of remote jobs by sector:\n", remote_percentage)

    # --- 3. 2D Visualization (Bar Chart) ---
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#d9534f', '#5bc0de']
    sns.barplot(x=remote_percentage.index, y=remote_percentage.values, palette=colors, ax=ax)

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'مقایسه درصد مشاغل دورکاری در بخش فناوری اطلاعات با سایر بخش‌ها')
    config.set_labels(ax, xlabel='بخش شغلی', ylabel='درصد آگهی‌های دورکاری')

    rtl_sector_labels = [config.rtl_text(label) for label in remote_percentage.index]
    ax.set_xticklabels(rtl_sector_labels, fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:.0f}%'))
    ax.yaxis.set_major_formatter(formatter)

    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[config.to_persian_numerals(f'{v:.1f}%') for v in container.datavalues],
            fontproperties=config.nazanin_font,
            fontsize=16,
            padding=3
        )

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "37_it_remote_comparison.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_it_remote_comparison(CLEANED_DATASET_PATH)
