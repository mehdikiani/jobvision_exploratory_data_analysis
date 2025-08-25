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


def visualize_job_benefits(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the most frequently offered job benefits and saves the
    result as a horizontal bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_BENEFITS = 10

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
    benefits_col = 'BenefitFa'
    if benefits_col not in df.columns:
        print(f"Error: Column '{benefits_col}' not found in the cleaned dataset.")
        return

    # Drop rows with no benefit information
    df_benefits = df.dropna(subset=[benefits_col])
    
    # Split comma-separated strings into lists of benefits and explode the dataframe
    df_benefits['BenefitList'] = df_benefits[benefits_col].str.split(',')
    df_exploded = df_benefits.explode('BenefitList')
    
    # Trim whitespace from each benefit to handle inconsistencies
    df_exploded['BenefitList'] = df_exploded['BenefitList'].str.strip()
    
    # Count the occurrences of each benefit
    benefit_counts = df_exploded['BenefitList'].value_counts().head(TOP_N_BENEFITS)

    print(f"Top {TOP_N_BENEFITS} most common job benefits:\n", benefit_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 10))
    colors = sns.color_palette("muted", len(benefit_counts))
    sns.barplot(x=benefit_counts.values, y=benefit_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'{config.to_persian_numerals(str(TOP_N_BENEFITS))} مزایای شغلی رایج در آگهی‌ها'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد تکرار در آگهی‌ها', ylabel='مزایا')

    rtl_benefit_labels = [config.rtl_text(label) for label in benefit_counts.index]
    ax.set_yticklabels(rtl_benefit_labels, fontproperties=config.nazanin_font)

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
    file_name = "21_job_benefits_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_job_benefits(CLEANED_DATASET_PATH)
