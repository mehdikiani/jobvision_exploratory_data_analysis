import pandas as pd
import json
import os

def preprocess_job_data(raw_file_path: str, cleaned_file_path: str):
    """
    Loads the raw JobVision dataset, performs comprehensive cleaning by replacing
    all known English words with Persian equivalents, and saves the result.
    """
    print(f"Starting preprocessing of '{raw_file_path}'...")

    # --- 1. Central Translation Dictionary ---
    # This map will be used to replace all English words with Persian.
    english_to_persian_map = {
        '.net':'دات نت',
        'net.':'دات نت',
        'net core':'دات نت کر',
        'HSE': 'بهداشت، ایمنی و محیط زیست',
        'UI/UX': 'رابط و تجربه کاربری',
        'DevOps': 'دواپس',
        'Sys-Admin': 'ادمین سیستم',
        'MDF': 'ام‌دی‌اف',
        # Add other common standalone words if needed
        'Back-End': 'بک-اند',
        'Front-End': 'فرانت-اند',
        'Full-Stack': 'فول-استک',
        'IT': 'فناوری اطلاعات',
        '/': '،',
        '/': '-',
        'and': 'و',
        'with': 'با',
        'for': 'برای',  
         'coremvc': 'دات‌نت کر ام‌وی‌سی'
    }

    try:
        # --- 2. Data Loading ---
        df = pd.read_csv(raw_file_path)
        print("Raw dataset loaded successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{raw_file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return

    # --- 3. Column Standardization ---
    rename_map = {}
    for col in df.columns:
        if col.startswith('Jobpost_'):
            rename_map[col] = col[len('Jobpost_'):]
        elif col.startswith('Comany_'):
            rename_map[col] = col.replace('Comany_', 'Company_')
    df.rename(columns=rename_map, inplace=True)
    
    cols_to_drop = [
        'RowNumber', 'ProvinceEn', 'WorkTypeEn', 'IndustryEn', 'BenefitEn',
        'CityEn', 'CompanyOwnershipTypesEn', 'SizeEn', 'ActivityTypeEn',
        'Company_ProvinceEn'
    ]
    existing_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    df.drop(columns=existing_cols_to_drop, inplace=True)

    # --- 4. Text & Categorical Data Cleaning ---
    columns_to_clean = [
        'MainJobCategory', 'IndustryFa', 'Company_IndustryFa', 'RawTitle'
    ]

    print("Starting word-by-word translation...")
    for col in columns_to_clean:
        if col in df.columns:
            # First, ensure the column is of string type
            df[col] = df[col].astype(str)
            # Replace the slash character first
            df[col] = df[col].str.replace(' / ', '، ', regex=False)
            # Loop through the dictionary and replace each English word
            for eng, per in english_to_persian_map.items():
                # Use regex=False for literal string replacement, case=False for case-insensitivity
                df[col] = df[col].str.replace(eng, per, regex=False, case=False)
    print("Word replacement complete.")

    # --- 5. Handling Missing Values ---
    categorical_fills = {
        'ProvinceFa': 'نامشخص', 'WorkTypeFa': 'نامشخص',
        'MainJobCategory': 'نامشخص', 'RequiredExperienceYears': 0
    }
    for col, fill_value in categorical_fills.items():
        if col in df.columns:
            df[col].fillna(fill_value, inplace=True)

    # --- 6. Data Type Conversion ---
    bool_cols = [
        'SalaryCanBeShown', 'RequiredRelatedExperienceInThisIndustry',
        'HasDisabilitySupport', 'IsRemote', 'IsInternship',
        'PriorityWithLocalCandidate', 'RequiredMilitaryServiceCard'
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    numeric_cols = ['MinSalary', 'MaxSalary', 'RequiredMinAge', 'RequiredMaxAge']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 7. Saving the Cleaned Data ---
    try:
        df.to_csv(cleaned_file_path, index=False, encoding='utf-8-sig')
        print("-" * 50)
        print(f"Preprocessing complete! Final cleaned data saved to '{cleaned_file_path}'.")
        print("-" * 50)
    except Exception as e:
        print(f"An error occurred while saving the cleaned file: {e}")


if __name__ == '__main__':
    RAW_DATA_PATH = 'JobVision_Jobposts_Dataset.csv'
    CLEANED_DATA_PATH = 'JobVision_Cleaned.csv'
    preprocess_job_data(RAW_DATA_PATH, CLEANED_DATA_PATH)
