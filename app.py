from db import Database
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from dash import Dash, html, dcc, Input, Output, State, callback
from datetime import datetime, timedelta

app = Dash(__name__)
database = Database("stockdata")

BG          = "#06080d"
SURFACE     = "#0b0f17"
SURFACE2    = "#10161f"
BORDER      = "#182030"
ACCENT      = "#00e5b0"     
ACCENT2     = "#ff2d78"           
TEXT        = "#d8e8f5"
TEXT_DIM    = "rgba(216,232,245,0.35)"
FONT        = "JetBrains Mono, Fira Mono, monospace"


app.layout = html.Div([

    html.Div([
        html.Div([
            html.Span("◈", style={
                "color": ACCENT, "fontSize": "22px", "marginRight": "10px"
            }),
            html.Span("STOCKEYE", style={
                "fontSize": "18px", "fontWeight": "700",
                "letterSpacing": "4px", "color": TEXT
            }),
            html.Span("  v3.0", style={
                "fontSize": "11px", "color": TEXT_DIM, "marginLeft": "6px"
            }),
        ], style={"display": "flex", "alignItems": "center"}),

        html.Div([
            html.Div([
                html.Span("$", style={
                    "position": "absolute", "left": "14px", "top": "50%",
                    "transform": "translateY(-50%)",
                    "color": ACCENT, "fontSize": "14px", "fontWeight": "700",
                    "pointerEvents": "none"
                }),
                dcc.Input(
                    id="ticker_input",
                    type="text",
                    placeholder="TICKER",
                    style={
                        "background": "transparent",
                        "border": "none",
                        "outline": "none",
                        "color": TEXT,
                        "fontFamily": FONT,
                        "fontSize": "14px",
                        "letterSpacing": "2px",
                        "fontWeight": "600",
                        "paddingLeft": "32px",
                        "paddingRight": "12px",
                        "width": "120px",
                        "textTransform": "uppercase"
                    }
                ),
            ], style={
                "position": "relative",
                "display": "flex",
                "alignItems": "center",
                "background": SURFACE2,
                "border": f"1px solid {BORDER}",
                "borderRadius": "6px",
                "height": "38px",
                "marginRight": "10px"
            }),

            html.Button(
                [html.Span("FETCH DATA  ›")],
                id="submit_button",
                n_clicks=0,
                style={
                    "background": f"linear-gradient(135deg, {ACCENT}, #00d47e)",
                    "border": "none",
                    "borderRadius": "6px",
                    "color": "#0d0f14",
                    "fontFamily": FONT,
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "letterSpacing": "1.5px",
                    "padding": "0 20px",
                    "height": "38px",
                    "cursor": "pointer",
                }
            ),
        ], style={"display": "flex", "alignItems": "center"}),

    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "padding": "16px 28px",
        "borderBottom": f"1px solid {BORDER}",
        "background": SURFACE,
    }),

    html.Div([
        dcc.Graph(
            id="graph",
            figure={},
            config={"displayModeBar": False},
            style={"height": "100%"}
        )
    ], style={
        "padding": "24px 28px",
        "background": BG,
        "minHeight": "calc(100vh - 73px)"
    }),

], style={
    "background": BG,
    "color": TEXT,
    "fontFamily": FONT,
    "minHeight": "100vh",
    "margin": "0",
})

