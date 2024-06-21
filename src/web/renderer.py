import combustache

from . import models as m

TEMPLATES = combustache.load_templates('./templates', '.html')


def render(
    template_name: str,
    user: m.User | None = None,
    data: dict | None = None,
) -> str:
    render_data = dict(user=user)
    if data is not None:
        render_data = render_data | data
    return combustache.render(TEMPLATES[template_name], render_data, TEMPLATES)
