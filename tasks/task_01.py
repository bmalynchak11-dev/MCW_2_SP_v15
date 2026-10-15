import struct

def solve(hex_text: str) -> str:
    cleaned = "".join(hex_text.split())
    
    if len(cleaned) % 2 != 0:
        return "Помилка: некоректний шістнадцятковий запис"
    
    try:
        raw_bytes = bytes.fromhex(cleaned)
    except ValueError:
        return "Помилка: некоректний шістнадцятковий запис"
    
    n_bytes = len(raw_bytes)
    fmt_map = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}
    
    if n_bytes not in fmt_map:
        return f"Помилка: довжина {n_bytes} байтів не підтримується"
    
    fmt_char = fmt_map[n_bytes]
    fmt_char_signed = fmt_char.lower()
    
    le_u = struct.unpack(f"<{fmt_char}", raw_bytes)[0]
    le_s = struct.unpack(f"<{fmt_char_signed}", raw_bytes)[0]
    be_u = struct.unpack(f">{fmt_char}", raw_bytes)[0]
    be_s = struct.unpack(f">{fmt_char_signed}", raw_bytes)[0]
    
    return f"LE: {le_u} / {le_s}; BE: {be_u} / {be_s}"