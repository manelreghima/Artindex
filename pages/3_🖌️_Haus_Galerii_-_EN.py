import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
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
    
def create_credits(text):
    st.markdown('<span style="word-wrap:break-word;font-family:Source Code Pro;font-size: 14px;">' + text + '</span>', unsafe_allow_html=True)
# Sidebar Table of Contents
toc = Toc()
toc.placeholder(sidebar=True)

df = read_df('data/haus_cleaned.csv')
#df = df[df["date"] >= 2001]
df = df[df["date"] <= 2023]
df["technique"] = df["technique"].str.capitalize() 

df["category_parent"] = "Eritehnika"
df.loc[df["category"] == "Õlimaal", "category_parent"] = "Maal"
df.loc[df["category"] == "Muu maalitehnika", "category_parent"] = "Maal"

df.loc[df["category"] == "Kõrgtrükk", "category_parent"] = "Graafika"
df.loc[df["category"] == "Sügavtrükk", "category_parent"] = "Graafika"
df.loc[df["category"] == "Lametrükk", "category_parent"] = "Graafika"
df.loc[df["category"] == "Digitrükk", "category_parent"] = "Graafika"

df.loc[df["category"] == "Joonistustehnika", "category_parent"] = "Joonistus"

df.loc[df["technique"] == "Segatehnika", "category_parent"] = "Segatehnika"
df.loc[df["technique"]=="Segatehnika", "category"] = "Segatehnika" 

#temp fix
df.loc[df["technique"] == "Õli puit", "category"] = "Õlimaal"
df.loc[df["technique"] == "Õli puit", "category_parent"] = "Maal"

def change_value(change_from, change_to, column):
    df.loc[df[column]==change_from, column] = change_to
# Estonian categories and techniques
change_value("Maal", "Painting", "category_parent")
change_value("Graafika", "Graphics", "category_parent")
change_value("Segatehnika", "Mixed medium", "category_parent")
change_value("Joonistus", "Drawing", "category_parent")
change_value("Eritehnika", "Special", "category_parent")

def change_value(change_to, change_from, column):
    df.loc[df[column]==change_from, column] = change_to

change_value("Oil painting", "Õlimaal", "category")
change_value("Other (non-oil) paintings", "Teised (mitte õli) maalid", "category")
change_value("Mixed medium", "Segatehnika", "category")
change_value("Graphics", "Graafika", "category")
change_value("Drawing", "Joonistustehnika", "category")
change_value("Intaglio print", "Sügavtrükk", "category")
change_value("Planographic print", "Lametrükk", "category")
change_value("Relief print", "Kõrgtrükk", "category")

change_value("Oil on canvas", "Õli lõuend", "technique")
change_value("Oil on cardboard", "Õli papp", "technique")
change_value("Oil on plywood", "Õli vineer", "technique")
change_value("Oil on masonite", "Õli masoniit", "technique")
change_value("Oil on paper", "Õli paber", "technique")
change_value("Oil", "Õli", "technique")
change_value("Oil on wood", "Õli puit", "technique")

change_value("Watercolor", "Akvarell", "technique")
change_value("Pastel", "Pastell", "technique")
change_value("Acrylic", "Akrüül", "technique")
change_value("Gouache", "Guašš", "technique")

change_value("Drypoint", "Kuivnõel", "technique")
change_value("Aquatint", "Akvatinta", "technique")
change_value("Mezzotinto", "Metsotinto", "technique")
change_value("Linoleum intaglio", "Linoolsügavtrükk", "technique")
change_value("Etching", "Söövitus", "technique")
change_value("Copper engraving", "Vasegravüür ", "technique")
change_value("Intaglio print", "Sügavtrükk", "technique")
change_value("Vitrography", "Vitrograafia", "technique")
change_value("Aquatint", "Reservaaž ", "technique")

change_value("Lithography", "Litograafia", "technique")
change_value("Silk print", "Siiditrükk", "technique")
change_value("Monotype", "Monotüüpia", "technique")
change_value("Diatype", "Diatüüpia", "technique")
change_value("Planographic print", "Lametrükk", "technique")
change_value("Soft-ground etching", "Pehmelakk", "technique")

