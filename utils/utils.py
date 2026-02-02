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

def save_to_json_file(result_data, output_filepath):
    datadir, filename = os.path.split(output_filepath)
    os.makedirs(datadir, exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)