import subprocess
import os
import shutil
import logging

def run_command(command, input_text=None):
    """Run a shell command and print its output."""
    process = subprocess.Popen(command, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=input_text)
    logging.info(stdout)
    if stderr:
        logging.error(stderr, exc_info=True)

def setup_sphinx(docs_folder):
    """Set up Sphinx documentation using sphinx-quickstart."""
    os.makedirs(docs_folder, exist_ok=True)
    os.chdir(docs_folder)
    
    # Sphinx quickstart setup
    sphinx_setup_input = """n
            Askondata
            Helical
            1.0.0

            """
    
    run_command('sphinx-quickstart', input_text=sphinx_setup_input)

def update_conf_py(docs_folder):
    """Update the conf.py file for Sphinx."""
    conf_path = os.path.join(docs_folder, 'conf.py')
    if not os.path.exists(conf_path):
        raise FileNotFoundError(f"Configuration file not found at {conf_path}")

    with open(conf_path, 'r') as file:
        conf_content = file.readlines()

    conf_content.insert(0, "import os\nimport sys\nsys.path.insert(0, os.path.abspath('..'))\n")
    for i, line in enumerate(conf_content):
        if line.startswith("extensions = ["):
            conf_content[i] = "extensions = [\n    'sphinx.ext.autodoc',\n    'sphinx.ext.viewcode',\n    'sphinx.ext.napoleon',\n]\n"
        if line.startswith("html_theme = 'alabaster'"):
            conf_content[i] = "html_theme = 'sphinx_rtd_theme'\n"
    with open(conf_path, 'w') as file:
        file.writelines(conf_content)
        file.writelines("autodoc_mock_imports = ['pymongo']")

def generate_api_docs(docs_folder):
    """Generate API documentation using sphinx-apidoc."""
    # Move to the parent directory of docs to run sphinx-apidoc
    os.chdir(os.path.dirname(docs_folder))
    """Generate API documentation using sphinx-apidoc."""
    #run_command(f'sphinx-apidoc -o {os.path.join(docs_folder)} ./src')
    run_command(f'sphinx-apidoc -o docs ./src')

def update_index_rst(docs_folder):
    """Update index.rst to include modules."""
    index_path = os.path.join(docs_folder, 'index.rst')
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"index.rst file not found at {index_path}")

    with open(index_path, 'a') as file:
        file.write("   modules\n")
        file.write("""                    
.. automodule:: src
   :members:
   :undoc-members:
   :show-inheritance:
""")
        
def build_html_docs(docs_folder):
    """Build HTML documentation."""
    os.chdir(docs_folder)
    run_command('.\\make.bat html')

'''def update_modules_rst1(docs_folder):
    """Update modules.rst with submodules."""
    askondata_src_path = os.path.join(os.path.dirname(docs_folder), 'askondata', 'src')
    modules_path = os.path.join(docs_folder, 'modules.rst')
    
    def get_submodules(path):
        """Recursively get submodules and their Python files."""
        submodules = []
        for root, dirs, files in os.walk(path):
            # Remove unwanted directories
            dirs[:] = [d for d in dirs if d not in {'configurations', 'exceptions', '__pycache__'}]
            
            # Include each Python file as a submodule, except __init__.py
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    module_path = os.path.relpath(os.path.join(root, file), os.path.dirname(docs_folder)).replace(os.sep, '.')
                    module_path = module_path[:-3]  # Remove the '.py' extension
                    submodules.append(module_path)
                
            # Also include the directory itself if it contains an __init__.py file
            if '__init__.py' in files:
                module_path = os.path.relpath(root, os.path.dirname(docs_folder)).replace(os.sep, '.')
                submodules.append(module_path)
        
        return submodules
    
    submodules = get_submodules(askondata_src_path)
    
    # Generating the toctree and automodule sections
    toctree_entries = []
    automodule_entries = []
    
    for module in sorted(submodules):
        #toctree_entries.append(f"   {module}")
        automodule_entries.append(
            f"{module}\n{'-' * len(module)}\n\n.. automodule:: {module}\n   :members:\n   :undoc-members:\n   :show-inheritance:\n"
        )
    
    maxdepth = 4
    
    # Constructing the final content
    modules_content = "askondata\n=========\n\n"
    modules_content += f".. toctree::\n   :maxdepth: {maxdepth}\n\n"
    modules_content += '\n'.join(toctree_entries) + "\n\n"
    modules_content += '\n'.join(automodule_entries)
    
    # Write to file
    with open(modules_path, 'w') as file:
        file.write(modules_content)

def update_modules_rst2(docs_folder):
    """Update modules.rst with submodules."""
    askondata_src_path = os.path.join(os.path.dirname(docs_folder), 'askondata', 'src')
    modules_path = os.path.join(docs_folder, 'modules.rst')
    
    def get_submodules(path):
        """Recursively get submodules and their Python files."""
        submodules = {}
        for root, dirs, files in os.walk(path):
            # Remove unwanted directories
            dirs[:] = [d for d in dirs if d not in {'configurations', 'exceptions', '__pycache__'}]
            
            module_list = []
            # Include each Python file as a submodule, except __init__.py
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    module_path = os.path.relpath(os.path.join(root, file), os.path.dirname(docs_folder)).replace(os.sep, '.')
                    module_path = module_path[:-3]  # Remove the '.py' extension
                    module_list.append(module_path)
                
            # Include the directory itself if it contains an __init__.py file
            if '__init__.py' in files:
                module_path = os.path.relpath(root, os.path.dirname(docs_folder)).replace(os.sep, '.')
                module_list.append(module_path)
                
            if module_list:
                submodules[root] = module_list
        
        return submodules
    
    submodules = get_submodules(askondata_src_path)
    
    # Generate the hierarchical structure
    def generate_entries(submodules):
        entries = []
        for root, modules in sorted(submodules.items()):
            # Determine the main module name and its submodules
            relative_path = os.path.relpath(root, os.path.dirname(docs_folder)).replace(os.sep, '.')
            entries.append(f"{relative_path}\n{'=' * len(relative_path)}\n")
            for module in sorted(modules):
                entries.append(
                    f".. automodule:: {module}\n"
                    f"   :members:\n"
                    f"   :undoc-members:\n"
                    f"   :show-inheritance:\n"
                )
            entries.append('\n')  # Add a newline after each module section
        return entries

    automodule_entries = generate_entries(submodules)
    
    maxdepth = 4
    
    # Constructing the final content
    modules_content = "askondata\n=========\n\n"
    modules_content += f".. toctree::\n   :maxdepth: {maxdepth}\n\n"
    modules_content += '\n'.join(automodule_entries)
    
    # Write to file
    with open(modules_path, 'w') as file:
        file.write(modules_content)'''

