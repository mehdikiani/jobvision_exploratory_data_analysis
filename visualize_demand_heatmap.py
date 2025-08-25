import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

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


def visualize_demand_heatmap(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Creates a heatmap to visualize the concentration of top job categories
    within the top provinces.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_PROVINCES = 5
    TOP_N_CATEGORIES = 10

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

    # --- 2. Data Preparation & Filtering ---
    # Identify top provinces and categories to keep the heatmap focused
    top_provinces = df['ProvinceFa'].value_counts().head(TOP_N_PROVINCES).index
    top_categories = df['MainJobCategory'].value_counts().head(TOP_N_CATEGORIES).index

    # Filter the dataframe to only include these top entities
    df_filtered = df[df['ProvinceFa'].isin(top_provinces) & df['MainJobCategory'].isin(top_categories)]
    
    # --- 3. Data Aggregation (Pivot Table) ---
    # Create a pivot table to count jobs at the intersection of province and category
    heatmap_data = df_filtered.pivot_table(
        index='MainJobCategory',
        columns='ProvinceFa',
        values='RawTitle', # Any non-null column can be used for counting
        aggfunc='count'
    ).fillna(0) # Fill any missing intersections with 0

    # Reorder columns to match the original popularity ranking
    heatmap_data = heatmap_data[top_provinces]

    print("Heatmap data (Job Counts):\n", heatmap_data)

    # --- 4. 2D Visualization (Heatmap) ---
    fig, ax = plt.subplots(figsize=(18, 14))
    
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".0f", # Format annotations as integers
        linewidths=.5,
        cmap="YlGnBu",
        ax=ax,
        annot_kws={"fontproperties": config.nazanin_font, "size": 14}
    )

    # --- 5. Styling and Labeling ---
    title_text = 'نقشه حرارتی تقاضای شغلی (استان در مقابل دسته‌بندی شغلی)'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='استان', ylabel='دسته‌بندی شغلی')

    # Apply RTL processing and fonts to axis labels
    rtl_col_labels = [config.rtl_text(label) for label in heatmap_data.columns]
    rtl_row_labels = [config.rtl_text(label.replace(' / ', '، ')) for label in heatmap_data.index]
    
    ax.set_xticklabels(rtl_col_labels, fontproperties=config.nazanin_font, rotation=45, ha='right')
    ax.set_yticklabels(rtl_row_labels, fontproperties=config.nazanin_font)

    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "13_demand_heatmap.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_demand_heatmap(CLEANED_DATASET_PATH)
