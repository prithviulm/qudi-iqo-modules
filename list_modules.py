import os

def list_modules(directory):
    """Recursively list all Python modules in a directory."""
    modules = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.relpath(os.path.join(root, file), directory)
                module_path = module_path.replace(os.sep, ".").rsplit(".", 1)[0]  # Format as Python module
                modules.append(module_path)
    return modules

# Example usage
directories = ["src/qudi/hardware", "src/qudi/interface", "src/qudi/util", "src/qudi/logic"]

for directory in directories:
    print(f"Modules in {directory}:")
    for module in list_modules(directory):
        print(f"    {module}")
