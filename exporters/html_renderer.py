import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_html(persona, template_name="templates/cv_de.html"):
    """
    Render Jinja2 template to a unicode string.
    Uses FileSystemLoader(..., encoding="utf-8") to force UTF-8 reading on Windows.
    Expects template_name to be either "templates/cv_de.html" or "cv_de.html".
    """
    templates_dir = os.path.join(os.getcwd(), "templates")
    env = Environment(
        loader=FileSystemLoader(templates_dir, encoding="utf-8"),
        autoescape=select_autoescape(["html", "xml"])
    )
    # Accept either a basename or a full path
    tpl_name = os.path.basename(template_name)
    tpl = env.get_template(tpl_name)
    html = tpl.render(persona=vars(persona))
    return html

