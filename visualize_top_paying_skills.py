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


def visualize_top_paying_skills(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Identifies the most in-demand skills within the highest-paying jobs.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_SKILLS = 15
    SALARY_PERCENTILE_THRESHOLD = 0.90 # Focus on the top 10% of salaries

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
    df['AvgSalary'] = df[['MinSalary', 'MaxSalary']].mean(axis=1)
    df.dropna(subset=['AvgSalary', 'SoftwareSkills'], inplace=True)

    # Determine the salary threshold for top-paying jobs
    high_salary_threshold = df['AvgSalary'].quantile(SALARY_PERCENTILE_THRESHOLD)
    print(f"Identifying skills for jobs paying above the {int(SALARY_PERCENTILE_THRESHOLD*100)}th percentile.")
    print(f"High salary threshold: {high_salary_threshold:,.0f} Million Toman")

    # Filter for only the top-paying jobs
    df_high_salary = df[df['AvgSalary'] >= high_salary_threshold].copy()

    # --- 3. Skill Aggregation ---
    df_high_salary['SkillList'] = df_high_salary['SoftwareSkills'].apply(parse_software_skills)
    df_skills = df_high_salary.explode('SkillList')
    df_skills.dropna(subset=['SkillList'], inplace=True)
    
    skill_counts = df_skills['SkillList'].value_counts().head(TOP_N_SKILLS)

    print(f"Top {TOP_N_SKILLS} skills in high-paying jobs:\n", skill_counts)

    # --- 4. 2D Visualization ---
    fig, ax = plt.subplots(figsize=(16, 12))
    colors = sns.color_palette("magma", len(skill_counts))
    sns.barplot(x=skill_counts.values, y=skill_counts.index, palette=colors, ax=ax, orient='h')

    # --- 5. Styling and Labeling ---
    title_text = f'مهارت‌های کلیدی در مشاغل پردرآمد (دهک بالای حقوق)'
    config.set_title(ax, title_text)
    config.set_labels(ax, xlabel='تعداد تکرار در آگهی‌ها', ylabel='مهارت نرم‌افزاری')

    rtl_skill_labels = [config.rtl_text(label) for label in skill_counts.index]
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

    # --- 6. Save Figure to File ---
    os.makedirs(output_dir, exist_ok=True)
    file_name = "30_top_paying_skills.png"
    output_path = os.path.join(output_dir, file_name)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("-" * 50)
    print(f"Figure saved successfully to: {output_path}")
    print("-" * 50)


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_top_paying_skills(CLEANED_DATASET_PATH)
