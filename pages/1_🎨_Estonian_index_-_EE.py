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
st.title('Eesti kunstiindeks')
toc.header('Ülevaade')
create_paragraph('''Kanvas.ai Art Index on vahend kunstiinvestoritele.

Kanvas.ai kunstiindeks on andmebaas, mis on loodud Eesti kunstioksjonite \n viimase 20 aasta (2001-2021) müügiajaloo põhjal, eesmärgiga muuta kunst ja kunsti investeerimine \n kõigile huvilistele arusaadavamaks.

Andmed on kogutud Eesti peamiste galeriide avalike oksjonite tulemuste põhjal, mis annab ülevaate sellest, kuidas kunstiturg \nkäib ajas ning millised kunstimeediumid ja autorid on kõige paremini investeerinud.

Andmete põhjal on selge, kuidas kunsti populaarsus on viimastel aastatel teinud hiigelsuure hüppe nii hindade kui ka mahu poolest. Näiteks paljude kunstiteoste liikide puhul on hinnatõus või tootlus olnud üle 10% aastas. Seega on \n hästi valitud kunstiteos hea valik, et kaitsta oma raha inflatsiooni eest.

Kanvas.ai kunstiindeks ei sisalda praegu teavet oksjonivälise kunsti kohta, kuid \n plaanime hakata koguma andmeid ka NFTKanvas.ai \n lehel müüdud NFT-kunstimeedia kohta.

Praegu on kunstiindeksi metoodika väljatöötamisel. Palun saatke meile e-posti aadressil info@kanvas.ai kõik ettepanekud ja kommentaarid.''')


