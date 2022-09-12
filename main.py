import pandas as pd
import pandas_datareader.data as reader
from fredapi import Fred
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# set_page_config() can only be called once per app, and must be called as the 
# first Streamlit command in your script.
st.set_page_config(page_title='hayes-usd-liquidity-conditions-index', 
    layout='wide', page_icon='🔔') 

# access fred
# import os
# fred = Fred(api_key = os.environ.get('FRED_API_KEY'))
fred = Fred(api_key = st.secrets["FRED_API_KEY"])

# download data from fred 
#
# Fed Balance Sheet: raw values are in millions of dollars => billions of dollars
assets = fred.get_series('WALCL') / 1e3
# Reverse Repo (RRP) Balances held at the NY Fed: raw values are in billions of dollars 
rrp = fred.get_series('RRPONTTLD')
# Treasury's General Account Balance Held at NY Fed: raw values are in billions of dollars
tga = fred.get_series('WTREGEN')

# TODO: make user input
start_date = '2021-12-01'
end_date = dt.datetime.now().strftime('%Y-%m-%d')

# construct the Hayes USD Liquidity Conditions Index
x = (assets - tga).loc[start_date:end_date].dropna()
x = x.reindex(pd.date_range(x.index.min(), x.index.max())).ffill()
HUSDLCI = (x - rrp).dropna() # billions of dollars
HUSDLCI = HUSDLCI / 1e3      # trillions of dollars
HUSDLCI.name = 'HUSDLCI'

# download BTC price data from yahoo 

btc = reader.get_data_yahoo('BTC-USD', start_date, end_date)['Close']
btc.name = 'BTCUSD'

# join data side by side
df = pd.concat([HUSDLCI, btc], axis=1).dropna()
# st.dataframe(df.head())

# calc 30-day rolling correlations
rolling_corr_30d = df.HUSDLCI.rolling(30).corr(df.BTCUSD).dropna()


# --- plot HUSDLCI and BTCUSD --- #

fig = make_subplots(specs=[[{"secondary_y": True}]]) # mk figure with 2 Y-axis

# left y-axis
fig.add_trace( 
    go.Scatter(x=df.index, y=df.BTCUSD, mode='lines', name='BTCUSD',
        line=dict(color='#ed872d', width=1.5)),
    secondary_y=False,
)
fig.update_yaxes(title_text="BTCUSD", showgrid=False, linewidth=2, 
    secondary_y=False,
)
# right y-axis
fig.add_trace( 
    go.Scatter(x=df.index, y=df.HUSDLCI, mode='lines', name='HUSDLCI',
        line=dict(color='#FAFAFA', width=1.5)),
    secondary_y=True,
)
fig.update_yaxes(title_text="HUSDLCI (Trillions of USD)", showgrid=False, 
    linewidth=2, secondary_y=True,
)
# format x-axis
fig.update_xaxes(title_text=None, showgrid=False, linewidth=2)

# format layout
fig.update_layout(paper_bgcolor="#0E1117", plot_bgcolor='#0E1117', 
    yaxis_tickprefix = '', yaxis_tickformat = ',.2f', 
    legend=dict(orientation="h"),
    title_text="BTC Price & Hayes USD Liquidity Conditions Index",
    font=dict(size=18),
    autosize=False,
    width=1200,
    height=600,
)
# render figure
st.plotly_chart(fig, use_container_width=True)
st.markdown('- USD Liquidity (white curve) goes up => Fed (net) prints; goes down => Fed (net) tapers.')
st.markdown("- Data are sourced from [FRED](https://fred.stlouisfed.org/) and Yahoo Finance. The above chart automatically updates when new data become available.")
st.markdown("- Hayes USD Liquidity Conditions Index = The Fed's Balance Sheet — NY Fed Total Amount of Accepted Reverse Repo Bids — US Treasury General Account Balance Held at NY Fed.")
st.markdown("#### The [Hayes USD Liquidity Conditions Index](https://cryptohayes.medium.com/teach-me-daddy-33e7a66dfe76) is a tool devised by King Arthur. Remember his sword is [Excalibur](https://entrepreneurshandbook.co/excalibur-44b2822dc4e6).")


# --- plot their 30-day rolling correlations --- #

fig2 = make_subplots() 

# y-axis
fig2.add_trace( 
    go.Scatter(x=rolling_corr_30d.index, y=rolling_corr_30d, mode='lines', 
               name='30-day rolling correlation', line=dict(color='#a1caf1', width=2))
)
fig2.update_yaxes(title_text="Correlation", showgrid=False, linewidth=2)

# add dashed line at zero
fig2.add_hline(y=0, line_width=0.5, line_dash="dash",)

# format x-axis
fig2.update_xaxes(title_text=None, showgrid=False, linewidth=2)

# format layout
fig2.update_layout(paper_bgcolor="#0E1117", plot_bgcolor='#0E1117', 
    yaxis_tickprefix = '', yaxis_tickformat = ',.2f', 
    # legend=dict(orientation="h"),
    title_text="30-day Rolling Correlation between BTC Price and Hayes USD Liquidity Conditions Index",
    font=dict(size=18),
    autosize=False,
    width=1200,
    height=600,
)
# render figure
st.plotly_chart(fig2, use_container_width=True)



# about
st.markdown("""---""")
st.subheader('Get data-driven insights and Learn DeFi analytics')
st.markdown("- Subscribe to my [newsletter](https://coindataschool.substack.com/about)")
st.markdown("- Follow me on twitter: [@coindataschool](https://twitter.com/coindataschool)")
st.markdown("- Follow me on github: [@coindataschool](https://github.com/coindataschool)")
st.subheader('Support my work')
st.markdown("- Buy me a coffee with ETH: `0x783c5546c863f65481bd05fd0e3fd5f26724604e`")
st.markdown("- [Tip me sat](https://tippin.me/@coindataschool)")