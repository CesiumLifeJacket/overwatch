from cgi import escape
import jinja2

template = jinja2.Template(open('web-template/directory.html').read())

