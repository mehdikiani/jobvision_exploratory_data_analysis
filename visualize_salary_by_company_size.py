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
    """
    if not isinstance(size_str, str):
        return 'نامشخص'
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


def visualize_salary_by_company_size(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the relationship between company size and salary distribution,
    saving the result as a box plot.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    SALARY_OUTLIER_QUANTILE = 0.98

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
    df['AvgSalary'] = df[['MinSalary', 'MaxSalary']].mean(axis=1)
    salary_cap = df['AvgSalary'].quantile(SALARY_OUTLIER_QUANTILE)
    df_filtered = df[(df['AvgSalary'] > 0) & (df['AvgSalary'] <= salary_cap)].copy()

    df_filtered['Standardized_Size'] = df_filtered['Company_SizeFa'].apply(standardize_company_size)
    df_filtered = df_filtered[df_filtered['Standardized_Size'] != 'نامشخص']
    
    size_order = [
        'زیر ۱۰ نفر', '۱۱ تا ۵۰ نفر', '۵۱ تا ۲۰۰ نفر', 
        '۲۰۱ تا ۵۰۰ نفر', '۵۰۱ تا ۱۰۰۰ نفر', 'بیش از ۱۰۰۰ نفر'
    ]

    # --- 3. 2D Visualization (Box Plot) ---
    fig, ax = plt.subplots(figsize=(18, 10))
    
    sns.boxplot(
        x='AvgSalary',
        y='Standardized_Size',
        data=df_filtered,
        order=size_order,
        palette='viridis',
        ax=ax,
        orient='h'
    )

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'مقایسه توزیع حقوق بر اساس اندازه شرکت')
    config.set_labels(ax, xlabel='میانگین حقوق ماهانه (میلیون تومان)', ylabel='اندازه شرکت')

    rtl_size_labels = [config.rtl_text(label) for label in size_order]
    ax.set_yticklabels(rtl_size_labels, fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:,.0f}'))
    ax.xaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "29_salary_by_company_size.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_salary_by_company_size(CLEANED_DATASET_PATH)
