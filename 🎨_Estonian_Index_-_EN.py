import streamlit as st
import plotly.express as px
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import plotly.graph_objects as go
import pandas as pd
from StreamlitHelper import Toc, get_img_with_href, read_df, create_table
import numpy as np

st.set_page_config(
    page_title="Art Index",
    page_icon="data/Vertical-BLACK2.ico",
)
# inject CSS to hide row indexes and style fullscreen button
inject_style_css = """
            <style>
            /*style hide table row index*/
            thead tr th:first-child {display:none}
            tbody th {display:none}
            
            /*style fullscreen button*/
            button[title="View fullscreen"] {
                background-color: #004170cc;
                right: 0;
                color: white;
            }

            button[title="View fullscreen"]:hover {
                background-color:  #004170;
                color: white;
                }
            a { text-decoration:none;}
            </style>
            """
st.markdown(inject_style_css, unsafe_allow_html=True)

def create_paragraph(text):
    st.markdown('<span style="word-wrap:break-word;">' + text + '</span>', unsafe_allow_html=True)
    
df = read_df('data/auctions_clean.csv')
# Fix data
df = df[df["date"] >= 2001]
df = df[df["date"] <= 2021]
df["date"] = df["date"].astype("int")
df = df.sort_values(by=["date"])
df.loc[df["technique"]=="Mixed tech", "technique"] = "Mixed technique"
df_hist = read_df('data/historical_avg_price.csv')
df_hist = df_hist[df_hist["date"] >= 2001]
df_hist = df_hist.groupby("date").sum()

#temp fix
df.loc[df["technique"] == "Silk print", "category"] = "Graphics"
df.loc[df["technique"] == "Vitrography", "category"] = "Graphics"
df.loc[df["technique"] == "Wood cut", "category"] = "Graphics"

# Sidebar Table of Contents
toc = Toc()
toc.placeholder(sidebar=True)

kanvas_logo = get_img_with_href('data/horisontal-BLACK.png', 'https://kanvas.ai', '200px')
st.sidebar.markdown(kanvas_logo, unsafe_allow_html=True)

kanvas_logo = get_img_with_href('data/horisontal-BLACK.png', 'https://kanvas.ai', '400px')
st.markdown(kanvas_logo, unsafe_allow_html=True)

# TITLE
st.title('Estonian Art Index')
toc.header('Overview')
create_paragraph('''Kanvas.ai Art Index is a tool for art investors.

Kanvas.ai's art index is a database created based on Estonian art auction sales \nhistory of the last 20 years (2001-2021), with an aim of making art and investing \nin art easier to understand for anyone interested.

The data has been collected based on the results of the public auctions of the \nmain galleries in Estonia, which provides an overview of how the art market \nbehaves over time and which art mediums and authors have the best investment \nperformance.

Based on the data, it is clear how the popularity of art has taken a big leap in \nrecent years, both in terms of prices and volume. For example, for many types of \nart work, the price increase or performance has been over 10% a year. Hence, a \nwell-chosen piece of art is a good choice to protect your money against inflation.

Kanvas.ai's Art Index currently does not include non-auction art information, but \nwe have a plan to start collecting data on NFT art media sold on the NFTKanvas.ai \npage as well.

The Art Index methodology is currently under development. Please email us info@kanvas.ai with any suggestions and comments.
''')


