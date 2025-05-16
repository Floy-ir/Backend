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
        'ي': 'ی'
    }
    
    # First normalize the characters
    normalized = multiple_replace(dic, airline_name)
    
    # Remove "ایر" and "ایرلاین" from beginning and end
    normalized = normalized.strip()
    prefixes_to_remove = ['ایر', 'ایرلاین']
    suffixes_to_remove = ['ایر', 'ایرلاین']
    
    # Remove from beginning
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    
    # Remove from end
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    return normalized
