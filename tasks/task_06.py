from collections import defaultdict, deque

def solve(objects: list, refs: list, variables: list, delete: list) -> tuple:
    obj_set = set(objects)
    
    for a, b in refs:
        if a not in obj_set:
            raise ValueError(f"Невідомий об'єкт: {a}")
        if b not in obj_set:
            raise ValueError(f"Невідомий об'єкт: {b}")
            
    for v in variables:
        if v not in obj_set:
            raise ValueError(f"Невідомий об'єкт: {v}")
            
    curr_vars = list(variables)
    for d in delete:
        if d in curr_vars:
            curr_vars.remove(d)
        else:
            raise ValueError(f"Немає змінної: {d}")
            
    # Вихідні ребра (граф залежностей)
    outgoing = defaultdict(list)
    incoming_count = {obj: 0 for obj in objects}
    for a, b in refs:
        outgoing[a].append(b)
        incoming_count[b] += 1
        
    var_counts = {obj: 0 for obj in objects}
    for v in curr_vars:
        var_counts[v] += 1
        
    ref_count = {obj: incoming_count[obj] + var_counts[obj] for obj in objects}
    
    # Каскадне звільнення для об'єктів з ref_count == 0
    freed_set = set()
    queue = deque([obj for obj in objects if ref_count[obj] == 0])
    
    while queue:
        u = queue.popleft()
        if u in freed_set:
            continue
        freed_set.add(u)
        for target in outgoing[u]:
            ref_count[target] -= 1
            if ref_count[target] == 0 and target not in freed_set:
                queue.append(target)
                
    # Обхід графа від збережених кореневих змінних для пошуку живих
    live_set = set()
    root_queue = deque([v for v in curr_vars if v not in freed_set])
    
    while root_queue:
        curr = root_queue.popleft()
        if curr in live_set:
            continue
        live_set.add(curr)
        for nxt in outgoing[curr]:
            if nxt not in freed_set and nxt not in live_set:
                root_queue.append(nxt)
                
    freed = [obj for obj in objects if obj in freed_set]
    live = [obj for obj in objects if obj in live_set]
    cycle_garbage = [obj for obj in objects if obj not in freed_set and obj not in live_set]
    
    return (freed, live, cycle_garbage)