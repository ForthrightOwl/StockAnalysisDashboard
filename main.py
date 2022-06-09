from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import datetime as dt
app = Dash(__name__)

"""Styling parameters"""
BACKGROUND_COLOR = "#edf3f4"
CONTENT_COLOR = "white"
TEXT_COLOR = "#718BA5"
BORDER_COLOR = "#8EA9C1"
FONT = "Times New Roman"


app.layout= html.Div(children=[
    html.H1(children=["Stock Analysis Dashboard"],
            style={"font-family":FONT, "color":TEXT_COLOR, "text-align":"center",
                   "background-color":BACKGROUND_COLOR, "font-size":40}),

    html.Div(
        dcc.Tabs(id="tab-bar", value="multiples", children=[
            dcc.Tab(label="Filters", value="filters",
                    style={"font-family":FONT, "font":TEXT_COLOR, "background-color":BACKGROUND_COLOR, "font-size":20}),
            dcc.Tab(label="Multiples", value="multiples",
                    style={"font-family":FONT, "font":TEXT_COLOR, "background-color":BACKGROUND_COLOR, "font-size":20}),
            dcc.Tab(label="Financial Statements Hist", value="fin-st-hist",
                    style={"font-family":FONT, "font":TEXT_COLOR, "background-color":BACKGROUND_COLOR, "font-size":20}),
            dcc.Tab(label="Financial Statements Comp", value="fin-st-comp",
                    style={"font-family":FONT, "font":TEXT_COLOR, "background-color":BACKGROUND_COLOR, "font-size":20})
        ], style={"border-color": BORDER_COLOR, "border-width": "1.5px", "border-style":"solid"}
                 )
    ),

    html.Div(id="content")

],
    style={"background-color":BACKGROUND_COLOR}
)

@app.callback(
    Output("content", "children"),
    Input("tab-bar", "value")
)
def tab_selector(tab):
    if tab == "filters":
        return html.Div(children=[

            html.H1(children=["Filters"],
                    style={"font-family":FONT, "color":TEXT_COLOR, "text-align":"center",
                   "background-color":BACKGROUND_COLOR, "font-size":30}),

        ],
        style={"background-color": BACKGROUND_COLOR, "border-color": BORDER_COLOR, "border-width": "1.5px",
               "border-style":"solid", "margin-top":"1cm"})

    elif tab == "multiples":
        return html.Div(children=[

            html.H1(children=["Valuation Multiples"],
                    style={"font-family":FONT, "color":TEXT_COLOR, "text-align":"center",
                   "background-color":BACKGROUND_COLOR, "font-size":30}),

            html.Div(children=[
                html.Div([
                    html.Div(children=[
                        html.Div("Filters", style={"margin-left":"2%", "margin-top":"2%"}),
                        html.Div("Choose a multiple:", style={"margin-left":"2%"}),
                        dcc.Dropdown(id="multiple-dropdown",
                                     options=[
                                         {"label": "P/E", "value": "pe"},
                                         {"label": "EV/EBITDA", "value": "evebitda"},
                                         {"label": "P/FCFE", "value": "pfcfe"}
                                     ],
                                     style={"width":"95%", "margin-left":"2%"}),
                        html.Div("Choose a time period", style={"margin-left":"2%"}),
                        dcc.DatePickerRange(id="tsdate", start_date=dt.date(2020, 1, 1), end_date=dt.date.today(),
                                            style={"width": "95%", "margin-left": "2%", "margin-bottom":"2%"}
                                            )
                    ],
                    style={"background-color":CONTENT_COLOR, "border-color": BORDER_COLOR, "border-width": "1.5px",
                       "border-style":"solid", "margin-top":"1cm", "width":"95%", "margin":"auto", "margin-bottom":"1cm"}),

                    html.Div(children=[
                        html.Div("Income measure growth", style={"margin-left":"2%", "margin-top":"2%"}),
                        dcc.Graph(id="income-graph")
                    ], style={"background-color":CONTENT_COLOR, "border-color": BORDER_COLOR, "border-width": "1.5px",
                       "border-style":"solid", "margin-top":"1cm", "width":"95%", "margin":"auto"})

                ], style={"width":"40%", "display":"inline-block"}),

                html.Div([
                    html.Div(children=[
                        html.Div("Timeseries Analysis", style={"margin-left":"2%", "margin-top":"2%"}),
                        html.Div("Choose a graph:", style={"margin-left":"2%"}),
                        dcc.Dropdown(id="time-mult-dropdown",
                                     options=[
                                         {"label":"vs. Comparison group", "value":"multiples"},
                                         {"label": "Difference", "value": "diff"},
                                         {"label": "Percentile", "value": "perc"}
                                     ], style={"margin-left": "1%", "width":"40%"}),
                        dcc.Graph(id="time-mult-graph",)
                        ],
                        style={"background-color":CONTENT_COLOR, "border-color": BORDER_COLOR, "border-width": "1.5px",
                            "border-style":"solid", "margin-bottom":"1cm", "width":"95%", "margin":"auto"}),

                    html.Div(children=[
                             html.Div("Value change composition", style={"margin-top":"2%", "margin-left":"2%"}),
                             html.Div("This graph breaks down the change in value into change in multiple and change in income.",
                                      style={"margin-left":"2%"}),
                             dcc.Graph(id="comp-graph",)
                             ],
                        style={"background-color": CONTENT_COLOR, "border-color": BORDER_COLOR, "border-width": "1.5px",
                            "border-style": "solid", "margin":"auto","margin-top":"1cm", "width": "95%"})
                ], style={"width":"60%", "display":"inline-block", "margin-bottom":"3cm"})
            ], style={"margin-top":"1cm", "display":"flex", "justify-content":"space-around"})
    ])

    elif tab == "fin-st-hist":
        return "Historical financial statements tab"
    elif tab == "fin-st-comp":
        return "Financial statements comparison tab"




app.run_server(debug=True)