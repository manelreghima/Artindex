import streamlit as st
import plotly.express as px
import pandas as pd
from StreamlitHelper import Toc, get_img_with_href, read_df, create_table

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
    
# Sidebar Table of Contents
toc = Toc()
toc.placeholder(sidebar=True)

df = pd.read_csv('data/europe2.csv')
df = df[df["auction_year"] >= 2002]
df = df.drop("Unnamed: 0", axis=1)
df = df[df["dimension"]>0]
df = df.dropna(subset=["currency"])
df['date'] = df["auction_year"]
df = df.sort_values(by=["date"])
top_10_categories = list(df['technique'].value_counts().nlargest(11).index)
top_10_categories.remove("Unknown")

kanvas_logo = get_img_with_href('data/horisontal-BLACK.png', 'https://kanvas.ai', '200px')
st.sidebar.markdown(kanvas_logo, unsafe_allow_html=True)

kanvas_logo = get_img_with_href('data/horisontal-BLACK.png', 'https://kanvas.ai', '400px')
st.markdown(kanvas_logo, unsafe_allow_html=True)

# TITLE
st.title('Euroopa kunsti indeks')
toc.header('Ülevaade')
create_paragraph('''Kanvas.ai kunsti indeks on tööriist kunsti investeerijale.

Kanvas.ai kunsti indeks viimase 19 aasta (2002 kuni 2021) Eesti kunstioksjonite \nmüükide põhjal loodud andmebaas, eesmärgiga muuta kunst ja kunsti investeerimine \nlihtsamini mõistetavaks igale huvilisele.

Andmed on kogutud Euroopa põhiliste galeriide avalike oksjoni tulemuste põhjal, mis \nannab ülevaate kuidas käitub kunstiturg ajas ning millised kunstimeediumid ning \nautorid on kõige parema investeerimise tootlikkusega.

Kanvas.ai kunstiindeksist puuduvad oksjoniväline kunsti info kuid meil on plaan \nhakata koguma ka NFTKanvas.ai lehel müüdud NFT kunstimeediumi andmeid.

Kunstiindeksi metoodika on praegu väljatöötamisel. Soovituste ja kommentaaridega saatke meile e-kiri info@kanvas.ai.
''')

prices = []
volumes = []
dates = []
for year in range(df["date"].min(), df["date"].max()):
    dates.append(year)
    prices.append(df[df["date"] == year]["end_price"].mean())
    volumes.append(df[df["date"] == year]["end_price"].sum())
data = {'avg_price': prices, 'volume': volumes, 'date': dates}
df_hist = pd.DataFrame.from_dict(data)

