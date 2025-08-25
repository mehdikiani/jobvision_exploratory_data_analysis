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


def visualize_military_service_requirement(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the requirement for a military service
    card, and saves the result as a pie chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
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
    military_col = 'RequiredMilitaryServiceCard'
    if military_col not in df.columns:
        print(f"Error: Column '{military_col}' not found in the cleaned dataset.")
        return

    # Filter out jobs that are only for women, as the requirement is not applicable
    df_filtered = df[df['PreferredGender'] != 'فقط خانم'].copy()
    
    military_counts = df_filtered[military_col].value_counts()
    
    # Map boolean values to meaningful Persian labels
    military_counts.index = military_counts.index.map({True: 'الزامی', False: 'الزامی نیست'})

    print("Job post count by military service requirement:\n", military_counts)

    # --- 3. 2D Visualization (Pie Chart) ---
    fig, ax = plt.subplots(figsize=(12, 12))
    
    labels = [config.rtl_text(label) for label in military_counts.index]
    sizes = military_counts.values
    colors = sns.color_palette(['#d9534f','#5bc0de']) # Red for required, Blue for not
    explode = (0.1, 0) if 'الزامی' in military_counts.index and military_counts.index[0] == 'الزامی' else (0, 0.1)

    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct=lambda pct: config.to_persian_numerals(f'{pct:.1f}%'),
        startangle=90,
        colors=colors,
        explode=explode,
        wedgeprops=dict(edgecolor='w')
    )
    
    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'وضعیت نظام وظیفه مورد نیاز در آگهی‌ها')
    
    plt.setp(texts, fontproperties=config.nazanin_font, size=20)
    plt.setp(autotexts, fontproperties=config.nazanin_font, size=18, color="w", weight="bold")
    
    ax.axis('equal')

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "17_military_service_requirement.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_military_service_requirement(CLEANED_DATASET_PATH)
