import os
import json

def safe_string_to_int(s):
    try:
        return int(s)
    except ValueError:
        print(f"无法将 '{s}' 转换为整数")
        return None

def get_port_from_env(env_name, default_port):
    port = os.getenv(env_name)

    if port is not None:
        port = safe_string_to_int(port)

    if port is None:
        port = default_port

    return port

def save_to_json_file(result_data, datadir, filename):
    try:
        os.makedirs(datadir, exist_ok=True)
        file_path = os.path.join(datadir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        return file_path
    except Exception as e:
        return None