change_value("Wood engraving", "Puugravüür", "technique")
change_value("Plywood cut", "Vineerilõige", "technique")
change_value("Linocut", "Linool", "technique")
change_value("Relief print", "Kõrgtrükk", "technique")
change_value("Plastic cut", "Plastikaatlõige", "technique")

change_value("Drawing", "Joonistus", "technique")
change_value("Ink", "Tint", "technique")
change_value("Ink", "Tušš", "technique")
change_value("Crayon", "Kriit", "technique")
change_value("Pencil", "Pliiats", "technique")
change_value("Charcoal", "Süsi", "technique")
change_value("Graphite", "Grafiit", "technique")
change_value("Sanguine", "Sangviin", "technique")

change_value("Collage", "Kollaaž", "technique")
change_value("Author's technique", "Autoritehnika", "technique")
change_value("Bronze", "Pronks ", "technique")
change_value("Wood", "Puit", "technique")


order_categories = ["Painting", "Graphics", "Drawing", "Mixed medium", "Special"]
df["cat_sort"] = [order_categories.index(x) for x in df["category_parent"]]
df = df.sort_values(by=["date", "cat_sort"])
df = df.dropna(subset=["author"])

kanvas_logo = get_img_with_href('data/horisontal-BLACK.png', 'https://kanvas.ai', '200px')
st.sidebar.markdown(kanvas_logo, unsafe_allow_html=True)

kanvas_logo = get_img_with_href('data/haus_logo.png', 'https://haus.ee', '200px')
st.markdown(kanvas_logo, unsafe_allow_html=True)

# TITLE
st.title('Haus Gallery Art Index')
toc.header('Overview')
create_paragraph('''This art index, based on the logic of economic analysis and graphically implemented, has been compiled based on the sales results of Haus Gallery's 25 years of art auction.

The index provides an overview of how the art market, actively developed by Haus Gallery, has behaved over time and which authors and art techniques have had the best investment growth during this period.

The purpose of the index is to be a helpful tool for the art buyer, who considers the value of art price growth in addition to the emotional value.
''')

create_credits("The index is created by Kanvas.ai. The art index methodology is being improved and further developed. All suggestions and comments are welcome at info@kanvas.ai")

# TABLE - Koik top 20
toc.subheader('Table - Top 20 of All Time')
pd.options.display.float_format = '{:}'.format
df_top_20 = pd.read_csv('data/haus_koik_top_20-eng.csv')
df_top_20.index += 1
df_styled = df_top_20.style.format(formatter="{:}")
st.dataframe(df_styled)

# TABLE - Vanem TOP 50
toc.subheader('Table - Top 50 Classics of Earlier Art (Last 10 Years)')
pd.options.display.float_format = '{:}'.format
df_top_50 = pd.read_csv('data/haus_vana_top_50-eng.csv')
df_top_50.index += 1
df_styled = df_top_50.style.format(formatter="{:}")
st.dataframe(df_styled)

# TABLE - Moodne TOP 50
toc.subheader('Table - Top 50 Classics of Modern Art (Last 10 Years)')
pd.options.display.float_format = '{:}'.format
df_top_50 = pd.read_csv('data/haus_moodne_top_50-eng.csv')
df_top_50.index += 1
df_styled = df_top_50.style.format(formatter="{:}")
st.dataframe(df_styled)

# TABLE - Graafika TOP 20
toc.subheader('Table - Graphics Top 20 (Last 10 Years)')
pd.options.display.float_format = '{:}'.format
df_top_20 = pd.read_csv('data/haus_graafika_top_20-eng.csv')
df_top_20.index += 1
df_styled = df_top_20.style.format(formatter="{:}")
st.dataframe(df_styled)

prices = []
volumes = []
dates = []
for year in range(df["date"].min(), df["date"].max()+1):
    dates.append(year)
    prices.append(df[df["date"] == year]["end_price"].mean())
    volumes.append(df[df["date"] == year]["end_price"].sum())
data = {'avg_price': prices, 'volume': volumes, 'date': dates}
df_hist = pd.DataFrame.from_dict(data)

