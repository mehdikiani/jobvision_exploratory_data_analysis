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


def visualize_salary_by_province(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes and compares the average salary across the provinces with the
    most job openings, saving the result as a bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_PROVINCES = 5
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
    # Calculate average salary and handle outliers
    df['AvgSalary'] = df[['MinSalary', 'MaxSalary']].mean(axis=1)
    salary_cap = df['AvgSalary'].quantile(SALARY_OUTLIER_QUANTILE)
    df_filtered = df[(df['AvgSalary'] > 0) & (df['AvgSalary'] <= salary_cap)].copy()

    # Identify the top N provinces by job post count
    top_provinces_list = df_filtered['ProvinceFa'].value_counts().head(TOP_N_PROVINCES).index.tolist()
    print(f"Analyzing salaries for top {TOP_N_PROVINCES} provinces: {top_provinces_list}")

    # Filter the dataframe to include only the top provinces
    df_top_provinces = df_filtered[df_filtered['ProvinceFa'].isin(top_provinces_list)]

    # Calculate the mean salary for each of these provinces
    avg_salary_by_province = df_top_provinces.groupby('ProvinceFa')['AvgSalary'].mean().sort_values(ascending=False)

    print("Average salary by top province (Million Toman):\n", avg_salary_by_province)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    colors = sns.color_palette("coolwarm", len(avg_salary_by_province))
    sns.barplot(x=avg_salary_by_province.values, y=avg_salary_by_province.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'مقایسه میانگین حقوق در {config.to_persian_numerals(str(TOP_N_PROVINCES))} استان پرتقاضا'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='میانگین حقوق ماهانه (میلیون تومان)', ylabel='استان')

    rtl_province_labels = [config.rtl_text(label) for label in avg_salary_by_province.index]
    ax.set_yticklabels(rtl_province_labels, fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{val:,.1f}'))
    ax.xaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)
        
    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[config.to_persian_numerals(f'{v:,.1f}') for v in container.datavalues],
            fontproperties=config.nazanin_font,
            fontsize=14,
            padding=5
        )

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    # This is our 8th analysis script.
    file_name = "08_salary_by_province.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_salary_by_province(CLEANED_DATASET_PATH)
