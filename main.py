
import os
import re
import subprocess
import shutil

EXECUTE_IN_ALL_FOLDERS: bool = False
REMOVE_ORIGINAL_MODELS: bool = True
DEFAULT_FOLDER: str = os.getcwd()

def execute_python_code_in_directories(script) -> None:
    """
    Executes a Python script in all subdirectories of the given root directory.

    Args:
        root_dir: The root directory to start the search from.
        script_name: The name of the Python script to execute.
    """
    def conditional_call():
        if not EXECUTE_IN_ALL_FOLDERS:
            script()
            return

        for dirpath, dirnames, filenames in os.walk(DEFAULT_FOLDER):
            print(dirpath)
            os.chdir(dirpath)
            script()
    
    return conditional_call

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
    
    if REMOVE_ORIGINAL_MODELS:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            print(file_path)
            if os.path.isfile(file_path) and filename != "__init__.py":
                os.remove(file_path)
                print(f"Removed file: {file_path}")
                    
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

    files = [file for file in os.listdir(f"{folder_path}/dist") if file != "__init__.py" and file.endswith(".py")]
    for file in files:
        file_path = os.path.join(f"{folder_path}/dist", file)
        # Apply your desired logic to each file here
        print(f"Processing file: {file_path}") 
        # Example: Modify the PyArmor import statement
        fix_pyarmor_import(file_path) 

def fix_pyarmor_import(file_path):
    """
    Modifies the PyArmor import statement in the specified file.

    Args:
        file_path: Path to the Python file.
    """

    try:
        with open(file_path, 'r') as f:
            content = f.read()

            # Find the original import line
            match = re.search(r'^from pyarmor_runtime_\w{6} import __pyarmor__', content, re.MULTILINE)

            if match:
                # Replace the line with the modified version
                new_line = f"from .{match.group(0).split(' ')[1]} import __pyarmor__"
                content = content.replace(match.group(0), new_line)

                # Write the modified content back to the file
                with open(file_path, 'w') as f:
                    f.write(content)

                print(f"Import statement in {file_path} modified successfully.")

            else:
                print(f"Import statement not found in {file_path}.")

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

@execute_python_code_in_directories
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
