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


def visualize_correlation_matrix(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Loads the cleaned data, calculates the correlation matrix for numerical
    features, and saves it as a heatmap.

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

    # --- 2. Data Preparation ---
    # Select only the relevant numerical columns for correlation analysis
    numerical_cols = [
        'MinSalary',
        'MaxSalary',
        'RequiredExperienceYears',
        'RequiredMinAge',
        'RequiredMaxAge'
    ]
    
    # Create a clean dataframe with these columns
    df_numerical = df[numerical_cols].dropna()
    
    # Rename columns to Persian for the plot
    persian_rename_map = {
        'MinSalary': 'حداقل حقوق',
        'MaxSalary': 'حداکثر حقوق',
        'RequiredExperienceYears': 'سابقه کار',
        'RequiredMinAge': 'حداقل سن',
        'RequiredMaxAge': 'حداکثر سن'
    }
    df_numerical.rename(columns=persian_rename_map, inplace=True)

    # --- 3. Correlation Calculation ---
    correlation_matrix = df_numerical.corr()
    print("Correlation Matrix:\n", correlation_matrix)

    # --- 4. 2D Visualization (Heatmap) ---
    fig, ax = plt.subplots(figsize=(12, 10))
    
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f", # Format annotations to two decimal places
        cmap="coolwarm",
        linewidths=.5,
        ax=ax,
        annot_kws={"fontproperties": config.nazanin_font, "size": 14}
    )

    # --- 5. Styling and Labeling ---
    config.set_title(ax, 'ماتریس همبستگی بین متغیرهای عددی')
    
    # Apply RTL processing and fonts to axis labels
    rtl_labels = [config.rtl_text(label) for label in correlation_matrix.columns]
    
    ax.set_xticklabels(rtl_labels, fontproperties=config.nazanin_font, rotation=45, ha='right')
    ax.set_yticklabels(rtl_labels, fontproperties=config.nazanin_font)
    
    # Ensure the color bar numbers are also in Persian
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=14)
    cbar.ax.set_yticklabels([config.to_persian_numerals(label.get_text()) for label in cbar.ax.get_yticklabels()], fontproperties=config.nazanin_font)


    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "16_correlation_matrix.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_correlation_matrix(CLEANED_DATASET_PATH)
