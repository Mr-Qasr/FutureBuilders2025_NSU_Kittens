import psutil  # make sure it's in requirements.txt

def get_total_ram_gb() -> float:
    mem = psutil.virtual_memory()
    return mem.total / (1024**3)

def classify_machine() -> str:
    ram = get_total_ram_gb()

    if ram < 6:
        return "LOW"
    if ram < 12:
        return "MEDIUM"
    return "HIGH"
