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

BG          = "#09060d"
SURFACE     = "#110b17"
SURFACE2    = "#19101f"
BORDER      = "#281830"
ACCENT      = "#b44dff"
ACCENT2     = "#ff2d78"
TEXT        = "#ecd8f5"
TEXT_DIM    = "rgba(236,216,245,0.35)"
FONT        = "JetBrains Mono, Fira Mono, monospace"

_px   = lambda n: f"{n}px"
_rgba = lambda hex_, a: f"rgba({int(hex_[1:3],16)},{int(hex_[3:5],16)},{int(hex_[5:7],16)},{a})"

header = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [html.Div(style={
                        "width": "18px", "height": "2px",
                        "background": ACCENT if i == 0 else (ACCENT2 if i == 1 else BORDER),
                        "marginBottom": "3px" if i < 2 else "0"
                    }) for i in range(3)],
                    style={"display": "flex", "flexDirection": "column",
                           "marginRight": "14px", "paddingTop": "1px"}
                ),

                html.Div(
                    [
                        html.Div(
                            "STOCKEYE",
                            style={
                                "fontSize": "20px", "fontWeight": "900",
                                "letterSpacing": "6px", "color": TEXT,
                                "lineHeight": "1"
                            }
                        ),
                        html.Div(
                            "MARKET INTELLIGENCE TERMINAL",
                            style={
                                "fontSize": "8px", "letterSpacing": "3px",
                                "color": TEXT_DIM, "marginTop": "3px",
                                "lineHeight": "1"
                            }
                        ),
                    ]
                ),
                
                html.Div(
                    "v3.0",
                    style={
                        "fontSize": "9px", "fontWeight": "700",
                        "color": ACCENT, "letterSpacing": "1px",
                        "border": f"1px solid {ACCENT}",
                        "borderRadius": "2px",
                        "padding": "2px 6px",
                        "marginLeft": "16px",
                        "opacity": "0.7",
                        "alignSelf": "flex-start",
                        "marginTop": "2px"
                    }
                ),
            ],
            style={"display": "flex", "alignItems": "center"}
        ),

        html.Div(
            [
                html.Div(
                    style={
                        "width": "6px", "height": "6px",
                        "borderRadius": "50%",
                        "background": ACCENT,
                        "boxShadow": f"0 0 8px {ACCENT}",
                        "marginRight": "16px",
                        "flexShrink": "0",
                        "animation": "pulse 2s ease-in-out infinite",
                    }
                ),

                html.Div(
                    [
                        html.Span(
                            "_ ",
                            style={
                                "color": ACCENT2, "fontSize": "13px",
                                "fontWeight": "900", "marginRight": "4px",
                                "userSelect": "none"
                            }
                        ),
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
                                "fontSize": "13px",
                                "letterSpacing": "3px",
                                "fontWeight": "700",
                                "width": "110px",
                                "textTransform": "uppercase",
                                "caretColor": ACCENT,
                            }
                        ),
                    ],
                    style={
                        "display": "flex", "alignItems": "center",
                        "background": SURFACE2,
                        "border": f"1px solid {BORDER}",
                        "borderLeft": f"3px solid {ACCENT2}",
                        "padding": "0 14px",
                        "height": "38px",
                        "marginRight": "8px",
                    }
                ),

                html.Button(
                    [
                        html.Span("FETCH", style={"letterSpacing": "2px"}),
                        html.Span(
                            " ›",
                            style={"color": BG, "fontWeight": "900", "fontSize": "16px"}
                        ),
                    ],
                    id="submit_button",
                    n_clicks=0,
                    style={
                        "background": ACCENT,
                        "border": "none",
                        "color": "#06080d",
                        "fontFamily": FONT,
                        "fontSize": "12px",
                        "fontWeight": "900",
                        "letterSpacing": "2px",
                        "padding": "0 20px",
                        "height": "38px",
                        "cursor": "pointer",
                        "transition": "background 0.15s",
                    }
                ),
            ],
            style={"display": "flex", "alignItems": "center"}
        ),
    ],
    style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "padding": "14px 32px",
        "background": SURFACE,
        "borderBottom": f"1px solid {BORDER}",
        "borderTop": f"2px solid {ACCENT}",
        "position": "relative",
    }
)

