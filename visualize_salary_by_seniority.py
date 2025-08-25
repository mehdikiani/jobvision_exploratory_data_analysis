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


def categorize_seniority(title: str) -> str:
    """
    Infers the seniority level from a job title based on keywords.
    """
    if not isinstance(title, str):
        return 'نامشخص'
    
    title = title.lower()
    
    # Keywords for different levels
    manager_keywords = ['manager', 'مدیر', 'head', 'سرپرست', 'chief', 'رئیس']
    senior_keywords = ['senior', 'ارشد']
    junior_keywords = ['junior', 'کارآموز', 'intern', 'تازه']
    
    # FIX: Return fully Persian labels to prevent font rendering issues.
    if any(keyword in title for keyword in manager_keywords):
        return 'مدیر / سرپرست'
    elif any(keyword in title for keyword in senior_keywords):
        return 'ارشد'
    elif any(keyword in title for keyword in junior_keywords):
        return 'مقدماتی / کارآموز'
    else:
        return 'سطح میانی'


def visualize_salary_by_seniority(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the relationship between inferred seniority level and average
    salary, saving the result as a bar chart.

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

    # --- 2. Data Preparation & Aggregation ---
    df['AvgSalary'] = df[['MinSalary', 'MaxSalary']].mean(axis=1)
    salary_cap = df['AvgSalary'].quantile(SALARY_OUTLIER_QUANTILE)
    df_filtered = df[(df['AvgSalary'] > 0) & (df['AvgSalary'] <= salary_cap)].copy()

    df_filtered['SeniorityLevel'] = df_filtered['RawTitle'].apply(categorize_seniority)
    
    avg_salary_by_seniority = df_filtered.groupby('SeniorityLevel')['AvgSalary'].mean()
    
    # FIX: Update the order to match the new, fully Persian labels.
    seniority_order = [
        'مقدماتی / کارآموز',
        'سطح میانی',
        'ارشد',
        'مدیر / سرپرست'
    ]
    avg_salary_by_seniority = avg_salary_by_seniority.reindex(seniority_order).dropna()

    print("Average salary by seniority level (Million Toman):\n", avg_salary_by_seniority)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    colors = sns.color_palette("cubehelix", len(avg_salary_by_seniority))
    sns.barplot(x=avg_salary_by_seniority.index, y=avg_salary_by_seniority.values, palette=colors, ax=ax)

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'رابطه سطح ارشدیت و حقوق پیشنهادی')
    config.set_labels(ax, xlabel='سطح ارشدیت', ylabel='میانگین حقوق ماهانه (میلیون تومان)')

    rtl_seniority_labels = [config.rtl_text(label) for label in avg_salary_by_seniority.index]
    ax.set_xticklabels(rtl_seniority_labels, fontproperties=config.nazanin_font, rotation=0)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:,.1f}'))
    ax.yaxis.set_major_formatter(formatter)

    for label in ax.get_yticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[config.to_persian_numerals(f'{v:,.1f}') for v in container.datavalues],
            fontproperties=config.nazanin_font,
            fontsize=14,
            padding=3
        )

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "09_salary_by_seniority.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_salary_by_seniority(CLEANED_DATASET_PATH)
