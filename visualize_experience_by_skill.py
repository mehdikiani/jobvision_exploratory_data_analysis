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


def parse_software_skills(skills_json: str):
    """
    Parses the JSON string from the 'SoftwareSkills' column and returns a
    list of all skill names mentioned.
    """
    if pd.isna(skills_json) or not isinstance(skills_json, str):
        return []
    try:
        skills_list = json.loads(skills_json.replace("'", '"'))
        if isinstance(skills_list, list):
            valid_skills = [
                skill.get('TitleFa', '').strip() 
                for skill in skills_list 
                if skill.get('TitleFa') and skill.get('TitleFa').strip()
            ]
            return valid_skills
    except (json.JSONDecodeError, TypeError):
        return []
    return []


def visualize_experience_by_skill(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes the distribution of required experience for key IT skills.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    # FIX: Use the Persian names for skills as they appear in the dataset.
    KEY_IT_SKILLS = [
        'اچ تی ام ال,سی اس اس', 'جاوا اسکریپت', 'ری اکت', 'انگولار', 'ویو',
        'پایتون', 'پی اچ پی', 'جاوا', 'اس کیو ال', 'گیت'
    ]
    EXPERIENCE_OUTLIER_CAP = 15 # Cap experience at 15 years for a clearer plot

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
    df_filtered = df[(df['RequiredExperienceYears'] > 0) & (df['RequiredExperienceYears'] <= EXPERIENCE_OUTLIER_CAP)].copy()
    
    df_filtered['SkillList'] = df_filtered['SoftwareSkills'].apply(parse_software_skills)
    df_skills = df_filtered.explode('SkillList').dropna(subset=['SkillList'])
    
    # Filter for only the key skills we want to analyze
    df_final = df_skills[df_skills['SkillList'].isin(KEY_IT_SKILLS)]

    print(f"Analyzing experience distribution for key skills.")

    # --- 3. 2D Visualization (Violin Plot) ---
    fig, ax = plt.subplots(figsize=(18, 10))
    
    sns.violinplot(
        x='RequiredExperienceYears',
        y='SkillList',
        data=df_final,
        order=KEY_IT_SKILLS,
        palette='Spectral',
        ax=ax,
        orient='h',
        inner='quartile' # Show quartiles inside the violins
    )

    # --- 4. Styling and Labeling ---
    config.set_title(ax, 'توزیع سابقه کار مورد نیاز برای مهارت‌های کلیدی')
    config.set_labels(ax, xlabel='سابقه کار مورد نیاز (سال)', ylabel='مهارت نرم‌افزاری')

    # Now that the labels are Persian, we need to apply RTL processing
    rtl_skill_labels = [config.rtl_text(label) for label in KEY_IT_SKILLS]
    ax.set_yticklabels(rtl_skill_labels, fontproperties=config.nazanin_font)

    formatter = FuncFormatter(lambda val, pos: config.to_persian_numerals(f'{int(val)}'))
    ax.xaxis.set_major_formatter(formatter)

    for label in ax.get_xticklabels():
        label.set_fontproperties(config.nazanin_font)

    # --- 5. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "35_experience_by_it_skill.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_experience_by_skill(CLEANED_DATASET_PATH)
