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


def visualize_gender_preference(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads cleaned job data, analyzes the distribution of preferred gender
    in job posts, and saves the result as a pie chart.

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
    gender_col = 'PreferredGender'
    if gender_col not in df.columns:
        print(f"Error: Column '{gender_col}' not found in the cleaned dataset.")
        return

    # Filter out entries where gender is not specified
    df_filtered = df.dropna(subset=[gender_col])
    
    gender_counts = df_filtered[gender_col].value_counts()

    print("Job post count by preferred gender:\n", gender_counts)

    # --- 3. 2D Visualization (Pie Chart) ---
    fig, ax = plt.subplots(figsize=(13, 14))
    
    # Prepare data for the pie chart
    labels = [config.rtl_text(label) for label in gender_counts.index]
    sizes = gender_counts.values
    colors = sns.color_palette("pastel", len(labels))
    
    # FIX: Create the 'explode' tuple dynamically to match the data length.
    # This makes the code robust to changes in the number of categories.
    explode = [0] * len(labels) # Start with no explosion
    # Find the index of specific slices to explode them
    try:
        index_male = gender_counts.index.get_loc('فقط آقا')
        explode[index_male] = 0.05
    except KeyError:
        pass # If the category doesn't exist, do nothing
    try:
        index_female = gender_counts.index.get_loc('فقط خانم')
        explode[index_female] = 0.05
    except KeyError:
        pass

    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct=lambda pct: config.to_persian_numerals(f'{pct:.1f}%'),
        startangle=90,
        colors=colors,
        explode=tuple(explode), # Convert list to tuple for the function
        wedgeprops=dict(edgecolor='w')
    )
    
    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'تحلیل جنسیت مورد نیاز در آگهی‌های شغلی')
    
    plt.setp(texts, fontproperties=config.nazanin_font, size=20)
    plt.setp(autotexts, fontproperties=config.nazanin_font, size=18, color="k", weight="bold")
    
    ax.axis('equal')

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "14_gender_preference.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_gender_preference(CLEANED_DATASET_PATH)
