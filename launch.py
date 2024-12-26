from tkinter import Tk, filedialog
import json
import os
from typing import Callable


def get_input_file() -> str:
    root = Tk()
    root.withdraw()  # Hide the Tkinter root window
    file_path = filedialog.askopenfilename(
        title="Select a target Preset file (.json)",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    root.destroy()
    return file_path

# 1.1.4 and below: 1
# v2.0 and above: 2
def detect_json_version(data: dict) -> int:
    # 要素を検証してみる
    for k, v in data.items():
        if isinstance(v, dict):
            return 1 # v2 なら v1 へ
        elif isinstance(v, list):
            return 2 # v1 なら v2 へ
        else:
            raise ValueError("Unknown Template")

def convert_v1_1_4_to_v2_0(data: dict) -> dict:
    """
    v2.0 を v1.1.4 に変換
    """
    v2data = {}
    for _, v in data.items():
        v2data[v[0]] = {
            "coordinates": v[1],
            "orientation": v[2],
            "direction": v[3]
        }
    return v2data

def convert_v2_0_to_v1_1_4(data: dict) -> dict:
    v1data = {}
    for (k, v) in data.items():
        v1data[k] = [v["coordinates"], v["orientation"], v["direction"]]
    return v1data

def get_convert_function(target_version: int) -> Callable:
    vermap = {
        1: convert_v2_0_to_v1_1_4,
        2: convert_v1_1_4_to_v2_0
    }
    return vermap[target_version]

def main():
    version_map = {
        1: "autogarden.json",
        2: "auto_garden.current.json"
    }
    input_file = get_input_file()
    target_ver = int(input("-= Enter converted version =-\n[Auto (if v2.0 to 1.1.4) (if v1.1.4 to 2.0)]: 0\n[v1.1.0-v1.1.4]: 1\n[β2.0+]: 2\nPlease enter the number [0/1/2]: "))

    if not os.path.exists(input_file):
        raise ValueError("Input file does not exist.")

    with open(input_file, "r") as f:
        data = json.load(f)

    # 出力対象を決める
    if target_ver == 0:
        version = detect_json_version(data)
    else:
        version = target_ver
    func = get_convert_function(version)
    data = func(data)

    output_file = os.path.splitext(input_file)[0] + f"-{version_map[version]}"
    with open(os.path.join(os.getcwd(), "outputs", output_file), "w") as f:
        if version == 1:
            # v1 なら並列に出力
            f.write(str(data).replace("'", '"'))
        else:
            json.dump(data, f, indent=2)
    print(f"Converted file saved to {output_file}")

if __name__ == "__main__":
    main()