def update_modules_rst(docs_folder):
    """Update modules.rst with submodules."""
    askondata_src_path = os.path.join(os.path.dirname(docs_folder), 'src')
    modules_path = os.path.join(docs_folder, 'modules.rst')
    
    def get_submodules(path):
        """Recursively get submodules and their Python files."""
        submodules = {}
        for root, dirs, files in os.walk(path):
            # Remove unwanted directories
            dirs[:] = [d for d in dirs if d not in {'configurations', 'exceptions', '__pycache__'}]
            
            module_list = []
            # Include each Python file as a submodule, except __init__.py
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    module_path = os.path.relpath(os.path.join(root, file), os.path.dirname(docs_folder)).replace(os.sep, '.')
                    module_path = module_path[:-3]  # Remove the '.py' extension
                    module_list.append(module_path)
                
            # Include the directory itself if it contains an __init__.py file
            if '__init__.py' in files:
                module_path = os.path.relpath(root, os.path.dirname(docs_folder)).replace(os.sep, '.')
                module_list.append(module_path)
                
            if module_list:
                submodules[root] = module_list
        
        return submodules
    
    submodules = get_submodules(askondata_src_path)
    
    # Generate the hierarchical structure
    def generate_entries(submodules):
        entries = {}
        for root, modules in sorted(submodules.items()):
            # Determine the main module name and its submodules
            relative_path = os.path.relpath(root, os.path.dirname(docs_folder)).replace(os.sep, '.')
            entries[relative_path] = []
            for module in sorted(modules):
                entries[relative_path].append(module)
        return entries

    automodule_entries = generate_entries(submodules)
    
    # Write the main modules.rst file
    with open(modules_path, 'w') as file:
        file.write("askondata\n=========\n\n")
        file.write(".. toctree::\n   :maxdepth: 1\n   :caption: Contents\n\n")
        
        for module_name in automodule_entries.keys():
            file.write(f"   {module_name}.rst\n")
    
    # Create separate .rst files for each module
    for module_name, submodules in automodule_entries.items():
        module_rst_path = os.path.join(docs_folder, f"{module_name}.rst")
        module_content = f"{module_name}\n{'=' * len(module_name)}\n\n.. toctree::\n   :maxdepth: 2\n\n"
        
        for submodule in submodules:
            submodule_rst_path = submodule.replace('.', '/') + '.rst'
            module_content += f"   {submodule_rst_path}\n"
            
            # Write the content for each submodule .rst file
            submodule_path = os.path.join(docs_folder, submodule_rst_path)
            os.makedirs(os.path.dirname(submodule_path), exist_ok=True)
            with open(submodule_path, 'w') as submodule_file:
                submodule_file.write(
                    f".. automodule:: {submodule}\n"
                    f"   :members:\n"
                    f"   :undoc-members:\n"
                    f"   :show-inheritance:\n\n"
                )
        
        with open(module_rst_path, 'w') as module_file:
            module_file.write(module_content)
             
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}', exc_info=True)

def generate_doc():
    absolute_path = os.path.abspath(os.path.join(__file__, ".."))
    docs_folder = os.path.join(absolute_path, "docs")

    if os.path.exists(docs_folder):
        clear_directory(docs_folder)
    else:
        os.makedirs(docs_folder)

    logging.info("Setting up Sphinx")
    setup_sphinx(docs_folder)

    logging.info("Updating conf.py")
    update_conf_py(docs_folder)

    logging.info("Generating API documentation")
    generate_api_docs(docs_folder)

    logging.info("Updating index.rst")
    update_index_rst(docs_folder)

    logging.info("Building HTML documentation")
    build_html_docs(docs_folder)

    logging.info("Updating modules.rst")
    update_modules_rst(docs_folder)

    logging.info("Generating API documentation")
    generate_api_docs(docs_folder)

    logging.info("Building HTML documentation")
    build_html_docs(docs_folder)

    logging.info("Documentation setup complete.")


if __name__ == "__main__":
    generate_doc()

