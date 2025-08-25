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


def visualize_remote_work_distribution(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the prevalence of remote work options,
    and saves the result as a pie chart.

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
    remote_col = 'IsRemote'
    if remote_col not in df.columns:
        print(f"Error: Column '{remote_col}' not found in the cleaned dataset.")
        return

    # The column is boolean, so value_counts() will count True/False
    remote_counts = df[remote_col].value_counts()
    
    # Map the boolean values to meaningful Persian labels for the chart
    remote_counts.index = remote_counts.index.map({True: 'دورکاری', False: 'حضوری'})

    print("Job post count by remote work option:\n", remote_counts)

    # --- 3. 2D Visualization (Pie Chart) ---
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Prepare data for the pie chart
    labels = [config.rtl_text(label) for label in remote_counts.index]
    sizes = remote_counts.values
    colors = sns.color_palette(['#4CAF50', '#FFC107']) # Green for remote, Amber for on-site
    explode = (0.1, 0) # Explode the 'Remote' slice slightly
    
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
    config.set_title(ax, 'نسبت موقعیت‌های شغلی دورکاری در مقابل حضوری')
    
    plt.setp(texts, fontproperties=config.nazanin_font, size=20)
    plt.setp(autotexts, fontproperties=config.nazanin_font, size=18, color="w", weight="bold")
    
    ax.axis('equal')

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "12_remote_work_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_remote_work_distribution(CLEANED_DATASET_PATH)
