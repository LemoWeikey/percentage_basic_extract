import pandas as pd
import numpy as np
import re
from collections import Counter

# --- Constants & Patterns ---
CHOOSE_LIST = [
    'xơ nhân tạo', 'polyester', 'cotton', 'recycle', 'organic', 'nylon', 'nylon6', 'rayon', 'modal', 'poly',
    'polyamide', 'elastane', 'chemically', 'mechanically', 'viscose', 'acrylic', 'generic', 'thermoplastic',
    'cationic', 'polyethylene', 'cashmere', 'recycled', 'lyra', 'eco', 'matta', 'tencel', 't400', 'pp',
    'polypropylen', 'polyurethane', 'dye', 'core spun yarrn', 'rec', 'regenerative', 'post consumer', 'merino',
    'elastic', 'spandex', 'triacetate', 'span', 'metallic', 'elastomultiester', 'lyocell', 'ecovero',
    'post-consumer', 'taffeta', 'lycra', 'bci', 'linen', 'brood', 'protein', 'pa6', 'wool', 'polyethyene',
    'acetate', 'spdx', 'other', 'elastan', 'lurex', 'epe', 'hemp', 'pes', 'silk', 'birla', 'livaeco',
    'elasthan', 'spandexdún', 'elasterell', 'rumble', 'recyclepolyester', 'elastaned', 'elasta', 'elast',
    'elastance', 'spanex', 'elasthanne', 'vi', 'ea', 'static', 'biconstituent', 'grey', 'pu', 'spx',
    'polyeser', 'vicose', 'ployeser', 'cly', 'polyurethan', 'tpu', 'spande', 'elastimultiester',
    'elanstane', 'fiber', 'fibers', 'metallised', 'elstance', 'elastanedcdp', 'elastanes', 'el', 'elstane',
    'organiccotton', 'polye', 'lyocel', 'polyeste', 'sapndex', 'viscosed', 'bemberg', 'visecose',
    'vicoseb', 'cupro', 'vie', 'coton', 'truehemp', 'loycell', 'ployester', 'pa', 'gec', 're', 'ly',
    'coolmax', 'co', 'acr', 'vis', 'mono', 'bamboo', 'long', 'staple', 'model', 'pol', 'polyvinyl', 'pva',
    'polyamid', 'line', 'thermo', 'bông', 'r', 'oc', 'rpes', 'ctn', 'poliester', 'poliammide', 'metallized',
    'spandec', 'po', 'freefit', 'xơ', 'stape', 'repreve', 'filamment', 'li', 'ten', 'cotto', 'pe', 'xla',
    'cellulose', 'lino', 'ester', 'cttn', 'lycell', 'piw', 'ecolycra', 'plyester', 'elaspan',
    'blackrecyclepolyeste', 'strech', 'polyuretane', 'n', 'freffit', 'polyeter', 'ep', 'elastolefine',
    'elas', 'rr', 'polyamise', 'elanstic', 'soandex', 'cd', 'tel', 'polysester', 'cottotn', 'spadnex',
    'rp', 'paper', 'viscorayon', 'polyestere', 'kevlar', 'noex', 'antistatic', 'sandex', 'elasstanem',
    'recycled polyester', 'ploy ciclo', 'ny', 'sp'
]
CHOOSE_SET = set(word.lower() for word in CHOOSE_LIST)

def extract_percent_values(text):
    """Recursively extracts percentage values."""
    if pd.isna(text):
        return []
    text = text.lower()
    all_percentages = re.findall(r'\d+\.?\d*%|\d+\.?\d*\s*(?:pct|percent)', text, re.IGNORECASE)
    return all_percentages

