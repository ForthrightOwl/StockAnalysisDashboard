from dash import html, dcc
from dash.dependencies import Input, Output
import functions
from app import app


sp500 = functions.sp500_const(functions.API_KEY)["symbol"]

filters_layout = html.Div(children=[

            html.H1(children=["Filters"],
                    style={"font-family":functions.FONT, "color":functions.TEXT_COLOR, "text-align":"center",
                   "background-color":functions.BACKGROUND_COLOR, "font-size":30}),

            html.Div(children=[
                html.Div(children=[
                    html.Div("Company analysed", style={"margin-left":"2%", "margin-top":"2%"}),
                    html.Div("Put in a company ticker:", style={"margin-left":"2%"}),
                    dcc.Dropdown(id="ticker",
                                    options=sp500,
                                    clearable=False, style={"margin-left":"2%", "width":"95%"})
                ],
                    style={"background-color":functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                            "border-style":"solid", "margin-top":"1cm", "width":"95%", "margin":"auto", "padding-bottom":"2%",
                            "margin-bottom":"1cm"}),

                html.Div(children=[
                    html.Div("Comparison group", style={"margin-left":"2%", "margin-top":"2%"}),
                    html.Div(children=["Pre-defined categories:"], style={"margin-left":"2%"}),
                    dcc.Dropdown(id="preset_comp_groups",
                                 options=[
                                     {"label": "Sector", "value": "sector"},
                                     {"label": "Industry", "value": "industry"},
                                     {"label": "Custom", "value":"custom"}
                                 ],
                                 style={"width": "95%", "margin-left": "2%"}),
                    html.Div(children=["Add company by ticker:"], style={"margin-left":"2%"}),
                    dcc.Dropdown(
                        id="comp_group_select",
                        options=[{"label": i, "value": i} for i in sp500],
                        multi=True,
                        style={"margin-left":"2%", "width":"95%"}
                    )
                ], style={"background-color":functions.CONTENT_COLOR, "border-color": functions.BORDER_COLOR, "border-width": "1.5px",
                   "border-style":"solid", "margin-top":"1cm", "width":"95%", "margin":"auto", "padding-bottom":"2%"}),


            ], style={"margin":"auto", "width":"40%", "margin-bottom":"5cm", "background-color":functions.BACKGROUND_COLOR})],
        style={"background-color":functions.BACKGROUND_COLOR, "margin-top":"1cm", "width":"95%", "margin":"auto", "padding-bottom":"20cm"})

@app.callback(
    Output("comp_group_select", "value"),
    Input("ticker", "value"),
    Input("preset_comp_groups", "value")
)
def select_comp_group(ticker, preset):
    sp_df = functions.sp500_const(functions.API_KEY)
    if preset == "sector":
        sector = sp_df.loc[sp_df["symbol"] == ticker]["sector"].values.item()
        comps = sp_df.loc[sp_df["sector"] == sector]
        return comps["symbol"]
    elif preset == "industry":
        industry = sp_df.loc[sp_df["symbol"] == ticker]["subSector"].values.item()
        comps = sp_df.loc[sp_df["subSector"] == industry]
        return comps["symbol"]
    else:
        pass

@app.callback(
    Output("stock", "data"),
    Output("comps", "data"),
    Input("ticker", "value"),
    Input("comp_group_select", "value")
)
def store_data(ticker, comp_group):
    stock = ticker
    comps = comp_group
    return stock, comps
