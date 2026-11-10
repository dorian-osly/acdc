import os
import sys
import platform
import subprocess

def build():
    print("Building Animal Crossing Dynamic Clock executable...")
    sep = ";" if platform.system() == "Windows" else ":"
    icon_ext = "ico" if platform.system() == "Windows" else "png"
    icon_path = os.path.join("assets", f"icon.{icon_ext}")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--clean",
        "--name=AnimalCrossingDynamicClock",
        f"--add-data=assets{sep}assets",
        "main.py"
    ]

    if os.path.exists(icon_path):
        cmd.insert(6, f"--icon={icon_path}")

    cmd.insert(4, "--onefile")

    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\nSUCCESS! Executable created in ./dist/")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")

if __name__ == "__main__":
    build()
