import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_MAP = {
    0: "відтінки сірого",
    2: "RGB",
    3: "палітра",
    4: "сірий з альфою",
    6: "RGBA"
}

def solve(data: bytes) -> str:
    if len(data) < 8 or data[:8] != PNG_SIGNATURE:
        return "Помилка: немає підпису PNG"
    
    offset = 8
    total_len = len(data)
    
    # Перевірка першого шматка на IHDR довжиною 13 байтів
    if total_len - offset < 12:
        return "Помилка: перший шматок не IHDR"
    first_len, first_type = struct.unpack_from(">I4s", data, offset)
    if first_type != b"IHDR" or first_len != 13:
        return "Помилка: перший шматок не IHDR"
    
    lines = []
    ihdr_parsed = False
    
    while offset < total_len:
        if total_len - offset < 12:
            lines.append(f"Обірваний шматок на зсуві {offset}")
            return "\n".join(lines)
        
        length, chunk_type_raw = struct.unpack_from(">I4s", data, offset)
        required_len = 12 + length
        
        if total_len - offset < required_len:
            lines.append(f"Обірваний шматок на зсуві {offset}")
            return "\n".join(lines)
        
        chunk_data = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        actual_crc = zlib.crc32(chunk_type_raw + chunk_data) & 0xffffffff
        
        crc_status = "CRC збігається" if actual_crc == expected_crc else "CRC не збігається"
        chunk_name = chunk_type_raw.decode("ascii", errors="replace")
        
        if not ihdr_parsed and chunk_name == "IHDR":
            width, height, bit_depth, color_type = struct.unpack_from(">IIBB", chunk_data, 0)
            color_str = COLOR_MAP.get(color_type, f"невідомий ({color_type})")
            # Використовуємо латинську 'x' (width)x(height)
            lines.append(f"Зображення: {width}x{height}, {bit_depth} біт, {color_str}")
            ihdr_parsed = True
        
        lines.append(f"{chunk_name}: {length} байтів, {crc_status}")
        offset += required_len
        
        if chunk_name == "IEND":
            trailing_bytes = total_len - offset
            if trailing_bytes > 0:
                lines.append(f"Зайвих байтів після IEND: {trailing_bytes}")
            return "\n".join(lines)
            
    lines.append("Немає IEND.")
    return "\n".join(lines)