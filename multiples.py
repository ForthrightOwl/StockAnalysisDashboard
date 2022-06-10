from dash import html, dcc
from dash.dependencies import Input, Output
import datetime as dt
import functions
from app import app
import plotly.express as px

"""Graphing functions"""
def comparison_graph(stock, comp_group, ratio_function, api_key):
    stck = ratio_function(stock, api_key)
    cpgrp = functions.avg_ratio(ratio_function, comp_group, api_key)
    fig = px.line(x=[stck, cpgrp])
    return fig

multiples_layout = html.Div(children=[

            html.H1(children=["Valuation Multiples"],
                    style={"font-family": functions.FONT, "color": functions.TEXT_COLOR, "text-align": "center",
                            "background-color": functions.BACKGROUND_COLOR, "font-size": 30}),

            html.Div(children=[
                html.Div([
                    html.Div(children=[
                        html.Div("Filters", style={"margin-left": "2%", "margin-top": "2%"}),
                        html.Div("Choose a multiple:", style={"margin-left": "2%"}),
                        dcc.Dropdown(id="multiple-dropdown",
                                     options=[
                                         {"label": "P/E", "value": "pe"},
                                         {"label": "EV/EBITDA", "value": "evebitda"},
                                         {"label": "P/FCFE", "value": "pfcfe"}
                                     ],
                                     style={"width":"95%", "margin-left":"2%"}),
                        html.Div("Choose a time period", style={"margin-left":"2%"}),
                        dcc.DatePickerRange(id="tsdate", start_date=dt.date(2020, 1, 1), end_date=dt.date.today(),
                                            style={"width": "95%", "margin-left": "2%", "margin-bottom": "2%"}
                                            )
                    ],
                    style={"background-color": functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR,
                           "border-width": "1.5px", "border-style": "solid", "margin-top": "1cm", "width": "95%",
                            "margin": "auto", "margin-bottom": "1cm"}),

                    html.Div(children=[
                        html.Div("Income measure growth", style={"margin-left":"2%", "margin-top":"2%"}),
                        dcc.Graph(id="income-graph")
                    ], style={"background-color":functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                                "border-style": "solid", "margin-top": "1cm", "width": "95%", "margin": "auto"})

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
                        style={"background-color":functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                            "border-style":"solid", "margin-bottom":"1cm", "width":"95%", "margin":"auto"}),

                    html.Div(children=[
                             html.Div("Value change composition", style={"margin-top":"2%", "margin-left":"2%"}),
                             html.Div("This graph breaks down the change in value into change in multiple and change in income.",
                                      style={"margin-left":"2%"}),
                             dcc.Graph(id="comp-graph",)
                             ],
                        style={"background-color": functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                            "border-style": "solid", "margin":"auto","margin-top":"1cm", "width": "95%"})
                ], style={"width":"60%", "display":"inline-block", "margin-bottom":"3cm"})
            ], style={"margin-top":"1cm", "display":"flex", "justify-content":"space-around"})
    ],style={"width":"90%", "margin":"auto"})

"""@app.callback(
    Output("time-mult-graph", "figure"),
    Input("stock", "data"),
    Input("comps", "data"),
    Input("multiple-dropdown", "value")
)
def multiple_time_graph(ticker, comp_group, multiple):
    if multiple == "pe":
        fig = comparison_graph(ticker, comp_group, functions.price_earnings, functions.API_KEY)
        return fig
    elif multiple == "evebitda":
        fig = comparison_graph(ticker, comp_group, functions.ev_ebitda, functions.API_KEY)
        return fig
    elif multiple == "pfcfe":
        fig = comparison_graph(ticker, comp_group, functions.price_fcfe, functions.API_KEY)
        return fig"""

