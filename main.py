
import os
import subprocess
import shutil

def obfuscate_folder(folder_path, dist_folder_name):
    """
    Obfuscates all Python files within a given folder using PyArmor.

    Args:
        folder_path: Path to the folder containing Python files.
        dist_folder_name: Name of the distribution folder to be created.
    """

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                dist_file_path = os.path.join(root, dist_folder_name, file)
                os.makedirs(os.path.dirname(dist_file_path), exist_ok=True)

                try:
                    subprocess.run(["pyarmor", "gen", file_path], check=True)

                    print(f"Obfuscated: {file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Error obfuscating {file_path}: {e}")
                    
    subprocess.run(["rm", "-r", f"{folder_path}/dist"], check=True)
    subprocess.run(["mv", "dist/", f"{folder_path}/"], check=True)

def create_init_file(folder_path, dist_folder_name):
    """
    Creates or updates __init__.py file to import obfuscated modules.

    Args:
        folder_path: Path to the folder containing Python files.
        dist_folder_name: Name of the distribution folder.
    """

    init_file_path = os.path.join(folder_path, "__init__.py")

    with open(init_file_path, "w") as f:
        files = [file for file in os.listdir(folder_path) if file != "__init__.py" and file.endswith(".py")]

        values: str = ""

        for file in files:
            module_name = os.path.splitext(file)[0]
            relative_dist_path = os.path.join(dist_folder_name, file)
            values += f"from .dist import {module_name}\n"
    
        f.write(values)
        f.close()

def run():
    """
    Main function to execute the obfuscation process.
    """

    root_folders = ["models", "wizards", "controllers"]
    dist_folder_name = "dist"

    for folder in root_folders:
        folder_path = os.path.join(".", folder)

        if os.path.exists(f"{folder_path}/dist"):
            subprocess.run(["rm", "-r", f"{folder_path}/dist"], check=True)

        if os.path.exists(folder_path):
            obfuscate_folder(folder_path, dist_folder_name)
            create_init_file(folder_path, dist_folder_name)

if __name__ == "__main__":
    run()
