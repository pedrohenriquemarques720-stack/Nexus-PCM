import os
import subprocess
import sys

def build_executable():
    print("🔨 Criando executável do Nexus PCM...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "NexusPCM",
        "--add-data", f"app/templates{os.pathsep}templates",
        "--add-data", f"app/static{os.pathsep}static",
        "--hidden-import=jinja2",
        "--hidden-import=sqlalchemy",
        "--hidden-import=aiosqlite",
        "--hidden-import=uvicorn",
        "--hidden-import=bcrypt",
        "--hidden-import=passlib",
        "app/main.py"
    ]
    
    cmd = [c for c in cmd if c]
    subprocess.run(cmd)
    
    print("\n✅ Executável criado em: dist/NexusPCM.exe")

if __name__ == "__main__":
    build_executable()