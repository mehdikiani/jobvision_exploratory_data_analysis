import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import seaborn as sns
from matplotlib import rcParams
import arabic_reshaper
from bidi.algorithm import get_display

import re
# === Load Persian Fonts ===

titr_path = os.path.join("fonts", 'BTitrBd.ttf')
nazanin_path = os.path.join("fonts", 'BNazanin.ttf')

# Set default sizes directly in FontProperties
titr_font = fm.FontProperties(fname=titr_path, size=24, weight='bold')
nazanin_font = fm.FontProperties(fname=nazanin_path, size=22)

# Only set font name string (not FontProperties object!) in rcParams
rcParams['font.family'] = nazanin_font.get_name()
rcParams['axes.titlesize'] = 24
rcParams['axes.titleweight'] = 'bold'
rcParams['axes.labelsize'] = 18
rcParams['xtick.labelsize'] = 16
rcParams['ytick.labelsize'] = 16
rcParams['axes.facecolor'] = 'white'
rcParams['axes.edgecolor'] = '#DFE8F6'
rcParams['axes.grid'] = True
rcParams['grid.color'] = '#DFE8F6'
rcParams['grid.linestyle'] = '--'
rcParams['legend.fontsize'] = 16
rcParams['figure.figsize'] = (20, 8)

# Consistent Seaborn Theme
sns.set_theme(style="whitegrid", palette=["#023E7D"])

# === Helper Functions ===

def rtl_text(text: str) -> str:
    """
    Reshapes and reverses Persian/Arabic text for correct RTL rendering.
    If the text is purely English, it returns it unchanged.
    """
    if not isinstance(text, str):
        text = str(text)

    # Check if the string contains any Arabic script characters
    if re.search('[\u0600-\u06FF]', text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped, base_dir='R')
    else:
        # If no Arabic characters are found, return the original string
        return text

def set_title(ax, text):
    ax.set_title(rtl_text(text), fontproperties=titr_font)

def set_labels(ax, xlabel, ylabel):
    ax.set_xlabel(rtl_text(xlabel), fontproperties=nazanin_font)
    ax.set_ylabel(rtl_text(ylabel), fontproperties=nazanin_font)

def set_xlabel(ax, xlabel):
    ax.set_xlabel(rtl_text(xlabel), fontproperties=nazanin_font)

def set_ylabel(ax, ylabel):
    ax.set_ylabel(rtl_text(ylabel), fontproperties=nazanin_font)
    
def to_persian_numerals(number_str: str) -> str:
    """Converts a string of English numerals to Persian numerals."""
    if not isinstance(number_str, str):
        number_str = str(number_str)
    persian_map = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return number_str.translate(persian_map)