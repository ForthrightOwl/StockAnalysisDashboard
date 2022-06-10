from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
from filters import filters_layout
from multiples import multiples_layout
from app import app
import functions


app_layout = html.Div(children=[

    html.H1(children=["Stock Analysis Dashboard"],
            style={"font-family":functions.FONT, "color":functions.TEXT_COLOR, "text-align":"center",
                   "background-color":functions.BACKGROUND_COLOR, "font-size":40}),

    html.Div(
        dcc.Tabs(id="tab-bar", value="filters", children=[
            dcc.Tab(label="Filters", value="filters",
                    style={"font-family":functions.FONT, "font":functions.TEXT_COLOR,
                           "background-color":functions.BACKGROUND_COLOR, "font-size":20}),
            dcc.Tab(label="Multiples", value="multiples",
                    style={"font-family":functions.FONT, "font":functions.TEXT_COLOR,
                           "background-color":functions.BACKGROUND_COLOR, "font-size":20}),
            dcc.Tab(label="Financial Statements Hist", value="fin-st-hist",
                    style={"font-family":functions.FONT, "font":functions.TEXT_COLOR,
                           "background-color":functions.BACKGROUND_COLOR, "font-size":20}),
            dcc.Tab(label="Financial Statements Comp", value="fin-st-comp",
                    style={"font-family":functions.FONT, "font":functions.TEXT_COLOR,
                           "background-color":functions.BACKGROUND_COLOR, "font-size":20})
        ],
                 style={"border-color": functions.BORDER_COLOR, "border-width": "1.5px", "border-style":"solid"}
                 )
    ),

    html.Div(id="content"),
    dcc.Store(id="stock"),
    dcc.Store(id="comps")

],
    style={"background-color":functions.BACKGROUND_COLOR}
)

@app.callback(
    Output("content", "children"),
    Input("tab-bar", "value")
)
def tab_selector(tab):
    if tab == "filters":
        return filters_layout
    elif tab == "multiples":
        return multiples_layout
    elif tab == "fin-st-hist":
        return html.Div(children=[

            html.H1(children=["Historical Financial Statements"],
                    style={"font-family": functions.FONT, "color": functions.TEXT_COLOR, "text-align": "center",
                           "background-color": functions.BACKGROUND_COLOR, "font-size": 30}),

            html.Div(children=[
                html.Div("Select a statement:", style={"margin-left":"1%"}),
                dcc.Dropdown(id="hist-fin-statement-select",
                             options=[
                                 {"label": "Income Statement", "value": "ins"},
                                 {"label": "Balance Sheet", "value": "bss"},
                                 {"label": "Cash Flow Statement", "value": "cfs"}
                             ], style={"margin-left": "1%", "width": "40%"})
            ]),

            dash_table.DataTable()

        ], style={"width":"90%", "margin":"auto"})

    elif tab == "fin-st-comp":
        return "Financial statements comparison tab"