chart_area = html.Div(
    [
        html.Div(
            [
                html.Span(
                    "◤ ANALYSIS",
                    style={
                        "fontSize": "9px", "letterSpacing": "3px",
                        "color": TEXT_DIM, "fontWeight": "700"
                    }
                ),
                html.Div(
                    style={
                        "flex": "1", "height": "1px",
                        "background": f"linear-gradient(to right, {BORDER}, transparent)",
                        "marginLeft": "12px"
                    }
                ),
            ],
            style={
                "display": "flex", "alignItems": "center",
                "marginBottom": "12px"
            }
        ),

        html.Div(
            dcc.Graph(
                id="graph",
                figure={},
                config={"displayModeBar": False},
                style={"height": "100%"}
            ),
            style={
                "border": f"1px solid {BORDER}",
                "height": "calc(100vh - 130px)",
                "minHeight": "700px",
            }
        ),
    ],
    style={
        "padding": "20px 32px 28px",
        "background": BG,
    }
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; }

            #ticker_input::placeholder {
                color: rgba(216,232,245,0.2);
                letter-spacing: 3px;
            }

            #submit_button:hover {
                background: #00ffca !important;
            }
            #submit_button:active {
                transform: translateY(1px);
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50%       { opacity: 0.3; }
            }

            ::-webkit-scrollbar       { width: 4px; }
            ::-webkit-scrollbar-track { background: #06080d; }
            ::-webkit-scrollbar-thumb { background: #182030; border-radius: 2px; }
        </style>
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

app.layout = html.Div(
    [
        header,
        chart_area,
    ],
    style={
        "background": BG,
        "color": TEXT,
        "fontFamily": FONT,
        "minHeight": "100vh",
        "margin": "0",
    }
)

@app.callback(
    Output("graph", "figure"),
    Input("submit_button", "n_clicks"),
    State("ticker_input", "value")
)
def update_graph(n_clicks: int, symbol: str):
    tables    = database.getTableNames()
    interval  = "1wk"
    frequency = "quarterly"
    name_price       = f"{symbol}_{interval}"
    name_fundamental = f"{symbol}_{frequency}"
    
    palette = [
        ACCENT,
        ACCENT2,
        "#2d78ff", 
        "#ff9d2d",
        "#7a1fff", 
        "#ff3da6",
    ]

    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "secondary_y": True}, {"type": "xy"}],
        ],
        subplot_titles=["PRICE CHART", "INCOME STATEMENT", "CASHFLOW STATEMENT"],
        row_heights=[0.62, 0.38],
        horizontal_spacing=0.06,
        vertical_spacing=0.14,
    )

    fig.update_layout(
        plot_bgcolor  = BG,         
        paper_bgcolor = BG,
        font          = dict(size=11, family=FONT, color=TEXT_DIM),
        xaxis_rangeslider_visible = False,
        legend = dict(
            orientation="h",
            xanchor="center", x=0.5, y=-0.09,
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
            font=dict(size=10, color=TEXT_DIM)
        ),
        height  = 820,
        margin  = dict(l=8, r=8, t=44, b=40),
        hoverlabel = dict(
            bgcolor     = SURFACE,
            bordercolor = ACCENT,
            font        = dict(family=FONT, size=11, color=TEXT)
        ),
    )

    for ann in fig.layout.annotations:
        ann.font.update(size=9, color=TEXT_DIM, family=FONT)
        ann.update(xanchor="left")

    axis_style = dict(
        gridcolor    = BORDER,
        gridwidth    = 1,
        zerolinecolor= BORDER,
        linecolor    = BORDER,
        tickfont     = dict(size=9, color=TEXT_DIM, family=FONT),
        showgrid     = True,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    if not n_clicks:
        return fig
    
    if name_price not in tables:
        pricedata = yf.download(
            symbol, interval=interval,
            start=datetime.now() - timedelta(days=500),
            end=datetime.now(), auto_adjust=True,
            multi_level_index=False,
            progress=False
        )
        database.addTable(name_price, pricedata)
    else:
        pricedata = database.getTable(name_price)
    
    if name_fundamental not in tables:
        ticker        = yf.Ticker(symbol)
        income_stmt   = ticker.get_incomestmt(freq=frequency)
        balance_sheet = ticker.get_balancesheet(freq=frequency)
        cashflow      = ticker.get_cashflow(freq=frequency)
        fundamental   = pd.concat([income_stmt, balance_sheet, cashflow]).T
        fundamental.drop_duplicates(keep="first", inplace=True)
        fundamental.sort_index(inplace=True)
        database.addTable(name_fundamental, fundamental)
    else:
        fundamental = database.getTable(name_fundamental)

    fig.add_trace(
        go.Ohlc(
            x=pricedata.index,
            open=pricedata.Open, high=pricedata.High,
            low=pricedata.Low,   close=pricedata.Close,
            increasing_line_color=ACCENT,
            decreasing_line_color=ACCENT2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "O %{open:.2f}  H %{high:.2f}<br>"
                "L %{low:.2f}  C %{close:.2f}<extra></extra>"
            ),
            showlegend=False,
        ),
        row=1, col=1
    )
    
    for earnings_date in fundamental["TotalRevenue"].dropna().index:
        if pricedata.index[0] <= earnings_date <= pricedata.index[-1]:
            fig.add_vline(
                earnings_date,
                line=dict(dash="dot", color=palette[2], width=1),
                opacity=0.6, col=1, row=1
            )
            
    fundamental.index = pd.to_datetime(fundamental.index).to_period("Q").astype(str)

    for n, bar in enumerate(["TotalRevenue", "NetIncome"]):
        try:
            bardata = fundamental[bar].dropna()
        except KeyError:
            continue
        fig.add_trace(
            go.Bar(
                x=bardata.index, y=bardata,
                name=bar,
                marker=dict(color=palette[n], opacity=0.9, line=dict(width=0)),
                hovertemplate=f"<b>{bar}</b><br>%{{y:,.0f}}<extra></extra>",
            ),
            row=2, col=1, secondary_y=False
        )

    try:
        margin = (fundamental["NetIncome"] / fundamental["TotalRevenue"] * 100).dropna()
        fig.add_trace(
            go.Scatter(
                x=margin.index, y=margin,
                name="NetMargin", mode="lines+markers",
                line=dict(color=palette[5], width=2),
                marker=dict(color=palette[5], size=5, line=dict(width=0)),
                hovertemplate="<b>NetMargin</b><br>%{y:,.1f}%<extra></extra>",
            ),
            row=2, col=1, secondary_y=True
        )
        
        fig.update_yaxes(**axis_style, secondary_y=True, range=[0, 100], row=2, col=1)
        fig.update_yaxes(secondary_y=False, showgrid=False, row=2, col=1)
        
    except Exception:
        pass

    for n, bar in enumerate(["OperatingCashFlow", "InvestingCashFlow", "FinancingCashFlow"]):
        try:
            bardata = fundamental[bar].dropna()
        except KeyError:
            continue
        fig.add_trace(
            go.Bar(
                x=bardata.index, y=bardata,
                name=bar,
                marker=dict(color=palette[n], opacity=0.9, line=dict(width=0)),
                hovertemplate=f"<b>{bar}</b><br>%{{y:,.0f}}<extra></extra>",
            ),
            row=2, col=2
        )

    return fig

if __name__ == "__main__":
    app.run()