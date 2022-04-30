import subprocess

def get_device_uuid() -> str:
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()