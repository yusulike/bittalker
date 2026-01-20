"""
Korean Number Converter
Converts numbers to Korean text for TTS pronunciation.
"""

# 기본 숫자
DIGITS = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']
# 자릿수 단위 (10, 100, 1000)
SMALL_UNITS = ['', '십', '백', '천']
# 큰 단위 (만, 억, 조)
BIG_UNITS = ['', '만', '억', '조', '경']

def number_to_korean(num: int) -> str:
    """
    Convert an integer to Korean text.
    
    Examples:
        95500 → "구만 오천오백"
        1234 → "천이백삼십사"
        100000 → "십만"
    """
    if num == 0:
        return "영"
    
    if num < 0:
        return "마이너스 " + number_to_korean(-num)
    
    result = []
    
    # Split into groups of 4 digits (만, 억, 조...)
    groups = []
    while num > 0:
        groups.append(num % 10000)
        num //= 10000
    
    for i, group in enumerate(reversed(groups)):
        if group == 0:
            continue
            
        group_text = _four_digits_to_korean(group)
        big_unit_idx = len(groups) - 1 - i
        
        if big_unit_idx < len(BIG_UNITS):
            group_text += BIG_UNITS[big_unit_idx]
        
        result.append(group_text)
    
    return ' '.join(result).strip()


def _four_digits_to_korean(num: int) -> str:
    """Convert a number 0-9999 to Korean."""
    if num == 0:
        return ""
    
    result = []
    
    for i in range(4):
        digit = num % 10
        num //= 10
        
        if digit == 0:
            continue
        
        unit = SMALL_UNITS[i]
        
        # "일"은 생략하는 경우가 있음 (십, 백, 천 앞에서)
        if digit == 1 and i > 0:
            result.append(unit)
        else:
            result.append(DIGITS[digit] + unit)
    
    return ''.join(reversed(result))


def format_price_korean(price: int) -> str:
    """
    Format a price for Korean TTS.
    
    Example:
        95500 → "구만 오천오백"
    """
    return number_to_korean(price)


if __name__ == "__main__":
    # Test
    tests = [0, 1, 10, 15, 100, 123, 1000, 1234, 10000, 95500, 95450, 100000, 123456]
    for n in tests:
        print(f"{n:>10} → {number_to_korean(n)}")
