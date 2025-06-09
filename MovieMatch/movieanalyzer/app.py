from dash import Dash
from .layout import layout
from .callbacks import register_callbacks

app = Dash(__name__)
app.layout = layout
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True) 