def clean_text(text):
    """Cleans unwanted patterns from text."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    exclude_patterns = [
        r'\bmới\s*\d+%?\b', r'\b\d+%\s*mới\b', 
        r'\bnew\s*\d+%?\b', r'\b\d+%\s*new\b', 
        r'\bbrand\s*\d+%?\b', r'\b\d+%\s*brand\b', 
        r'\bitem\s*\d+%?\b', r'\b\d+%\s*item\b', 
        r'\bhàng\s*mới\s*\d+%?\b', r'\b\d+%\s*hàng\s*mới\b', 
        r'\b\d+%\s*[\#&><?@!*]', 
        r'\(\s*\+\-\s*\d+%\)', r'\+\-\s*\d+%', 
        r'\(\s*\+/\-\s*\d+%\)', r'\+/\-\s*\d+%', 
        r'(?<!\d)\.\s*\d+%\s*[#><?@&.*]'
    ]
    for pattern in exclude_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_position_matching(row):
    """Finds positions of extracted percentages."""
    extracted_percentages = row['Extracted_Percentages']
    if not extracted_percentages:
        return []
    text = str(row['ProductList']).lower()
    matches = []
    used_positions = set()
    for percent in extracted_percentages:
        pattern = rf'(?<!\d){re.escape(percent)}(?!\d)'
        match_positions = [m.start() for m in re.finditer(pattern, text)]
        for pos in match_positions:
            if pos not in used_positions:
                matches.append(pos)
                used_positions.add(pos)
                break
    return sorted(matches)

def extract_text_from_row_v1(row):
    """Extracts text based on positions (Logic 1)."""
    text = row["ProductList"]
    positions = row["position_matching"]
    if not positions:
        return ""
    words = re.findall(r'\S+', text)
    if not words: return ""
    word_positions = [text.index(word) for word in words]
    min_pos = min(positions)
    max_pos = max(positions)
    
    # helper to find index safely
    def find_idx(condition, default):
        return next((i for i, pos in enumerate(word_positions) if condition(pos)), default)

    min_word_idx = find_idx(lambda p: p >= min_pos, 0)
    max_word_idx = find_idx(lambda p: p >= max_pos, len(words) - 1)

    left_window_idx = max(0, min_word_idx - 3)
    right_window_idx = min(len(words), max_word_idx + 4)
    return " ".join(words[left_window_idx:right_window_idx])

def filter_text_preserve_order(text, choose_set):
    """Filters text and preserves order of keywords and percentages."""
    if not isinstance(text, str): return ""
    text = re.sub(r'(\d),(\d+)%', lambda m: f"{m.group(1)}.{m.group(2)}%", text)
    text = re.sub(r'(\d),(\d+)', lambda m: f"{m.group(1)}.{m.group(2)}", text)
    text = re.sub(r'([a-zA-Z])(\d+[.,]?\d*%)', r'\1 \2', text)
    text = re.sub(r'(\d+[.,]?\d*%)([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'(?<=[a-zA-Z])(?=\d)', ' ', text)
    
    tokens = re.findall(
        r'\d+\.\d+%|\d+%|\d+\.\d*\s*(?:pct|percent)|\d+\s*(?:pct|percent)|\b\w+\b|\(|\)',
        text, re.IGNORECASE
    )
    filtered_tokens = [
        token for token in tokens
        if token.lower() in choose_set
        or re.match(r'\d+\.\d+%|\d+%|\d+\.\d*\s*(?:pct|percent)|\d+\s*(?:pct|percent)', token, re.IGNORECASE)
        or token in "()"
    ]
    return " ".join(filtered_tokens)

def balance_parentheses(text):
    """Balances parentheses."""
    if not isinstance(text, str): return ""
    open_count = text.count('(')
    close_count = text.count(')')
    while open_count > close_count:
        text = text[::-1].replace('(', '', 1)[::-1]
        open_count -= 1
    while close_count > open_count:
        text = text.replace(')', '', 1)
        close_count -= 1
    text = re.sub(r'\(\s*([\w\d%]+.*?)\s*\)', r'(\1)', text)
    text = re.sub(r'(\S)\s+\(', r'\1 (', text)
    text = re.sub(r'\)\s+(\S)', r') \1', text)
    text = re.sub(r'\(\s*\)$', '', text)
    return text.strip()

def remove_empty_parentheses(text):
    if not isinstance(text, str): return ""
    return re.sub(r'\(\s*\)', '', text).strip()

# --- Logic 2 Helpers (from Cell 2) ---

def extract_percentages_v2(text):
    matches = []
    text = re.sub(r'(\d+(?:\.\d+)?)\s+%', r'\1%', text)
    direct_matches = re.findall(r'\d+\.?\d*\s?%', text)
    matches.extend(direct_matches)
    
    split_percentages = re.findall(r'([\d/+]+)(?:%|)', text)
    for group in split_percentages:
        if "/" in group or "+" in group:
            try:
                numbers = [int(num) for num in re.split(r'[/+]', group) if num.isdigit()]
                if sum(numbers) == 100:
                    for num in numbers:
                        matches.append(f"{num}%")
            except: pass
    return matches

def find_percent_positions_v2(text):
    positions = []
    for match in re.finditer(r'\d+\.\d+\s?%|\d+\s?%', text):
        positions.append(match.start())
        
    for match in re.finditer(r'([\d/]+)(?:%|)', text):
        if "/" in match.group(1):
            try:
                numbers = [int(num) for num in match.group(1).split('/') if num.isdigit()]
                if sum(numbers) == 100:
                    start_index = match.start(1)
                    current_pos = start_index
                    for num in numbers:
                        if current_pos not in positions:
                            positions.append(current_pos)
                        current_pos += len(str(num)) + 1
            except: pass
    return sorted(positions)

def extract_text_from_row_v2(row):
    text = row.get("ProductList", "")
    positions = row.get("percent_positions", [])
    if not isinstance(text, str) or not text.strip() or not positions:
        return ""
    words = re.findall(r'\S+', text)
    if not words: return ""
    word_positions = [text.index(word) for word in words]
    min_pos = min(positions)
    max_pos = max(positions)
    
    def find_idx(condition, default):
        return next((i for i, pos in enumerate(word_positions) if condition(pos)), default)

    min_word_idx = find_idx(lambda p: p >= min_pos, 0)
    max_word_idx = find_idx(lambda p: p >= max_pos, len(words) - 1)
    
    left_window_idx = max(0, min_word_idx - 4)
    right_window_idx = min(len(words), max_word_idx + 4)
    return " ".join(words[left_window_idx:right_window_idx])

def filter_text_preserve_order_v2(text, choose_set):
    text = text.replace('_', ' ')
    text = re.sub(r'(\d+)\s*%', r'\1%', text)
    text = re.sub(r'(\d+(?:/\d+)?(?:\.\d+)?)\s+%', r'\1%', text)
    text = text.replace('&', '%')
    text = re.sub(r'(\d+)\s*%', r'\1%', text)
    text = re.sub(r'([a-zA-Z])(\d+\.\d+%)', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z])(\d+)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z]+)(\d+)\s*pct', r'\1 \2pct', text)
    text = re.sub(r'([a-zA-Z])(\d+%)', r'\1 \2', text)
    text = re.sub(r'(\d+%)([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Zàáảãạâầấậẫăằắặẵèéẻẽẹêềếệễìíỉĩịòóỏõọôồốộỗơờớợỡùúủũụưừứựữỳýỷỹỵđ])(\d+%)', r'\1 \2', text)
    
    match = re.search(r'(\d+(?:/\d+)+)\s*([a-zA-Z/\- ]*)', text)
    if match:
        numbers = match.group(1)
        materials = match.group(2).replace('/', ' ')
        try:
            percent_list = [int(num) for num in numbers.split('/')]
            if sum(percent_list) == 100:
                percent_str = " ".join(f"{num}%" for num in percent_list)
                text = text.replace(match.group(0), f"{percent_str} {materials}".strip())
        except: pass

    text = re.sub(r'(\d+(?:/\d+)+)%',
                lambda m: " ".join(f"{num}%" for num in m.group(1).split('/')),
                text)
    text = re.sub(r'(\w)(\d+/\d+)', r'\1 \2', text)
    
    tokens = re.findall(r'\d+\.\d+%|\d+%|\d+\.\d*\s*(?:pct|percent)|\d+\s*(?:pct|percent)|\b[\w/-]+\b|\(|\)', text, re.IGNORECASE)
    filtered_tokens = [
        token for token in tokens
        if token.lower() in choose_set
        or re.match(r'\d+\.\d*%|\d+%|\d+\.\d*\s*(?:pct|percent)|\d+\s*(?:pct|percent)', token, re.IGNORECASE)
        or token in "()"
    ]
    return " ".join(filtered_tokens)

def match_percent_material(text):
    percentages = re.findall(r'\d+%', text)
    material_text = re.sub(r'\d+%', '', text)
    materials = material_text.split('/')
    materials = [m.strip() for m in materials]
    result = []
    for i, material in enumerate(materials):
        if i < len(percentages):
            result.append(f"{percentages[i]} {material}")
    
    # If standard matching resulted empty or weird, fallback/original check might be needed
    # But as per notebook logic we return this join
    if not result and not percentages: return text # Fallback if no percents met logic
    if not result: return " ".join(percentages) + " " + " ".join(materials) # Rough fallback
    
    return " ".join(result)

def analyze_case_percent(text):
    if not isinstance(text, str): return 0
    text = re.sub(r'(\d+)\s*pct', r'\1%', text)
    percentages = re.findall(r'\d+%', text)
    parts = re.split(r'\d+%', text)
    word_group_count = 0
    for part in parts:
        words = re.findall(r'\b\w+\b', part.strip())
        if words: word_group_count += 1
    percentage_count = len(percentages)
    if word_group_count == percentage_count: return 0
    elif percentage_count > word_group_count: return 1
    else: return 2

def filter_text_preserve_order_100(text, choose_set):
    if not isinstance(text, str): return ""
    text = text.replace('_', ' ')
    text = text.replace('&', '%')
    text = re.sub(r'([a-zA-Z])(\d+\.\d+%)', r'\1 \2', text)
    text = re.sub(r'(\d+)\s*%', r'\1%', text)
    text = re.sub(r'([a-zA-Z]+)(\d+)\s*pct', r'\1 \2pct', text)
    text = re.sub(r'(\d+)(%)([a-zA-Z])', r'\1\2 \3', text)
    text = re.sub(r'([a-zA-Z]+)(\d+)([a-zA-Z]*)', r'\1 \2\3', text)
    text = re.sub(r'(\S)(elastane|cotton|spandex|recycled)', r'\1 \2', text, flags=re.IGNORECASE)
    text = re.sub(r'(elastane|cotton|spandex|recycled)(\S)', r'\1 \2', text, flags=re.IGNORECASE)
    
    tokens = re.findall(r'\d+\.\d+%|\d+%|\d+\.\d*\s*(?:pct|percent)|\d+\s*(?:pct|percent)|\b\w+\b|\(|\)', text, re.IGNORECASE)
    filtered_tokens = [
        token for token in tokens
        if token.lower() in choose_set
        or re.match(r'\d+\.\d*%|\d+%|\d+\.\d*\s*(?:pct|percent)|\d+\s*(?:pct|percent)', token, re.IGNORECASE)
        or token in "()"
    ]
    return " ".join(filtered_tokens)

def clean_percentages_final(text):
    if not isinstance(text, str): return text
    while re.match(r'^(\d+%)\s+(\d+%)', text):
        text = re.sub(r'^(\d+%)\s+(\d+%)', r'\2', text)
    while re.search(r'(\d+%)\s+(\d+%)$', text):
        text = re.sub(r'(\d+%)\s+(\d+%)$', r'\1', text)
    text = re.sub(r'^\d+%\s*\((.*)\)', r'(\1)', text)
    text = re.sub(r'\((.*)\)\s*\d+%$', r'(\1)', text)
    text = re.sub(r'(\d{4,})%', '', text)
    return text.strip()

# --- MAIN PROCESSING FUNCTION ---

def process_dataframe(df, col_name):
    # --- PHASE 1: Initial Processing (Cell 1 Logic) ---
    df_dl = df[[col_name]].copy()
    df_dl.columns = ["Products"]
    
    df_dl["ProductList"] = df_dl["Products"].apply(clean_text)
    df_dl["Extracted_Percentages"] = df_dl["ProductList"].apply(extract_percent_values)
    df_dl['position_matching'] = df_dl.apply(get_position_matching, axis=1)
    df_dl["extracted_text"] = df_dl.apply(extract_text_from_row_v1, axis=1)
    df_dl["filtered_text"] = df_dl["extracted_text"].apply(lambda x: filter_text_preserve_order(x, CHOOSE_SET))
    df_dl["balanced_text"] = df_dl["filtered_text"].apply(balance_parentheses)
    df_dl["cleaned_text"] = df_dl["balanced_text"].apply(remove_empty_parentheses)
    
    # Calculate sum to check for < 100 cases
    def calculate_sum(text):
        if not isinstance(text, str): return 0
        nums = [float(num) for num in re.findall(r'\d+\.?\d*', text)]
        return int(np.sum(nums))
        
    df_dl['total_sum'] = df_dl['cleaned_text'].apply(calculate_sum)
    
    # Identify rows with < 100% sum
    df_filtered = df_dl[df_dl['total_sum'] < 100].copy()
    
    # If no problematic rows, return result of Phase 1
    if df_filtered.empty:
        # User request: "if the data df_filtererd begining of cell 2 is empty ... give me the excel file result of cell 1"
        return df_dl[['Products', 'ProductList', 'cleaned_text']]
        
    # --- PHASE 2: Advanced Processing for < 100% (Cell 2 Logic) ---
    # Logic: df_filtered is processed with extract_percentages, find_percent_positions, etc. (v2 helpers)
    
    df_filtered['percent_values'] = df_filtered['ProductList'].apply(extract_percentages_v2)
    df_filtered['percent_positions'] = df_filtered['ProductList'].apply(find_percent_positions_v2)
    
    # Filter valid rows for processing
    df_filtered_two = df_filtered[
        df_filtered['ProductList'].notna() & (df_filtered['ProductList'].str.strip() != "")
    ].copy()
    
    if not df_filtered_two.empty:
        df_filtered_two["cleaned_text"] = df_filtered_two.apply(extract_text_from_row_v2, axis=1)
        
        # Second pass filtering
        df_filtered_two["filtered_text"] = df_filtered_two["cleaned_text"].apply(
            lambda x: filter_text_preserve_order_v2(x, CHOOSE_SET)
        )
        
        # Match percent material
        df_filtered_two["filtered_text"] = df_filtered_two["filtered_text"].apply(match_percent_material)
        
        # We need to map this back to df_filtered
        df_filtered.loc[df_filtered_two.index, 'cleaned_text'] = df_filtered_two['filtered_text']
    
    # Update main df with better results from df_filtered
    df_dl.loc[df_filtered.index, 'cleaned_text'] = df_filtered['cleaned_text']
    
    # Ensure total_sum is updated for the main df after Phase 2 updates
    df_dl.loc[df_filtered.index, 'total_sum'] = df_filtered['cleaned_text'].apply(calculate_sum)
    
    # --- PHASE 3: Even more logic (Case analysis & 100% check from Cell 2 end) ---
    # The notebook continues... "Case analysis" for cases == 1
    df_dl['Cases'] = df_dl['cleaned_text'].apply(lambda x: analyze_case_percent(str(x) if isinstance(x, (float, int)) else x))
    
    df_case_1 = df_dl[df_dl['Cases'] == 1].copy()
    
    if not df_case_1.empty:
        df_case_1['percent_values'] = df_case_1['ProductList'].apply(extract_percentages_v2)
        df_case_1['percent_positions'] = df_case_1['ProductList'].apply(find_percent_positions_v2)
        
        # Re-extract text with wider window (5 words)
        def extract_text_case_1(row):
            text = row["ProductList"]
            positions = row["percent_positions"]
            if not positions: return ""
            words = re.findall(r'\S+', text)
            if not words: return ""
            word_positions = [text.index(word) for word in words]
            min_pos = min(positions)
            max_pos = max(positions)
            def find_idx(c, d): return next((i for i, p in enumerate(word_positions) if c(p)), d)
            min_word_idx = find_idx(lambda p: p >= min_pos, 0)
            max_word_idx = find_idx(lambda p: p >= max_pos, len(words) - 1)
            left = max(0, min_word_idx - 5)
            right = min(len(words), max_word_idx + 5)
            return " ".join(words[left:right])

        df_case_1["cleaned_text"] = df_case_1.apply(extract_text_case_1, axis=1)
        
        # Filter with filter_text_preserve_order_100
        # sort choose_set by length for this specific function as in notebook
        sorted_choose_set = sorted(CHOOSE_SET, key=len, reverse=True)
        # Convert set back to list for order? unique items? Actually the function takes a set but logic implies checks
        # The notebook passed a SET to the function but defined sorted choose_set before??
        # Ah wait, "choose_set = sorted(..., reverse=True)" makes it a LIST.
        # So we should pass a LIST to the function if it iterates order?
        # The function `filter_text_preserve_order_100` uses `token.lower() in choose_set`. 
        # If choose_set is a list, `in` is O(N). If set, O(1).
        # The regex construction uses `sorted(...)`.
        # Let's just pass the set for the `in` check, it's safer.
        
        df_case_1["cleaned_text"] = df_case_1["cleaned_text"].apply(
            lambda x: filter_text_preserve_order_100(x, CHOOSE_SET)
        )
        
        df_case_1["balanced_text"] = df_case_1["cleaned_text"].apply(balance_parentheses)
        df_case_1["cleaned_text"] = df_case_1["balanced_text"].apply(remove_empty_parentheses)
        df_case_1["cleaned_text"] = df_case_1["cleaned_text"].apply(clean_percentages_final)
        
        df_dl.loc[df_case_1.index, 'cleaned_text'] = df_case_1['cleaned_text']
        
    # Final cleanup
    result_df = df_dl[['Products', 'ProductList', 'cleaned_text']].copy()
    result_df['ProductList'] = result_df['Products'].astype(str).str.lower()
    
    return result_df
