from dash import html, dcc
from dash.dependencies import Input, Output
import datetime as dt
import functions
from app import app
import plotly.express as px

"""Graphing functions"""
def comparison_graph(stock, comp_ratio, ratio_function, api_key):
    stck = ratio_function(stock, api_key)
    cpgrp = comp_ratio
    fig = px.line(y=[stck, cpgrp])
    return fig

def difference_graph(stock, comp_ratio, ratio_function, api_key):
    df = functions.stock_comparison_difference(stock, comp_ratio, ratio_function, api_key)
    fig = px.line(df)
    return fig

def percentile_difference_graph(stock, comp_ratio, ratio_function, api_key):
    df = functions.stock_comparison_difference_percentile(stock, comp_ratio, ratio_function, api_key)
    fig = px.line(df)
    return fig

def contribution_graph(function, ticker, start_date, api_key):
    df = function(ticker, start_date, api_key)
    fig = px.bar(df)
    return fig

def income_measure_graph():
    years = ["2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012"]
    data = functions.request_fs("income-statement", "AAPL", 400, functions.API_KEY)
    df = functions.curate_is(data).transpose()[years] / 1000000
    df2 = df.loc["Revenue"]
    fig = px.bar(df2)
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
                                     value="pe",
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
                        dcc.Graph(id="income-graph", figure=income_measure_graph())
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
                                     ],
                                     value="multiples",
                                     style={"margin-left": "1%", "width":"40%"}),
                        dcc.Graph(id="time-mult-graph")
                        ],
                        style={"background-color":functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                            "border-style":"solid", "margin-bottom":"1cm", "width":"95%", "margin":"auto"}),

                    html.Div(children=[
                             html.Div("Value change composition", style={"margin-top":"2%", "margin-left":"2%"}),
                             html.Div("This graph breaks down the change in value into change in multiple and change in income.",
                                      style={"margin-left":"2%"}),
                             dcc.Graph(id="comp-graph")
                             ],
                        style={"background-color": functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                            "border-style": "solid", "margin":"auto","margin-top":"1cm", "width": "95%"})
                ], style={"width":"60%", "display":"inline-block", "margin-bottom":"3cm"})
            ], style={"margin-top":"1cm", "display":"flex", "justify-content":"space-around"})
    ],style={"width":"90%", "margin":"auto"})

@app.callback(
    Output("time-mult-graph", "figure"),
    Input("stock", "data"),
    Input("comps_pe", "data"),
    Input("comps_evebitda", "data"),
    Input("comps_pfcfe", "data"),
    Input("multiple-dropdown", "value"),
    Input("time-mult-dropdown", "value")
)
def multiple_time_graph(ticker, comps_pe, comps_evebitda, comps_pfcfe, multiple, graph_type):
    if multiple == "pe":
        func = functions.price_earnings
        comp_ratio = comps_pe
    elif multiple == "evebitda":
        func = functions.ev_ebitda
        comp_ratio = comps_evebitda
    elif multiple == "pfcfe":
        func = functions.price_fcfe
        comp_ratio = comps_pfcfe

    if graph_type == "multiples":
        fig = comparison_graph(ticker, comp_ratio, func, functions.API_KEY)
        return fig
    elif graph_type == "diff":
        fig = difference_graph(ticker, comp_ratio, func, functions.API_KEY)
        return fig
    elif graph_type == "perc":
        fig = percentile_difference_graph(ticker, comp_ratio, func, functions.API_KEY)
        return fig

@app.callback(
    Output("comp-graph", "figure"),
    Input("multiple-dropdown", "value"),
    Input("stock", "data"),
    Input("tsdate", "start_date")
)
def graph_contribution(func, ticker, date):
    time_date = dt.datetime.strptime(date, "%Y-%m-%d")
    year = int(time_date.year)
    month = int(time_date.month)
    day = int(time_date.day)
    start_date = dt.date(year, month, day)
    if func == "pe":
        function = functions.price_earnings_contribution
        fig = contribution_graph(function, ticker, start_date, functions.API_KEY)
        return fig
    elif func == "evebitda":
        function = functions.ev_ebitda_contribution
        fig = contribution_graph(function, ticker, start_date, functions.API_KEY)
        return fig
    elif func == "pfcfe":
        function = functions.price_fcfe_contribution
        fig = contribution_graph(function, ticker, start_date, functions.API_KEY)
        return fig