# FIGURE - date and average price
toc.subheader('Figure - Historical Price Performances')
fig = px.area(df_hist, x="date", y="avg_price",
              labels={
                 "avg_price": "Historical Index Performance (€)",
                 "date": "Auction Year",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
# unfinished trendlines
fig2 = px.scatter(df_hist, x="date", y="avg_price", trendline="ols")
fig2.data = [t for t in fig2.data if t.mode == "lines"]
#fig = go.Figure(data= fig.data + fig2.data)

st.plotly_chart(fig, use_container_width=True)
create_paragraph('''
This figure shows the variation in the price of an average artwork over the years.
''')

# TABLE - categories average price
toc.subheader('Table - Historical Price Performance by Technique')
table_data = create_table(df.dropna(subset=["date"]), "category_parent", order_categories[:-1], calculate_volume=False, table_height=150)
st.table(table_data)
create_paragraph('Ranked by medium, or technique, according to which medium dominates the highest-selling works.')

# FIGURE - date and volume
toc.subheader('Joonis - Historical Volume Growth')
fig = px.area(df_hist, x="date", y="volume", 
             labels={
                 "volume": "Volume (€)",
                 "date": "Auction Year",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
# unfinished trendlines
fig2 = px.scatter(df_hist, x="date", y="volume", trendline="ols")
fig2.data = [t for t in fig2.data if t.mode == "lines"]
#fig = go.Figure(data= fig.data + fig2.data)

st.plotly_chart(fig, use_container_width=True)
create_paragraph('''
This figure shows the variation in the volume of artwork over the years.
''')

# TABLE - categories volume
toc.subheader('Table - Historical Volume Growth by Technique')
table_data = create_table(df.dropna(subset=["date"]), "category_parent", order_categories[:-1], calculate_volume=True, table_height=150)
st.table(table_data)
create_paragraph('This table shows the variation in the volume of more general techniques over a range of years.')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Figure - Art Sales by Technique and Artist (Start and End Price Difference)')

df['start_price'] = df['start_price'].fillna(df['end_price'])
@st.cache(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def create_treemap_overbid():
    df['overbid_%'] = (df['end_price'] - df['start_price'])/df['start_price'] * 100
    df2 = df[df["technique"] != " "]
    df2.loc[df2["category"] == "Muu maalitehnika", "category"] = df2["technique"]

    df2 = df2.groupby(['author', 'technique', 'category', 'category_parent']).agg({'end_price':['sum'], 'overbid_%':['mean']})
    df2.columns = ['total_sales', 'overbid_%']
    df2 = df2.reset_index()

    # fix treemap parenting
    df2.loc[df2["category"] == "Muu maalitehnika", "category"] = df2["technique"]
    df2.loc[df2["technique"] == "Tempera", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Tempera", "author"] = None

    df2.loc[df2["technique"] == "Watercolor", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Watercolor", "author"] = None

    df2.loc[df2["technique"] == "Pastel", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Pastel", "author"] = None

    df2.loc[df2["technique"] == "Acrylic", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Acrylic", "author"] = None

    df2.loc[df2["technique"] == "Gouache", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Gouache", "author"] = None

    df2.loc[df2["category"] == "Drawing", "category"] = df2["technique"]
    df2.loc[df2["category_parent"] == "Drawing", "technique"] = df2["author"]
    df2.loc[df2["category_parent"] == "Drawing", "author"] = None

    df2.loc[df2["category"] == "Muu", "category"] = df2["technique"]
    df2.loc[df2["category_parent"] == "Special", "technique"] = df2["author"]
    df2.loc[df2["category_parent"] == "Special", "author"] = None

    df2.loc[df2["category"] == "Mixed medium", "category"] = df2["author"]
    df2.loc[df2["category_parent"] == "Mixed medium", "technique"] = None
    df2.loc[df2["category_parent"] == "Mixed medium", "author"] = None

    fig = px.treemap(df2, path=[px.Constant("Techniques"), 'category_parent', 'category', 'technique', 'author'], values='total_sales',
                      color='overbid_%',
                      color_continuous_scale='RdBu',
                      range_color = (0, df['overbid_%'].mean() + df['overbid_%'].std()),
                      labels={
                         "overbid_%": "Overbid (%)",
                         "total_sales": "Total Sales",
                         "author": "Author",
                      })
    return fig
fig = create_treemap_overbid()
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
fig.update_traces(hovertemplate='<b>%{label} </b> <br> Total Sales: %{value}<br> Overbid (%): %{color:.2f}',)
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''
This figure shows total sales revenue by author and technique in more detail, with general techniques broken down into sub-techniques. Overbidding is distinguished from the initial price by color.
''')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Figure - Art Sales by Technique and Artist (Historical Price Performance)')

@st.cache(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def create_treemap_yearly():
    table_data = create_table(df, "author", list(df["author"].unique()), calculate_volume=False, table_height=250)
    df["yearly_performance"] = [table_data[table_data["Author"] == x]["Yearly growth (%)"] for x in df["author"]]
    df2 = df.groupby(['author', 'technique', 'category', 'category_parent']).agg({'end_price':['sum'], 'yearly_performance':['mean']})
    df2.columns = ['total_sales', 'yearly_performance']
    df2 = df2.reset_index()

    # fix treemap parenting
    df2.loc[df2["category"] == "Muu maalitehnika", "category"] = df2["technique"]
    df2.loc[df2["technique"] == "Tempera", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Tempera", "author"] = None

    df2.loc[df2["technique"] == "Watercolor", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Watercolor", "author"] = None

    df2.loc[df2["technique"] == "Pastel", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Pastel", "author"] = None

    df2.loc[df2["technique"] == "Acrylic", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Acrylic", "author"] = None

    df2.loc[df2["technique"] == "Gouache", "technique"] = df2["author"]
    df2.loc[df2["category"] == "Gouache", "author"] = None

    df2.loc[df2["category"] == "Drawing", "category"] = df2["technique"]
    df2.loc[df2["category_parent"] == "Drawing", "technique"] = df2["author"]
    df2.loc[df2["category_parent"] == "Drawing", "author"] = None

    df2.loc[df2["category"] == "Muu", "category"] = df2["technique"]
    df2.loc[df2["category_parent"] == "Special", "technique"] = df2["author"]
    df2.loc[df2["category_parent"] == "Special", "author"] = None

    df2.loc[df2["category"] == "Mixed medium", "category"] = df2["author"]
    df2.loc[df2["category_parent"] == "Mixed medium", "technique"] = None
    df2.loc[df2["category_parent"] == "Mixed medium", "author"] = None

    fig = px.treemap(df2, path=[px.Constant("Techniques"), 'category_parent', 'category', 'technique', 'author'], values='total_sales',
                      color='yearly_performance',
                      color_continuous_scale='RdBu',
                      range_color = (-20, 100),
                      labels={
                         "yearly_performance": "Historical Performance (%)",
                         "total_sales": "Total Sales",
                         "author": "Author",
                      })
    return fig

fig = create_treemap_yearly()
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
fig.update_traces(hovertemplate='<b>%{label} </b> <br> Total Sales: %{value}<br> Historical Performance (%): %{color:.2f}',)
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''
This figure shows total sales revenue by author and technique in more detail, with general techniques broken down into sub-techniques. The annual returns of the works of art are distinguished by color.
''')

# TABLE - best authors average price
author_sum = df.groupby(["author"], sort=False)["end_price"].sum()
top_authors = author_sum.sort_values(ascending=False)[:25]

toc.subheader('Table - Top 25 Best Performing Artists (Price Performance)')
table_data = create_table(df, "author", top_authors.index, calculate_volume=False, table_height=250)    
st.table(table_data)
create_paragraph('''
This table shows the average annual price growth of the authors' works (starting with the author with the highest total revenue).
''')

# TABLE - best authors volume
toc.subheader('Table - Top 25 Best Performing Artist (Volume Growth)')
table_data = create_table(df, "author", top_authors.index, calculate_volume=True, table_height=250)    
st.table(table_data)
create_paragraph('''
This table shows (starting with the author with the highest total revenue) the annual growth of the total revenue of the authors' works.
''')

# FIGURE - date and price
toc.subheader('Figure - Age of Art Work vs Price')
df['art_work_age'] = df['date'] - df['year']

df2 = df[df["technique"] != " "]
df2 = df2[df["category_parent"] != "Special"]
# create overview for first view - TODO add to slider
df3 = df2.groupby(['category_parent']).agg({'end_price':['mean'], 'art_work_age':['mean']})
df3.columns = ['sales', 'age']
df3 = df3.reset_index()
df3["cat_sort"] = [order_categories.index(x) for x in df3["category_parent"]]
df3 = df3.sort_values(by=["cat_sort"])
fig_all = px.scatter(df3.dropna(subset=['age']), x="age", y="sales", color="category_parent",
                 size='sales', 
                 labels={
                     "sales": "Auction Final Sales Price (€)",
                     "age": "Art Work Age",
                     "category_parent": "Technique",
                     "decade": "Decade",
                     "date":"Year",
                  })

fig = px.scatter(df2.dropna(subset=["decade"]), x="art_work_age", y="end_price", color="category_parent",
                 animation_frame="date", animation_group="category_parent", hover_name="category_parent",
                 size='date', size_max=15, range_x=[-2,125], range_y=[-200,15000],
                 labels={
                     "end_price": "Auction Final Sales Price (€)",
                     "art_work_age": "Art Work Age",
                     "category_parent": "Technique",
                     "decade": "Decade",
                     "date":"Year",
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))

fig = go.Figure(data=fig_all.data, frames=fig['frames'], layout=fig.layout)

st.plotly_chart(fig, use_container_width=True)
create_paragraph('''
This figure shows the average price and age of artwork by technique. By starting the animation, you can see the comparison by years.
''')

# FIGURE - size and price
toc.subheader('Figure - Size of Art Work vs Price')
df["dimension"] = df["dimension"] / (100*100)
df2 = df[df["technique"] != " "]
df2 = df2[df["category_parent"] != "Special"]
df2 = df2.dropna(subset=["dimension"])
# create overview for first view - TODO add to slider
df3 = df2.groupby(['category_parent']).agg({'end_price':['mean'], 'dimension':['mean']})
df3.columns = ['sales', 'dim']
df3 = df3.reset_index()
df3["cat_sort"] = [order_categories.index(x) for x in df3["category_parent"]]
df3 = df3.sort_values(by=["cat_sort"])
df3["date"] = 1000
#df2.loc[df2.index < 100, "category_parent"] = "Joonistus"
#df2 = df2.sort_values(by=["date"], ascending=False)
fig_all = px.scatter(df3, x="dim", y="sales", color="category_parent",
                 size="sales",
                 labels={
                     "sales": "Auction Final Sales Price (€)",
                     "dim": "Dimension (m²)",
                     "category_parent": "Technique",
                     "date":"Year",
                  })

fig = px.scatter(df2, x="dimension", y="end_price", color="category_parent",
                 animation_frame="date", animation_group="category_parent", hover_name="category_parent",
                 size='date', size_max=15, range_x=[-2,36], range_y=[-200,15000],
                 labels={
                     "end_price": "Auction Final Sales Price (€)",
                     "dimension": "Dimension (m²)",
                     "category_parent": "Technique",
                     "date":"Year",
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
frames= []
fig = go.Figure(data=fig_all.data, frames=fig['frames'], layout=fig.layout)
#fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 0
#fig.layout.updatemenus = [fig.layout.updatemenus[0]] + list(fig.layout.updatemenus)
#fig.data = fig.frames[0].data

st.plotly_chart(fig, use_container_width=True)
create_paragraph('''
This figure shows the average price and size of artwork by technique. By starting the animation, you can see the comparison by years.
''')

create_credits('''Copyright: Kanvas.ai''')
create_credits('''Authors: Astrid Laupmaa, Julian Kaljuvee, Markus Sulg''')
create_credits('''Source: Haus art auctions (1997-2022)''')
create_credits('''Other credits: Inspired by the original Estonian Art Index created by Riivo Anton; <br>Generous support from <a href="https://tezos.foundation/">Tezos Foundation</a>''')
toc.generate()

@st.cache
def convert_df():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return read_df('data/haus_cleaned.csv').to_csv().encode('utf-8')

csv = convert_df()
st.download_button(label="Download data",data=csv, file_name='haus_kunsti_indeks.csv', mime='text/csv')
