from bokeh.charts import Bar, Area
from bokeh.embed import file_html
from bokeh.resources import INLINE
from bokeh.charts.attributes import cat
from positions import portfolio_utils as pu


def get_position_data(positions):
    """Fetches metrics for given Position objects to be used for analysis views"""

    # columns to return
    cols = ["Name", "Symbol", "Shares", "Market Value ($)", "Last Price ($)", "Day's Change ($)", "Day's Change (%)",
            "Day's Gain/Loss ($)", "Cost Basis ($)", "Total Gain/Loss ($)", "Overall Return (%)", "Account"]

    df = pu.get_positions_dataframe(positions, nthreads=10)

    # derived values
    df["Market Value ($)"] = df["Shares"] * df["Last Price ($)"]
    df["Day's Gain/Loss ($)"] = df["Shares"] * df["Day's Change ($)"]
    df["Total Gain/Loss ($)"] = df["Market Value ($)"] - df["Cost Basis ($)"]
    df["Overall Return (%)"] = 100. * df["Total Gain/Loss ($)"] / df["Cost Basis ($)"]
    df["Concentration"] = 100. * df["Market Value ($)"] / df["Market Value ($)"].sum()

    return df


def get_concentration_bar_chart(df):
    """Creates bar chart visualizing portfolio concentration by position"""
    df = df[["Symbol", "Concentration"]].sort_values("Concentration", ascending=False)

    chart = Bar(
        df,
        label=cat(columns='Symbol', sort=False),
        values='Concentration',
        title='Portfolio Concentration By Position',
        ylabel='Concentration (%)',
        plot_width=1200,
        plot_height=400,
        legend=False,
        color='#4285f4'
    )

    return file_html(chart, INLINE)


def get_concentration_area_chart(df):
    """Creates area chart visualizing portfolio concentration by position"""
    df = (
        df[["Symbol", "Concentration"]]
        .sort_values("Concentration")
        .set_index("Symbol")
        .cumsum()
        .reset_index()
        .drop("Symbol", axis=1)
    )

    chart = Area(
        df['Concentration'].astype(float),
        title='Cumulative Portfolio Concentration',
        ylabel='% of Total Value',
        xlabel='Number of Positions',
        plot_width=1200,
        plot_height=400,
        legend=False,
        color='#4285f4'
    )

    chart.x_range.start, chart.x_range.end = 0, df.shape[0]

    return file_html(chart, INLINE)
