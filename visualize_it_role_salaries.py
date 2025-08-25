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


def standardize_it_role(title: str) -> str:
    """
    Standardizes raw IT job titles into common Persian categories.
    """
    if not isinstance(title, str):
        return 'سایر'
    
    title = title.lower().replace('-', ' ').replace('_', ' ')
    
    # FIX: Return fully Persian labels to solve font rendering issues.
    if any(keyword in title for keyword in ['back end', 'backend', 'بک اند']):
        return 'توسعه دهنده بک-اند'
    if any(keyword in title for keyword in ['front end', 'frontend', 'فرانت اند']):
        return 'توسعه دهنده فرانت-اند'
    if any(keyword in title for keyword in ['full stack', 'fullstack', 'فول استک']):
        return 'توسعه دهنده فول-استک'
    if any(keyword in title for keyword in ['android', 'اندروید']):
        return 'توسعه دهنده اندروید'
    if any(keyword in title for keyword in ['ios']):
        return 'توسعه دهنده iOS'
    if any(keyword in title for keyword in ['devops', ' دواپس']):
        return 'مهندس DevOps'
    if any(keyword in title for keyword in ['data scientist', 'دانشمند داده', 'تحلیلگر داده']):
        return 'دانشمند / تحلیلگر داده'
    if any(keyword in title for keyword in ['network', 'شبکه']):
        return 'مهندس شبکه'
    return 'سایر'


def visualize_it_role_salaries(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes and compares salary distributions for top IT job roles.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    SALARY_OUTLIER_QUANTILE = 0.98
    MIN_ROLE_COUNT = 500
    IT_JOB_CATEGORIES = [
        'توسعه نرم افزار و برنامه نویسی',
        'فناوری اطلاعات / نرم افزار و سخت افزار',
        'شبکه / امنیت / زیرساخت',
        'DevOps / Sys-Admin'
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

    # --- 2. Data Preparation ---
    df_it = df[df['MainJobCategory'].isin(IT_JOB_CATEGORIES)].copy()
    
    df_it['AvgSalary'] = df_it[['MinSalary', 'MaxSalary']].mean(axis=1)
    salary_cap = df_it['AvgSalary'].quantile(SALARY_OUTLIER_QUANTILE)
    df_it_filtered = df_it[(df_it['AvgSalary'] > 0) & (df_it['AvgSalary'] <= salary_cap)].copy()

    df_it_filtered['StandardizedRole'] = df_it_filtered['RawTitle'].apply(standardize_it_role)
    
    role_counts = df_it_filtered['StandardizedRole'].value_counts()
    top_roles = role_counts[role_counts >= MIN_ROLE_COUNT].index
    df_final = df_it_filtered[df_it_filtered['StandardizedRole'].isin(top_roles)]

    print("Top IT roles being analyzed:\n", top_roles.tolist())

    # --- 3. 2D Visualization (Box Plot) ---
    fig, ax = plt.subplots(figsize=(18, 10))
    
    sns.boxplot(
        x='AvgSalary',
        y='StandardizedRole',
        data=df_final,
        palette='mako',
        ax=ax,
        orient='h'
    )

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'مقایسه توزیع حقوق برای نقش‌های کلیدی فناوری اطلاعات')
    config.set_labels(ax, xlabel='میانگین حقوق ماهانه (میلیون تومان)', ylabel='نقش شغلی')

    # Now that all labels are Persian, this will work perfectly.
    current_labels = [label.get_text() for label in ax.get_yticklabels()]
    rtl_role_labels = [config.rtl_text(label) for label in current_labels]
    ax.set_yticklabels(rtl_role_labels, fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:,.0f}'))
    ax.xaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "34_it_role_salaries.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_it_role_salaries(CLEANED_DATASET_PATH)