@app.callback(
    Output("graph", "figure"),
    Input("submit_button", "n_clicks"),
    State("ticker_input", "value")
)
def update_graph(n_clicks: int, symbol: str) -> go.Figure:
    tables = database.getTableNames()
    interval = "1d"
    frequency = "quarterly"
    name_price = f"{symbol}_{interval}"
    name_fundamental = f"{symbol}_{frequency}"

    palette = [ACCENT, ACCENT2, "#00aaff", "#ffaa00", "#bf5fff", "#ff6b35"]

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "xy"}, {"type": "xy"}]
        ],
        subplot_titles=["PRICE CHART", "INCOME STATEMENT", "DEBT LEVEL AND COVERAGE"],
        row_heights=[0.62, 0.38],
        horizontal_spacing=0.06,
        vertical_spacing=0.12
    )

    fig.update_layout(
        plot_bgcolor=SURFACE2,
        paper_bgcolor=BG,
        font=dict(size=11, family=FONT, color=TEXT_DIM),
        xaxis_gridcolor=BORDER,
        yaxis_gridcolor=BORDER,
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            xanchor="center", x=0.5, y=-0.08,
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
            font=dict(size=10, color=TEXT_DIM)
        ),
        height=820,
        margin=dict(l=10, r=10, t=48, b=40),
        hoverlabel=dict(
            bgcolor=SURFACE,
            bordercolor=BORDER,
            font=dict(family=FONT, size=11, color=TEXT)
        ),
    )

    for ann in fig.layout.annotations:
        ann.font.update(size=10, color=TEXT_DIM, family=FONT)
        ann.update(x=ann.x, xanchor="left")

    axis_style = dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(size=9, color=TEXT_DIM),
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    fig.update_xaxes(col=1, row=2, **axis_style)
    fig.update_xaxes(col=2, row=2, **axis_style)

    if not n_clicks:
        return fig

    if name_fundamental not in tables:
        ticker = yf.Ticker(symbol)
        income_stmt   = ticker.get_incomestmt(freq=frequency)
        balance_sheet = ticker.get_balancesheet(freq=frequency)
        cashflow      = ticker.get_cashflow(freq=frequency)
        fundamental   = pd.concat([income_stmt, balance_sheet, cashflow]).T
        fundamental.drop_duplicates(keep="first", inplace=True)
        fundamental.sort_index(inplace=True)
        database.addTable(name_fundamental, fundamental)
    else:
        fundamental = database.getTable(name_fundamental)

    if name_price not in tables:
        pricedata = yf.download(symbol, interval=interval, start=datetime.now()-timedelta(days=500),
                                end=datetime.now(), auto_adjust=True, multi_level_index=False)
        database.addTable(name_price, pricedata)
    else:
        pricedata = database.getTable(name_price)

    fig.add_trace(
        go.Ohlc(
            x=pricedata.index,
            open=pricedata.Open,
            high=pricedata.High,
            low=pricedata.Low,
            close=pricedata.Close,
            increasing_line_color=ACCENT,
            decreasing_line_color=ACCENT2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "O %{open:.2f}  H %{high:.2f}<br>"
                "L %{low:.2f}  C %{close:.2f}<extra></extra>"
            ),
            showlegend=False,
        ), row=1, col=1
    )

    group1 = ["TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome"]
    for n, bar in enumerate(group1):
        try:
            bardata = fundamental[bar].dropna()
        except KeyError:
            continue
        fig.add_trace(
            go.Bar(
                x=bardata.index,
                y=bardata,
                name=bar,
                marker=dict(
                    color=palette[n],
                    opacity=0.85,
                    line=dict(width=0)
                ),
                hovertemplate=f"<b>{bar}</b><br>%{{y:,.0f}}<extra></extra>"
            ), row=2, col=1
        )

    group2 = ["TotalDebt", "FreeCashFlow", "CashAndCashEquivalents", "StockholdersEquity"]
    for n, bar in enumerate(group2):
        try:
            bardata = fundamental[bar].dropna()
        except KeyError:
            continue
        fig.add_trace(
            go.Bar(
                x=bardata.index,
                y=bardata,
                name=bar,
                marker=dict(
                    color=palette[n],
                    opacity=0.85,
                    line=dict(width=0)
                ),
                hovertemplate=f"<b>{bar}</b><br>%{{y:,.0f}}<extra></extra>"
            ), row=2, col=2
        )

    return fig

if __name__ == "__main__":
    app.run()