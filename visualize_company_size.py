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

def standardize_company_size(size_str: str) -> str:
    """
    A robust function to clean and standardize company size strings.
    It handles common variations in spacing and wording.
    """
    if not isinstance(size_str, str):
        return 'نامشخص'
    
    # Normalize the string by removing spaces and common characters
    normalized_str = size_str.replace(' ', '').replace('تا', '').replace('نفر', '')

    if 'زیر۱۰' in normalized_str or 'زیر10' in normalized_str:
        return 'زیر ۱۰ نفر'
    elif '۱۱۵۰' in normalized_str or '1150' in normalized_str:
        return '۱۱ تا ۵۰ نفر'
    elif '۵۱২০০' in normalized_str or '51200' in normalized_str:
        return '۵۱ تا ۲۰۰ نفر'
    elif '۲۰۱۵۰۰' in normalized_str or '201500' in normalized_str:
        return '۲۰۱ تا ۵۰۰ نفر'
    elif '۵۰۱۱۰۰۰' in normalized_str or '5011000' in normalized_str:
        return '۵۰۱ تا ۱۰۰۰ نفر'
    elif 'بیشاز۱۰۰۰' in normalized_str or 'بیشاز1000' in normalized_str:
        return 'بیش از ۱۰۰۰ نفر'
    else:
        return 'نامشخص'


def visualize_company_size_distribution(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of job posts by
    company size, and saves the result as a horizontal bar chart.
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
    size_col = 'Company_SizeFa'
    if size_col not in df.columns:
        print(f"Error: Column '{size_col}' not found in the cleaned dataset.")
        return

    # FIX: Apply the robust standardization function to the column.
    df['Standardized_Size'] = df[size_col].apply(standardize_company_size)
    
    # Filter out entries where size is not specified
    df_filtered = df[df['Standardized_Size'] != 'نامشخص']
    
    size_counts = df_filtered['Standardized_Size'].value_counts()
    
    # Define the logical order for the standardized categories
    size_order = [
        'زیر ۱۰ نفر',
        '۱۱ تا ۵۰ نفر',
        '۵۱ تا ۲۰۰ نفر',
        '۲۰۱ تا ۵۰۰ نفر',
        '۵۰۱ تا ۱۰۰۰ نفر',
        'بیش از ۱۰۰۰ نفر'
    ]
    
    # Reorder the counts according to our defined logical order
    size_counts = size_counts.reindex(size_order).dropna()

    print("Job post count by company size:\n", size_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    
    colors = sns.color_palette("magma_r", len(size_counts))
    sns.barplot(x=size_counts.values, y=size_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'توزیع آگهی‌های شغلی بر اساس اندازه شرکت')
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='اندازه شرکت')

    rtl_size_labels = [config.rtl_text(label) for label in size_counts.index]
    ax.set_yticklabels(rtl_size_labels, fontproperties=config.nazanin_font)

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
    file_name = "05_company_size_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_company_size_distribution(CLEANED_DATASET_PATH)
