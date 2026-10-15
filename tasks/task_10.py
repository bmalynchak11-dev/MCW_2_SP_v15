from collections import defaultdict

def _get_ancestors(path: str) -> list[str]:
    """Повертає список предків від найближчого до кореня '/' включно."""
    ancestors = []
    curr = path
    while True:
        ancestors.append(curr)
        if curr == "/":
            break
        idx = curr.rfind("/")
        curr = "/" if idx == 0 else curr[:idx]
    return ancestors

def solve(groups: dict, events: list) -> dict:
    # {pid: {'path': path, 'mem': int}}
    processes = {}
    
    killed = []
    rejected = []
    oom_kill = defaultdict(int)
    pids_max = defaultdict(int)
    
    for ev in events:
        ev_type = ev[0]
        
        if ev_type == "fork":
            _, pid, path = ev
            if pid in processes:
                raise ValueError(f"Процес {pid} уже існує")
            
            ancestors = _get_ancestors(path)
            fork_rejected = False
            
            for grp in ancestors:
                limit = groups.get(grp, {}).get("pids.max")
                if limit is not None:
                    # Кількість живих процесів у піддереві
                    count = sum(
                        1 for p in processes.values()
                        if p['path'] == grp or p['path'].startswith(grp.rstrip('/') + '/')
                    )
                    if count >= limit:
                        rejected.append(pid)
                        pids_max[grp] += 1
                        fork_rejected = True
                        break
                        
            if not fork_rejected:
                processes[pid] = {'path': path, 'mem': 0}
                
        elif ev_type == "alloc":
            _, pid, n = ev
            if pid not in processes:
                continue
            
            processes[pid]['mem'] += n
            ancestors = _get_ancestors(processes[pid]['path'])
            
            for grp in ancestors:
                limit = groups.get(grp, {}).get("memory.max")
                if limit is not None:
                    prefix = grp if grp == "/" else grp + "/"
                    subtree_pids = [
                        p_id for p_id, p_info in processes.items()
                        if p_info['path'] == grp or p_info['path'].startswith(prefix)
                    ]
                    total_mem = sum(processes[p_id]['mem'] for p_id in subtree_pids)
                    
                    if total_mem > limit:
                        # OOM-killer: найбільша пам'ять, за рівності — найменший pid
                        victim_pid = min(subtree_pids, key=lambda x: (-processes[x]['mem'], x))
                        killed.append(victim_pid)
                        del processes[victim_pid]
                        oom_kill[grp] += 1
                        break
                        
        elif ev_type == "free":
            _, pid, n = ev
            if pid in processes:
                processes[pid]['mem'] -= min(n, processes[pid]['mem'])
                
        elif ev_type == "exit":
            _, pid = ev
            if pid in processes:
                del processes[pid]
                
        else:
            raise ValueError(f"Невідома подія: {ev_type}")
            
    alive = [
        (pid, processes[pid]['path'], processes[pid]['mem'])
        for pid in sorted(processes.keys())
    ]
    
    oom_sorted = {k: oom_kill[k] for k in sorted(oom_kill.keys()) if oom_kill[k] > 0}
    pids_sorted = {k: pids_max[k] for k in sorted(pids_max.keys()) if pids_max[k] > 0}
    
    return {
        "alive": alive,
        "killed": killed,
        "rejected": rejected,
        "oom_kill": oom_sorted,
        "pids_max": pids_sorted
    }