def solve(address: int, length: int, page_size: int) -> str:
    if page_size <= 0 or (page_size & (page_size - 1)) != 0:
        return "Помилка: розмір сторінки має бути степенем двійки"
    if address < 0:
        return "Помилка: адреса не може бути від'ємною"
    if length < 1:
        return "Помилка: довжина має бути додатною"
    
    first_page = address // page_size
    last_page = (address + length - 1) // page_size
    total_pages = last_page - first_page + 1
    
    offset_in_first = address % page_size
    first_page_start_addr = first_page * page_size
    hex_start = hex(first_page_start_addr).lower()
    
    covered_bytes = total_pages * page_size
    unused_bytes = covered_bytes - length
    
    return (
        f"сторінок: {total_pages} (від {first_page} до {last_page}); "
        f"зсув у першій: {offset_in_first}; "
        f"початок першої: {hex_start}; "
        f"покрито: {covered_bytes} Б, не використано: {unused_bytes} Б"
    )