# FIGURE - date and average price
toc.subheader('Joonis - Ajalooline hinnanäitaja')
fig = px.area(df_hist, x="date", y="avg_price",
              labels={
                 "avg_price": "Ajalooline indeksinäitaja (€)",
                 "date": "Oksjoni aasta",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('Tekst')

# TABLE - categories average price
toc.subheader('Tabel - Ajalooline hinnanäitaja kategooriate kaupa')
df["category"] = df["technique"]
table_data = create_table(df, category_column="category", category_list=top_10_categories, calculate_volume=False, table_height=150)
st.table(table_data)
create_paragraph('Meediumite ehk tehnika järgi järjestud vastavalt sellele, missugused meediumid domineerivad kõige kallimalt müüdud teoste hulgas.')

# FIGURE - date and volume
toc.subheader('Joonis - Ajalooline volüümi kasv')
fig = px.area(df_hist, x="date", y="volume", 
             labels={
                 "volume": "Volüüm (€)",
                 "date": "Oksjoni aasta",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Tekst
''')

# TABLE - categories volume
toc.subheader('Tabel - Ajalooline volüümi kasv kategooriate kaupa')
table_data = create_table(df, category_column="category", category_list=top_10_categories, calculate_volume=True, table_height=150)
st.table(table_data)
create_paragraph('Sellest tabelist näeme, milline meedium on olnud kõige suurema käibega. Antud andmete põhjal võime näiteks näha, et graafika on kõige populaarsem ning kõige suurema käibe tõusu protsendiga.(Keskmiselt 204% 20 aasta jooksul ja õlimaalil samal ajal 35%)')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Joonis - Kunsti müügid kategooria ja kunstniku järgi')

df['start_price'] = df['start_price'].fillna(df['end_price'])
df['overbid_%'] = (df['end_price'] - df['start_price'])/df['start_price'] * 100
#df['art_work_age'] = df['date'] - df['year']
df2 = df[df["technique"].isin(top_10_categories)]
df2 = df2.groupby(['author', 'technique']).agg({'end_price':['sum'], 'overbid_%':['mean']})
df2.columns = ['total_sales', 'overbid_%']
df2 = df2.dropna(subset="overbid_%")
df2 = df2[df2["total_sales"] > 0]
#df2 = df2.sort_values("total_sales", ascending=False)
df2 = df2.reset_index()

top_10_cat_indexes = []
for cat in top_10_categories:
    indexes = df2.loc[df2["technique"]==cat, "total_sales"].nlargest(10).index
    top_10_cat_indexes.extend(list(indexes))
df2 = df2[df2.index.isin(top_10_cat_indexes)]

@st.cache_data(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def create_treemap():
    return px.treemap(df2, path=[px.Constant("Techniques"), 'technique', 'author'], values='total_sales',
                      color='overbid_%',
                      color_continuous_scale='RdBu',
                      range_color = (0, df['overbid_%'].mean() + df['overbid_%'].std()),
                      labels={
                         "overbid_%": "Ülepakkumine (%)",
                         "total_sales": "Kogumüük",
                         "author": "Autor",
                      })
fig = create_treemap()
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
fig.update_traces(hovertemplate='<b>%{label} </b> <br> Kogumüük: %{value}<br> Ülepakkumine (%): %{color:.2f}',)
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Tekst
''')

# TABLE - best authors average price
author_sum = df.groupby(["author"], sort=False)["end_price"].sum()
top_authors = []
for author in author_sum.sort_values(ascending=False).index:
    if df[df["author"] == author]["date"].nunique() > 1:
        top_authors.append(author)
        if len(top_authors) >= 10:
            break

toc.subheader('Tabel - Top 10 parimat kunstnikku')
table_data = create_table(df, category_column="author", category_list=top_authors, calculate_volume=False, table_height=250)    
st.table(table_data)
create_paragraph('''Tekst
''')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Joonis - Kunsti müügid kategooria ja kunstniku järgi')

df2 = df[df["technique"].isin(top_10_categories)]
df2 = df2[df["author"].isin(top_authors)]
table_data = create_table(df2, category_column="author", category_list=top_authors, calculate_volume=False, table_height=250)
df2["yearly_performance"] = [table_data[table_data["Kategooria"] == x]["Iga-aastane kasv (%)"] for x in df2["author"]]

df2 = df2.groupby(['author', 'technique']).agg({'end_price':['sum'], 'yearly_performance':['mean']})
df2.columns = ['total_sales', 'yearly_performance']
df2 = df2.reset_index()

fig = px.treemap(df2, path=[px.Constant("Techniques"), 'technique', 'author'], values='total_sales',
                  color='yearly_performance',
                  color_continuous_scale='RdBu',
                  range_color = (-20, 100),
                  labels={
                     "yearly_performance": "Aasta tootlus",
                     "total_sales": "Kogumüük",
                     "author": "Autor",
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
fig.update_traces(hovertemplate='<b>%{label} </b> <br> Kogumüük: %{value}<br> Aasta tootlus (%): %{color:.2f}',)
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''...
''')

# TABLE - best authors volume
toc.subheader('Tabel - Volüümi kasv Top 10 kunstnikul')
table_data = create_table(df, category_column="author", category_list=top_authors, calculate_volume=True, table_height=250)    
st.table(table_data)
create_paragraph('''Tekst
''')

# FIGURE - size and price
toc.subheader('Figure - Size of Art Work vs Price')
df["dimension"] = df["dimension"] / (100*100)
df3 = df[df["technique"].isin(top_10_categories)]
#df3 = df3.sort_values("dimension", ascending=False)
df3 = df3[df3["dimension"]>0.01]
#df4 = df3.groupby(['date', 'technique']).agg({'end_price':['sum'], 'overbid_%':['mean']})
#df3 = df3[:10000]
fig = px.scatter(df3.dropna(subset=["dimension"]), x="dimension", y="end_price", color="technique",
                 animation_frame="date", animation_group="technique", hover_name="technique",
                 size='date', hover_data=['author'], range_x=[-0.1,1.5], range_y=[-20000,150000],
                 labels={
                     "end_price": "Auction Final Sales Price (€)",
                     "dimension": "Dimension (m²)",
                     "author": "Author",
                     "technique": "Category",
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Tekst''')

def create_credits(text):
    st.markdown('<span style="word-wrap:break-word;font-family:Source Code Pro;font-size: 14px;">' + text + '</span>', unsafe_allow_html=True)
create_credits('''Copyright: Kanvas.ai''')
create_credits('''Autorid: Astrid Laupmaa, Julian Kaljuvee, Markus Sulg''')
create_credits('''Allikad: Eesti avalikud kunsti oksjonid (2001-2021)''')
create_credits('''Muu: Inspireeritud Riivo Antoni loodud kunstiindeksist; <br>Heldet toetust pakkus <a href="https://tezos.foundation/">Tezos Foundation</a>''')
toc.generate()

@st.cache_data
def convert_df():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return read_df('data/europe2.csv').to_csv().encode('utf-8')

csv = convert_df()
st.download_button(label="Laadi alla andmed",data=csv, file_name='europe_art_index.csv', mime='text/csv')