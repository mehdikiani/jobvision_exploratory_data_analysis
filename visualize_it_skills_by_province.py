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


def visualize_it_skills_by_province(cleaned_file_path: str, output_dir: str = 'eda'):
    """
    Analyzes and compares the top IT skills across the main tech-hub provinces.

    Args:
        cleaned_file_path (str): The path to the cleaned CSV dataset.
        output_dir (str): The directory to save the output figures.
    """
    # --- Analysis Configuration ---
    TOP_N_SKILLS = 10
    TOP_N_PROVINCES = 5 # <-- CLEAN CODE: You can now easily change this value.
    IT_JOB_CATEGORIES = [
        'توسعه نرم افزار و برنامه نویسی',
        'فناوری اطلاعات / نرم افزار و سخت افزار',
        'شبکه / امنیت / زیرساخت',
        'DevOps ، Sys-Admin'
    ]

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

    # --- 2. Filter for IT Jobs ---
    df_it = df[df['MainJobCategory'].isin(IT_JOB_CATEGORIES)].copy()
    print(f"Filtered for 'فناوری اطلاعات' jobs. Found {len(df_it)} relevant postings.")

    # --- 3. Identify Top IT Provinces Dynamically ---
    top_provinces = df_it['ProvinceFa'].value_counts().head(TOP_N_PROVINCES).index
    print(f"Dynamically identified top {TOP_N_PROVINCES} IT provinces: {top_provinces.tolist()}")

    # --- 4. Loop and Analyze Each Province ---
    for i, province in enumerate(top_provinces):
        print("-" * 50)
        print(f"Analyzing 'فناوری اطلاعات' skills for province: {province}")

        df_province_it = df_it[df_it['ProvinceFa'] == province]
        
        df_province_it['SkillList'] = df_province_it['SoftwareSkills'].apply(parse_software_skills)
        df_skills = df_province_it.explode('SkillList').dropna(subset=['SkillList'])
        
        skill_counts = df_skills['SkillList'].value_counts().head(TOP_N_SKILLS)

        print(f"Top {TOP_N_SKILLS} skills in {province}:\n", skill_counts)

        # --- Visualization ---
        fig, ax = plt.subplots(figsize=(16, 10))
        colors = sns.color_palette("rocket", len(skill_counts))
        sns.barplot(x=skill_counts.values, y=skill_counts.index, palette=colors, ax=ax, orient='h')

        # --- Styling and Labeling ---
        title_text = f'مهارت‌های برتر فناوری اطلاعات در استان {province}'
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

        # --- Save Figure to File ---
        os.makedirs(output_dir, exist_ok=True)
        safe_province_name = province.replace(" ", "_")
        file_name = f"33_{i+1}_it_skills_{safe_province_name}.png"
        output_path = os.path.join(output_dir, file_name)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Figure for {province} saved successfully to: {output_path}")

    print("-" * 50)
    print("All IT skill analyses by province are complete.")


if __name__ == '__main__':
    CLEANED_DATASET_PATH = 'JobVision_Cleaned.csv'
    visualize_it_skills_by_province(CLEANED_DATASET_PATH)
