from jinja2 import Environment, FileSystemLoader, select_autoescape
import templates

env = Environment(
    loader=FileSystemLoader(templates.__path__[0]),
    autoescape=select_autoescape(['html', 'xml'])
)
