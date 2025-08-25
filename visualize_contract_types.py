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


def visualize_contract_types(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of different work
    contract types, and saves the result as a pie chart.

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
    contract_col = 'WorkTypeFa'
    if contract_col not in df.columns:
        print(f"Error: Column '{contract_col}' not found in the cleaned dataset.")
        return

    # Filter out entries where contract type is not specified
    df_filtered = df.dropna(subset=[contract_col])
    df_filtered = df_filtered[df_filtered[contract_col] != 'نامشخص']
    
    contract_counts = df_filtered[contract_col].value_counts()

    print("Job post count by contract type:\n", contract_counts)

    # --- 3. 2D Visualization (Pie Chart) ---
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Prepare data for the pie chart
    labels = [config.rtl_text(label) for label in contract_counts.index]
    sizes = contract_counts.values
    colors = sns.color_palette("rocket", len(labels))
    
    # Create the pie chart with percentages
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct=lambda pct: config.to_persian_numerals(f'{pct:.1f}%'),
        startangle=140,
        colors=colors,
        wedgeprops=dict(edgecolor='w')
    )
    
    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'انواع قراردادهای کاری رایج')
    
    # Improve styling of the pie chart labels and percentages
    plt.setp(texts, fontproperties=config.nazanin_font, size=18)
    plt.setp(autotexts, fontproperties=config.nazanin_font, size=16, color="w", weight="bold")
    
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "06_contract_type_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_contract_types(CLEANED_DATASET_PATH)
