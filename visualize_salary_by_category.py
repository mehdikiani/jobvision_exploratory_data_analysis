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


def visualize_salary_by_category(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes and compares the average salary across the most in-demand
    job categories, saving the result as a bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_CATEGORIES = 10
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

    # Identify the top N job categories by post count
    top_categories_list = df_filtered['MainJobCategory'].value_counts().head(TOP_N_CATEGORIES).index.tolist()
    print(f"Analyzing salaries for top {TOP_N_CATEGORIES} categories: {top_categories_list}")

    # Filter the dataframe to include only the top categories
    df_top_categories = df_filtered[df_filtered['MainJobCategory'].isin(top_categories_list)]

    # Calculate the mean salary for each of these categories
    avg_salary_by_category = df_top_categories.groupby('MainJobCategory')['AvgSalary'].mean().sort_values(ascending=False)

    print("Average salary by top job category (Million Toman):\n", avg_salary_by_category)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 10))
    colors = sns.color_palette("inferno", len(avg_salary_by_category))
    sns.barplot(x=avg_salary_by_category.values, y=avg_salary_by_category.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'مقایسه میانگین حقوق در {config.to_persian_numerals(str(TOP_N_CATEGORIES))} دسته‌بندی شغلی پرتقاضا'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='میانگین حقوق ماهانه (میلیون تومان)', ylabel='دسته‌بندی شغلی')

    rtl_category_labels = [config.rtl_text(label) for label in avg_salary_by_category.index]
    ax.set_yticklabels(rtl_category_labels, fontproperties=config.nazanin_font)

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
    file_name = "10_salary_by_category.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_salary_by_category(CLEANED_DATASET_PATH)
