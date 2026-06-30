from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

def get_templates(template_name):
    try:
        # Load the template
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        env = Environment(loader=FileSystemLoader(template_dir))
        return env.get_template(template_name)
    except TemplateNotFound as e:
        print(f"Error: Template '{template_name}' not found in '{template_dir}'.")
        return None

