from jinja2 import Environment, FileSystemLoader


def render(template_name, folder_templates='templates', **kwargs):
    env_templates = Environment()
    env_templates.loader = FileSystemLoader(folder_templates)
    template = env_templates.get_template(template_name)
    return template.render(**kwargs)
