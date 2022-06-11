from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
from filters import filters_layout
from multiples import multiples_layout
from app import app
import functions

fin_stat_hist = html.Div(children=[

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

            dash_table.DataTable(id="hist_main_table")

        ], style={"width":"90%", "margin":"auto"})

@app.callback(
    Output("hist_main_table", "data"),
    Input("hist-fin-statement-select", "value")
)
def data_select(statement):
    years = ["2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012"]
    data = functions.request_fs("income-statement", "AAPL", 400, functions.API_KEY)
    df = functions.curate_is(data).transpose()[years] / 1000000
    df.reset_index(inplace=True)
    data2 = df.to_dict("records")
    return data2