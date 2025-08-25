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


def visualize_top_provinces_industries(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the industry distribution for each of the top 5 provinces
    and saves a separate bar chart for each.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_PROVINCES = 5
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

    # --- 2. Identify Top Provinces ---
    top_provinces = df['ProvinceFa'].value_counts().head(TOP_N_PROVINCES).index
    print(f"Identified top {TOP_N_PROVINCES} provinces: {top_provinces.tolist()}")

    # --- 3. Loop and Analyze Each Province ---
    for i, province in enumerate(top_provinces):
        print("-" * 50)
        print(f"Analyzing province: {province} ({i+1}/{TOP_N_PROVINCES})")

        # Filter the dataset for the current province
        df_province = df[df['ProvinceFa'] == province].copy()

        industry_col = 'Company_IndustryFa'
        if industry_col not in df_province.columns:
            print(f"Skipping province {province}, column '{industry_col}' not found.")
            continue

        df_province.dropna(subset=[industry_col], inplace=True)
        
        # Split and explode industries
        df_province['IndustryList'] = df_province[industry_col].str.split(',')
        df_exploded = df_province.explode('IndustryList')
        df_exploded['IndustryList'] = df_exploded['IndustryList'].str.strip()
        
        industry_counts = df_exploded['IndustryList'].value_counts().head(TOP_N_INDUSTRIES)

        print(f"Top {TOP_N_INDUSTRIES} industries in {province}:\n", industry_counts)

        # --- Visualization ---
        fig, ax = plt.subplots(figsize=(16, 10))
        colors = sns.color_palette("cubehelix_r", len(industry_counts))
        sns.barplot(x=industry_counts.values, y=industry_counts.index, palette=colors, ax=ax, orient='h')

        # --- Styling and Labeling ---
        title_text = f'توزیع آگهی‌ها در صنایع برتر استان {province}'
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

        # --- Save Figure to File ---
        os.makedirs(output_dir, exist_ok=True)
        # Sanitize province name for filename
        safe_province_name = province.replace(" ", "_")
        file_name = f"31_{i+1}_industry_distribution_{safe_province_name}.png"
        output_path = os.path.join(output_dir, file_name)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Figure saved successfully to: {output_path}")

    print("-" * 50)
    print("All analyses for top provinces are complete.")


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_top_provinces_industries(CLEANED_DATASET_PATH)