# FIGURE - date and average price
toc.subheader('Figure - Historical Price Performance')
fig = px.area(df_hist, x=df_hist.index, y="avg_price",
              labels={
                 "avg_price": "Historical Index Performance (€)",
                 "date": "Auction Year",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''The Art Index gives an overview of the rise and fall in the price of art. The price of art has made a noticeable jump in recent years. Interest in investing in art on the art auction market has skyrocketed since the pandemic.''')

# TABLE - categories average price
toc.subheader('Table - Historical Price Performance by Technique')
table_data = create_table(df, "category", df["category"].unique(), calculate_volume=False, table_height=150)
st.table(table_data)
create_paragraph('''Ranked by medium, or technique, according to which medium dominates the highest-selling works.''')

# Art Index Performance Prediction
toc.subheader('Art Index Performance Prediction')
df_art = pd.read_csv('./data/historical_avg_price.csv')
df_art[['ds', 'y']] = df_art[['date', 'avg_price']]
df_art = df_art[['ds', 'y']]
m = Prophet()
m.fit(df_art)
future = m.make_future_dataframe(periods = 20428)
forecast = m.predict(future.tail(1770))
m.plot(forecast)
fig1 = plot_plotly(m, forecast) 
st.plotly_chart(fig1) 
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
st.plotly_chart(fig, use_container_width=True)

create_paragraph('''According to these analysis, it is predicted that the art index price will experience a significant rise, increasing from 4,671.681 in February 2021 to 5,469.599 by December 2025.
''')
# FIGURE - date and volume
toc.subheader('Figure - Historical Volume Growth')
fig = px.area(df_hist, x=df_hist.index, y="volume", 
             labels={
                 "volume": "Volume (€)",
                 "date": "Auction Year",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''The increase in volume gives us an overview of how much the turnover of auctions has risen and fallen over time.

For example, in 2001 the auction turnover was around 174,000 euros, then in 2021 the auction turnover was 4.5 million. Certainly, the replacement of the kroon with the euro plays a very important role, and more auction galleries have been added. Still, art sales have seen a significant jump since 2019, the biggest in 20 years. The last major change occurred due to the effects of the 2006-2009 economic crisis.
''')

# TABLE - categories volume
toc.subheader('Table - Historical Volume Growth by Technique')
table_data = create_table(df, "category", df["category"].unique(), calculate_volume=True, table_height=150)
st.table(table_data)
create_paragraph('''From this table, we can see which medium has had the highest turnover. Based on the given data, we can see, for example, that graphics are the most popular and with the highest annual turnover increase percentage (204% annually over 20 years and 35% for oil painting at the same time).''')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Figure - Art Sales by Technique and Artist (Start and End Price Difference)')

df['start_price'] = df['start_price'].fillna(df['end_price'])
df['overbid_%'] = (df['end_price'] - df['start_price'])/df['start_price'] * 100
df['art_work_age'] = df['date'] - df['year']
df2 = df.groupby(['author', 'technique', 'category']).agg({'end_price':['sum'], 'overbid_%':['mean']})
df2.columns = ['total_sales', 'overbid_%']
df2 = df2.reset_index()

df2.loc[df2["category"] == "Mixed medium", "technique"] = df2["author"]
df2.loc[df2["category"] == "Mixed medium", "author"] = None
df2.loc[df2["category"] == "Drawing", "technique"] = df2["author"]
df2.loc[df2["category"] == "Drawing", "author"] = None

artists = df2["author"].unique()
artists = [artist for artist in artists if artist is not None]
artists = np.concatenate([["All artists"], artists])
selected_artist =st.selectbox('Select an Artist', options=artists, key="1")
if selected_artist=='All artists':

    fig = px.treemap(df2, path=[px.Constant("Techniques"), 'category', 'technique', 'author'], values='total_sales',
                      color='overbid_%',
                      color_continuous_scale='RdBu',
                      range_color = (0, df['overbid_%'].mean() + df['overbid_%'].std() / 2),
                      labels={
                         "overbid_%": "Overbid (%)",
                         "total_sales": "Total Sales",
                         "author": "Author",
                      })
else:    
    artist_df = df2[df2["author"] == selected_artist]
    fig = px.treemap(artist_df, path=["author", "category", "technique"], values="total_sales",
                    color="overbid_%", color_continuous_scale="RdBu",
                    range_color=(-20, 100), labels={
                        "yearly_performance": "Historical Performance (%)",
                        "total_sales": "Total Sales",
                        "author": "Author",
                    })

fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
fig.update_traces(hovertemplate='<b>%{label} </b> <br> Total Sales: %{value}<br> Overbid (%): %{color:.2f}',)
st.plotly_chart(fig, use_container_width=True)

if selected_artist!='All artists':
    artist_df = df2[df2["author"] == selected_artist]
    columns = ["author", "category", "technique", "total_sales", "overbid_%"]
    data = artist_df[columns]

    data = data.rename(columns={
        "author":"Artist",
        "category":"Category",
        "technique":"Technique",
        "total_sales": "Total Sales",
        "overbid_%": "Overbid %",
    })
    data = data.reset_index(drop=True)
    st.write(data)


create_paragraph('''Techniques and artists, where the color scale gives us an overview, how much art has been overbid during auctions ,and volume ranked by Technique and artist.

For example, the blue color shows artists and mediums, which had the highest overbidding percentage. Volume is also shown next to the artist’s name. For example, Konrad Mägi has the highest art piece sold, but this table shows that the highest overbidding goes to the works of Olev Subbi, in regards to the tempera medium. (711.69 % price increase from the starting price, while the numbers for Konrad Mägi are 59.06 % for oil on cardboard and 85.44% for oil on canvas medium). Although Konrad Mägi still has the edge over Subbi in terms of volume.
''')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Figure - Art Sales by Technique and Artist (Historical Price Performance)')
table_data = create_table(df, "author", list(df["author"].unique()), calculate_volume=False, table_height=250)
df["yearly_performance"] = [table_data[table_data["Author"] == x]["Yearly growth (%)"] for x in df["author"]]
df2 = df.groupby(['author', 'technique', 'category']).agg({'end_price':['sum'], 'yearly_performance':['mean']})
df2.columns = ['total_sales', 'yearly_performance']
df2 = df2.reset_index()

df2.loc[df2["category"] == "Mixed medium", "technique"] = df2["author"]
df2.loc[df2["category"] == "Mixed medium", "author"] = None

df2.loc[df2["category"] == "Drawing", "technique"] = df2["author"]
df2.loc[df2["category"] == "Drawing", "author"] = None

artists = df2["author"].unique()
artists = [artist for artist in artists if artist is not None]
artists = np.concatenate([["All artists"], artists])

selected_artist2 =st.selectbox('Select an author', options=artists, key="2")
if selected_artist2=='All artists':

    fig = px.treemap(df2, path=[px.Constant("Techniques"), 'category', 'technique', 'author'], values='total_sales',
                      color='yearly_performance',
                      color_continuous_scale='RdBu',
                      range_color = (-20, 100),
                      labels={
                         "yearly_performance": "Historical Performance (%)",
                         "total_sales": "Total Sales",
                         "author": "Author",
                      })
else:    
    artist_df = df2[df2["author"] == selected_artist2]

    fig = px.treemap(artist_df, path=[px.Constant("Techniques"), 'category', 'technique', 'author'], values='total_sales',
                        color='yearly_performance',
                        color_continuous_scale='RdBu',
                        range_color = (-20, 100),
                        labels={
                            "yearly_performance": "Historical Performance (%)",
                            "total_sales": "Total Sales",
                            "author": "Author",
                        })


fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
fig.update_traces(hovertemplate='<b>%{label} </b> <br> Total sales: %{value}<br> Annual return (%): %{color:.2f}',)
st.plotly_chart(fig, use_container_width=True)

if selected_artist2!='All artists':

    artist_df = df2[df2["author"] == selected_artist2]
    columns = ["category", "technique", "author", "total_sales", "yearly_performance"]
    data = artist_df[columns]

    data = data.rename(columns={
        "author":"Artist",
        "category":"Category",
        "technique":"Technique",
        "total_sales": "Total Sales",
        "yearly_performance": "Historical Performance (%)",
    })
    data = data.reset_index(drop=True)
    st.write(data)


create_paragraph('''
Techniques and artists, where the color scale gives us an overview of historical price performance and volume ranked by Technique and artist.

For example, the blue color shows artists and mediums, which had the highest historical price growth. Volume is also shown next to the artist’s name. For example, Konrad Mägi has the highest art piece sold, but this table shows that the highest average historical price goes to the works of Karin Luts (498.84 % price increase average over the years, while the number for Konrad Mägi is 198.95 %). Although Konrad Mägi still has the edge over Luts in terms of volume.
''')

# TABLE - best authors average price
author_sum = df.groupby(["author"], sort=False)["end_price"].sum()
top_authors = author_sum.sort_values(ascending=False)[:10]

toc.subheader('Table - Top 10 Best Performing Artists (Price Perfomance)')
table_data = create_table(df, "author", top_authors.index, calculate_volume=False, table_height=250)    
st.table(table_data)
create_paragraph('''This table shows the most popular artists and their historical price growth percentage. The percentage is calculated based on annual average end price differences.

Leading this table is Konrad Mägi, whose growth percentage is on average 198.95%. This growth percentage is definitely affected by the uniqueness of his works. Konrad Mägi has a limited number of works displayed at auctions. In second place we find Eduard Wiiralt, who in contrast to Konrad Mägi has a lot of his works displayed at auctions. The starting prices of Wiiralt’s works are low and he is very popular amongst collectors.
''')

# TABLE - best authors volume
toc.subheader('Table - Top 10 Best Performing Artist (Volume Growth)')
table_data = create_table(df, "author", top_authors.index, calculate_volume=True, table_height=250)    
st.table(table_data)
create_paragraph('''This table shows the turnover and average annual growth of art works. Here Wiiralt is positioned at 8th place and Konrad Mägi at 1st. Because the growth percentage is during the whole period (2001-2021) turnover, then the artists, who have the most works bought, are situated at the top of the table.
''')

# FIGURE - date and price
toc.subheader('Figure - Age of Art Work vs Price')
df['art_work_age'] = df['date'] - df['year']
q_low = df["end_price"].quantile(0.1)
q_hi  = df["end_price"].quantile(0.9)
df = df[(df["end_price"] < q_hi) & (df["end_price"] > q_low)]
fig = px.scatter(df.dropna(subset=["decade"]), x="art_work_age", y="end_price", color="category",
                 animation_frame="date", animation_group="technique", hover_name="technique",
                 size='date', hover_data=['author'], size_max=15, range_x=[-4,130], range_y=[-1000,8200],
                 labels={
                     "end_price": "Auction Final Sales Price (€)",
                     "art_work_age": "Art Work Age",
                     "author": "Author",
                     "category": "Technique",
                     "decade": "Decade"
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''From the given graph, it is possible to determine the price of the work according to the age and technique of the work of art. Techniques are separated by color.

The oldest work dates back to 1900, but is not the most expensive. In general, it can be seen that older works are more expensive, with the exception of Olev Subbi. It can be seen that pre-World War II works from 1910-1940 have been sold higher.
''')

# FIGURE - size and price
toc.subheader('Figure - Size of Art Work vs Price')
df["dimension"] = df["dimension"] / (100*100)
q_low = df["dimension"].quantile(0.1)
q_hi  = df["dimension"].quantile(0.9)
df = df[(df["dimension"] < q_hi) & (df["dimension"] > q_low)]
fig = px.scatter(df.dropna(subset=["dimension"]), x="dimension", y="end_price", color="category",
                 animation_frame="date", animation_group="technique", hover_name="technique",
                 size='date', hover_data=['author'], size_max=15, range_x=[-0.03, 4], range_y=[-1000,8200],
                 labels={
                     "end_price": "Auction Final Sales Price (€)",
                     "dimension": "Dimension (m²)",
                     "author": "Author",
                     "category": "Technique",
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''An overview of the relationship between the dimensions, technique and price of the work. Many smaller format works are often more expensive than large ones. The size of the piece does not necessarily mean that it is more expensive. Rather, the author is more important, and then the size of the work. For example, Konrad Mägi's Õlimaa is among the averages on the measurement chart, but considerably higher than the others on the price scale (127,823 euros hammer price), while the hammer price of the largest work (Toomas Vint) is €7,094.
''')

def create_credits(text):
    st.markdown('<span style="word-wrap:break-word;font-family:Source Code Pro;font-size: 14px;">' + text + '</span>', unsafe_allow_html=True)
create_credits('''Copyright: Kanvas.ai''')
create_credits('''Authors: Astrid Laupmaa, Julian Kaljuvee, Markus Sulg''')
create_credits('''Source: Estonian public art auction sales (2001-2021)''')
create_credits('''Other credits: Inspired by the original Estonian Art Index created by Riivo Anton; <br>Generous support from <a href="https://tezos.foundation/">Tezos Foundation</a>''')

toc.generate()

@st.cache
def convert_df():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return read_df('data/auctions_clean.csv').to_csv().encode('utf-8')

csv = convert_df()
st.download_button(label="Download data",data=csv, file_name='estonian_art_index.csv', mime='text/csv')