from flask import render_template_string

from front import HTML_TEMPLATE, HEADERS

def landing_page(request, conn, c):
    if request.method == 'GET':
        return get_landing_page(request, conn, c)

def get_landing_page(request, conn, c):
    conn.close()
    return (render_template_string(HTML_TEMPLATE), 200, HEADERS)