# FIGURE - date and average price
toc.subheader('Joonis - ajalooline hinnakäitumine')
fig = px.area(df_hist, x=df_hist.index, y="avg_price",
              labels={
                 "avg_price": "Indeksi ajalooline tootlus (€)",
                 "date": "Enampakkumise aasta",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Kunstiindeks annab ülevaate kunsti hinna tõusust ja langusest. Kunsti hind on viimastel aastatel teinud märgatava hüppe. Huvi kunstioksjonite turul kunsti investeerimise vastu on pärast pandeemiat hüppeliselt kasvanud.''')

# TABLE - categories average price
toc.subheader('Tabel - ajalooline hinnakäitumine tehnika kaupa')
table_data = create_table(df, "category", df["category"].unique(), calculate_volume=False, table_height=150)
st.table(table_data)
create_paragraph('''Järjestatud meediumi ehk tehnika järgi, vastavalt sellele, milline meedium domineerib enim müüdud teostes.''')

# Art Index Performance Prediction
toc.subheader('Kunstiindeksi tulemuslikkuse prognoosimine')
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

create_paragraph('''Selle analüüsi kohaselt prognoositakse, et kunstiindeksi hind tõuseb märkimisväärselt, tõustes 4 671,681 eurolt 2021. aasta veebruaris 5 469,599 eurole 2025. aasta detsembriks.
''')
# FIGURE - date and volume
toc.subheader('Joonis - ajalooline mahu kasv')
fig = px.area(df_hist, x=df_hist.index, y="volume", 
             labels={
                 "volume": "Maht (€)",
                 "date": "Oksjoni aasta",
             })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Mahu kasv annab meile ülevaate sellest, kui palju on oksjonite käive aja jooksul tõusnud ja langenud.

Näiteks 2001. aastal oli oksjonikäive umbes 174 000 eurot, siis 2021. aastal oli oksjonikäive 4,5 miljonit eurot. Kindlasti mängib väga olulist rolli krooni asendamine euroga, samuti on lisandunud rohkem oksjonigaleriisid. Siiski on kunstimüük alates 2019. aastast teinud märkimisväärse hüppe, mis on suurim 20 aasta jooksul. Viimane suur muutus toimus 2006-2009 majanduskriisi mõjude tõttu.''')

# TABLE - categories volume
toc.subheader('Tabel - ajalooline mahu kasv tehnika järgi')
table_data = create_table(df, "category", df["category"].unique(), calculate_volume=True, table_height=150)
st.table(table_data)
create_paragraph('''Sellest tabelist näeme, millisel meediumil on olnud suurim käive. Antud andmete põhjal näeme näiteks, et graafika on kõige populaarsem ja suurima aastase käibe kasvuprotsendiga (204% aastas 20 aasta jooksul ja 35% õlimaal samal ajal).''')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Joonis - Kunstimüük tehnika ja kunstniku järgi (alg- ja lõpphinna erinevus)')

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
artists = np.concatenate([["Kõik kunstnikud"], artists])
selected_artist =st.selectbox('Valige kunstnik', options=artists, key="1")
if selected_artist=='Kõik kunstnikud':

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

if selected_artist!='Kõik kunstnikud':
    artist_df = df2[df2["author"] == selected_artist]
    columns = ["author", "category", "technique", "total_sales", "overbid_%"]
    data = artist_df[columns]

    data = data.rename(columns={
        "author":"Kunstnik",
        "category":"Kategooria",
        "technique":"Tehnika",
        "total_sales": "Müük kokku",
        "overbid_%": "Ülepakkumise %",
    })
    data = data.reset_index(drop=True)
    st.write(data)


create_paragraph('''Tehnikad ja kunstnikud, kus värviskaala annab meile ülevaate, kui palju kunsti on oksjonite ajal ülepakkumisi tehtud ning mahud on järjestatud tehnika ja kunstniku järgi.

Näiteks sinine värv näitab kunstnikke ja meediume, mille puhul oli ülepakkumiste protsent kõige suurem. Maht on näidatud ka kunstniku nime kõrval. Näiteks Konrad Mägi on kõige rohkem müüdud kunstiteoseid, kuid see tabel näitab, et kõige suurem ülepakkumine läheb Olev Subbi töödele, mis puudutab tempera meediumit. (711,69 % hinnatõus alghinnast, samas kui Konrad Mägi puhul on numbrid 59,06 % õli kartongil ja 85,44 % õli lõuendil meediumi puhul). Kuigi mahu poolest on Konrad Mägi endiselt Subbi ees.''')

# FIGURE - treemap covering categories, techniques and authors by volume and overbid
toc.subheader('Joonis - Kunstimüük tehnika ja kunstniku järgi (ajalooline hinnakäitumine)')
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
artists = np.concatenate([["Kõik kunstnikud"], artists])

selected_artist2 =st.selectbox('Valige kunstnik', options=artists, key="2")
if selected_artist2=='Kõik kunstnikud':

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

if selected_artist2!='Kõik kunstnikud':

    artist_df = df2[df2["author"] == selected_artist2]
    columns = ["category", "technique", "author", "total_sales", "yearly_performance"]
    data = artist_df[columns]

    data = data.rename(columns={
        "author":"Kunstnik",
        "category":"Kategooria",
        "technique":"Tehnika",
        "total_sales": "Müük kokku",
        "yearly_performance": "Ajaloolised tulemused (%)",
    })
    data = data.reset_index(drop=True)
    st.write(data)


create_paragraph('''
Tehnikad ja kunstnikud, kus värviskaala annab meile ülevaate ajaloolistest hinnatulemustest ja mahust tehnika ja kunstniku järgi järjestatuna.

Näiteks sinine värv näitab kunstnikke ja meediume, mille ajalooline hinnakasv oli kõige suurem. Kunstniku nime kõrval on näidatud ka maht. Näiteks Konrad Mägi on kõige rohkem müüdud kunstiteoseid, kuid see tabel näitab, et kõrgeim keskmine ajalooline hind läheb Karin Lutsu töödele (498,84 % keskmine hinnakasv aastate jooksul, samas kui Konrad Mägi puhul on see arv 198,95 %). Kuigi Konrad Mägi on mahu poolest Lutsist ikka veel üle.''')

# TABLE - best authors average price
author_sum = df.groupby(["author"], sort=False)["end_price"].sum()
top_authors = author_sum.sort_values(ascending=False)[:10]

toc.subheader('Tabel - Top 10 parima tulemusega kunstnikud (hinnakäitumine)')
table_data = create_table(df, "author", top_authors.index, calculate_volume=False, table_height=250)    
st.table(table_data)
create_paragraph('''Selles tabelis on esitatud kõige populaarsemad kunstnikud ja nende ajalooline hinnakasvuprotsent. Protsent on arvutatud aasta keskmiste lõpphindade erinevuste põhjal.

Tabeli liider on Konrad Mägi, kelle kasvuprotsent on keskmiselt 198,95%. Seda kasvuprotsenti mõjutab kindlasti tema teoste ainulaadsus. Konrad Mägil on oksjonitel välja pandud piiratud arv teoseid. Teisel kohal on Eduard Wiiralt, kelle teoseid on erinevalt Konrad Mägist palju oksjonitel eksponeeritud. Wiiralti tööde alghinnad on madalad ja ta on kollektsionääride seas väga populaarne.''')

# TABLE - best authors volume
toc.subheader('Tabel - 10 kõige edukamat artisti (mahu kasv)')
table_data = create_table(df, "author", top_authors.index, calculate_volume=True, table_height=250)    
st.table(table_data)
create_paragraph('''Selles tabelis on esitatud kunstiteoste käive ja keskmine aastane kasv. Siin on Wiiralt 8. kohal ja Konrad Mägi 1. kohal. Kuna kasvuprotsent on kogu perioodi (2001-2021) käibe kohta, siis asuvad tabeli tipus kunstnikud, kelle teoseid on kõige rohkem ostetud.
''')

# FIGURE - date and price
toc.subheader('Joonis - Kunstiteose vanus vs. hind')
df['art_work_age'] = df['date'] - df['year']
q_low = df["end_price"].quantile(0.1)
q_hi  = df["end_price"].quantile(0.9)
df = df[(df["end_price"] < q_hi) & (df["end_price"] > q_low)]
fig = px.scatter(df.dropna(subset=["decade"]), x="art_work_age", y="end_price", color="category",
                 animation_frame="date", animation_group="technique", hover_name="technique",
                 size='date', hover_data=['author'], size_max=15, range_x=[-4,130], range_y=[-1000,8200],
                 labels={
                     "end_price": "Oksjoni lõplik müügihind (€)",
                     "art_work_age": "Kunstitöö vanus",
                     "author": "Autor",
                     "category": "Tehnika",
                     "decade": "Aastakümnend"
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Antud graafiku põhjal on võimalik määrata teose hinda vastavalt kunstiteose vanusele ja tehnikale. Tehnikad on eristatud värvide kaupa.

Vanim töö pärineb aastast 1900, kuid ei ole kõige kallim. Üldiselt on näha, et vanemad tööd on kallimad, välja arvatud Olev Subbi. On näha, et Teise maailmasõja eelsed tööd aastatest 1910-1940 on müüdud kallimalt.''')

# FIGURE - size and price
toc.subheader('Joonis - Kunstiteose suurus vs. hind')
df["dimension"] = df["dimension"] / (100*100)
q_low = df["dimension"].quantile(0.1)
q_hi  = df["dimension"].quantile(0.9)
df = df[(df["dimension"] < q_hi) & (df["dimension"] > q_low)]
fig = px.scatter(df.dropna(subset=["dimension"]), x="dimension", y="end_price", color="category",
                 animation_frame="date", animation_group="technique", hover_name="technique",
                 size='date', hover_data=['author'], size_max=15, range_x=[-0.03, 4], range_y=[-1000,8200],
                 labels={
                     "end_price": "Oksjoni lõplik müügihind (€)",
                     "dimension": "Mõõtmed (m²)",
                     "author": "Autor",
                     "category": "Tehnika",
                  })
fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
create_paragraph('''Ülevaade töö mõõtmete, tehnika ja hinna vahelisest suhtest. Paljud väiksema formaadiga tööd on sageli kallimad kui suured. Teose suurus ei tähenda tingimata, et see on kallim. Pigem on olulisem autor ja kui teose suurus. Näiteks Konrad Mägi Õlimaa on mõõtkavas keskmiste hulgas, kuid hinnaskaalal teistest tunduvalt kõrgemal (127 823 eurot haamrihind), samas kui suurima teose (Toomas Vint) haamrihind on 7094 eurot.''')

def create_credits(text):
    st.markdown('<span style="word-wrap:break-word;font-family:Source Code Pro;font-size: 14px;">' + text + '</span>', unsafe_allow_html=True)
create_credits('''Autoriõigus: Kanvas.ai''')
create_credits('''Autorid: Astrid Laupmaa, Julian Kaljuvee, Markus Sulg''')
create_credits('''Allikas: Estonian public art auction sales (2001-2021)''')
create_credits('''Other credits: Inspired by the original Estonian Art Index created by Riivo Anton; <br>Generous support from <a href="https://tezos.foundation/">Tezos Foundation</a>''')

toc.generate()

# @st.cache_data()
def convert_df():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return read_df('data/auctions_clean.csv').to_csv().encode('utf-8')

csv = convert_df()
st.download_button(label="Andmete allalaadimine",data=csv, file_name='estonian_art_index.csv', mime='text/csv')