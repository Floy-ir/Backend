import re


def multiple_replace(dic, text):
    pattern = "|".join(map(re.escape, dic.keys()))
    return re.sub(pattern, lambda m: dic[m.group()], str(text))

def normalize_airline(airline_name):
    # Character replacement dictionary
    dic = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی',
        'آ': 'ا',
        'ـ': '',  # Remove the Arabic tatweel character
        '\u200C': ' ',  # Convert half-space (zero-width non-joiner) to regular space
        '\u200D': ' ',  # Convert zero-width joiner to regular space
        '\u200E': ' ',  # Convert left-to-right mark to regular space
        '\u200F': ' ',  # Convert right-to-left mark to regular space
        '\u202A': ' ',  # Convert left-to-right embedding to regular space
        '\u202B': ' ',  # Convert right-to-left embedding to regular space
        '\u202C': ' ',  # Convert pop directional formatting to regular space
        '\u202D': ' ',  # Convert left-to-right override to regular space
        '\u202E': ' '   # Convert right-to-left override to regular space
    }
    
    # First normalize the characters
    normalized = multiple_replace(dic, airline_name)
    
    # Remove "ایر" and "ایرلاین" from beginning and end
    normalized = normalized.strip()
    prefixes_to_remove = ['ایرلاین']
    suffixes_to_remove = ['ایرلاین', 'ایرویز', 'ایر']
    
    # Remove from beginning
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    
    # Remove from end
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    # Normalize multiple spaces to single space
    normalized = ' '.join(normalized.split())
    
    return normalized
