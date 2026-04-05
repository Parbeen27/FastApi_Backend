import subprocess
import sys

# List of required packages
packages = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "python-jose",
    "bcrypt",
    "passlib[bcrypt]"
]

def install(package):
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")

def main():
    print("Starting installation of dependencies...\n")
    
    for package in packages:
        install(package)
    
    print("\n✅ All dependencies installed!")

if __name__ == "__main__":
    main()