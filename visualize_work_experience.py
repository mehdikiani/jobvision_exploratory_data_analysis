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


def categorize_experience(years: float) -> str:
    """Groups years of experience into career level categories."""
    if pd.isna(years):
        return 'نامشخص'
    if years <= 1:
        return 'کارآموز / بدون سابقه'  # Intern / No Experience
    elif 1 < years <= 3:
        return 'کم‌تجربه (۱ تا ۳ سال)' # Junior
    elif 3 < years <= 7:
        return 'باتجربه (۳ تا ۷ سال)'  # Mid-level
    elif 7 < years <= 10:
        return 'ارشد (۷ تا ۱۰ سال)'    # Senior
    else:
        return 'بسیار باتجربه (بیش از ۱۰ سال)' # Very Experienced


def visualize_work_experience(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of required work
    experience, and saves the result as a bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    EXPERIENCE_OUTLIER_CAP = 20 # Cap experience at 20 years to remove extreme outliers

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
    exp_col = 'RequiredExperienceYears'
    if exp_col not in df.columns:
        print(f"Error: Column '{exp_col}' not found in the cleaned dataset.")
        return

    # Remove outliers
    df_filtered = df[df[exp_col] <= EXPERIENCE_OUTLIER_CAP].copy()
    
    # Apply the categorization function
    df_filtered['ExperienceLevel'] = df_filtered[exp_col].apply(categorize_experience)
    
    exp_counts = df_filtered['ExperienceLevel'].value_counts()
    
    # Define a logical order for the experience levels
    level_order = [
        'کارآموز / بدون سابقه',
        'کم‌تجربه (۱ تا ۳ سال)',
        'باتجربه (۳ تا ۷ سال)',
        'ارشد (۷ تا ۱۰ سال)',
        'بسیار باتجربه (بیش از ۱۰ سال)'
    ]
    
    exp_counts = exp_counts.reindex(level_order).dropna()

    print("Job post count by experience level:\n", exp_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    colors = sns.color_palette("viridis", len(exp_counts))
    sns.barplot(x=exp_counts.values, y=exp_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'توزیع سابقه کار مورد نیاز در آگهی‌ها')
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='سطح تجربه')

    rtl_level_labels = [config.rtl_text(label) for label in exp_counts.index]
    ax.set_yticklabels(rtl_level_labels, fontproperties=config.nazanin_font)

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
    file_name = "07_work_experience_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_work_experience(CLEANED_DATASET_PATH)
