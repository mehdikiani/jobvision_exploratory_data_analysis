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


def visualize_company_industry(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of job posts by
    company industry, and saves the result as a bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_INDUSTRIES = 12

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
    industry_col = 'Company_IndustryFa'
    if industry_col not in df.columns:
        print(f"Error: Column '{industry_col}' not found in the cleaned dataset.")
        return

    # Drop rows with no industry information
    df_industries = df.dropna(subset=[industry_col])
    
    # Split comma-separated strings into lists of industries and explode the dataframe
    df_industries['IndustryList'] = df_industries[industry_col].str.split(',')
    df_exploded = df_industries.explode('IndustryList')
    
    # Trim whitespace from each industry
    df_exploded['IndustryList'] = df_exploded['IndustryList'].str.strip()
    
    # Count the occurrences of each industry
    industry_counts = df_exploded['IndustryList'].value_counts().head(TOP_N_INDUSTRIES)

    print(f"Top {TOP_N_INDUSTRIES} most common company industries:\n", industry_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 10))
    colors = sns.color_palette("plasma", len(industry_counts))
    sns.barplot(x=industry_counts.values, y=industry_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'توزیع آگهی‌ها در {config.to_persian_numerals(str(TOP_N_INDUSTRIES))} صنعت برتر'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد آگهی‌ها', ylabel='صنعت')

    rtl_industry_labels = [config.rtl_text(label) for label in industry_counts.index]
    ax.set_yticklabels(rtl_industry_labels, fontproperties=config.nazanin_font)

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
    file_name = "22_company_industry_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_company_industry(CLEANED_DATASET_PATH)
