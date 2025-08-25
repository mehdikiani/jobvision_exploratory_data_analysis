import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
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


def parse_language_skills(skills_json: str):
    """
    Parses the JSON string from the 'LanguageSkills' column and returns a
    list of all language names mentioned.
    """
    if pd.isna(skills_json) or not isinstance(skills_json, str):
        return []
    try:
        skills_list = json.loads(skills_json.replace("'", '"'))
        if isinstance(skills_list, list):
            # Extract 'Languages_TitleFa' for each skill
            valid_skills = [
                skill.get('Languages_TitleFa', '').strip() 
                for skill in skills_list 
                if skill.get('Languages_TitleFa') and skill.get('Languages_TitleFa').strip()
            ]
            return valid_skills
    except (json.JSONDecodeError, TypeError):
        return []
    return []


def visualize_language_skills(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the most frequently requested language skills and saves the
    result as a horizontal bar chart.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_LANGUAGES = 5

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
    skills_col = 'LanguageSkills'
    if skills_col not in df.columns:
        print(f"Error: Column '{skills_col}' not found in the cleaned dataset.")
        return

    df['LanguageList'] = df[skills_col].apply(parse_language_skills)
    df_languages = df.explode('LanguageList')
    df_languages.dropna(subset=['LanguageList'], inplace=True)
    
    language_counts = df_languages['LanguageList'].value_counts().head(TOP_N_LANGUAGES)

    print(f"Top {TOP_N_LANGUAGES} most in-demand language skills:\n", language_counts)

    # --- 3. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 9))
    colors = sns.color_palette("cool", len(language_counts))
    sns.barplot(x=language_counts.values, y=language_counts.index, palette=colors, ax=ax, orient='h')

    # --- 4. Styling and Labeling ---
    title_text = f'{config.to_persian_numerals(str(TOP_N_LANGUAGES))} مهارت زبانی مورد نیاز در بازار کار'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد تکرار در آگهی‌ها', ylabel='زبان')

    rtl_skill_labels = [config.rtl_text(label) for label in language_counts.index]
    ax.set_yticklabels(rtl_skill_labels, fontproperties=config.nazanin_font)

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
    file_name = "20_language_skills_distribution.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_language_skills(CLEANED_DATASET_PATH)
