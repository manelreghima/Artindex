import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.title('Kanvas.AI Art Index')

st.header('Haus Auctions - Map of Art Market')

st.subheader('Total sales by artist and overbidding amount')

df = pd.read_csv('data/haus_clean.csv')
df['overbid_%'] = (df['end_price'] - df['start_price'])/df['start_price'] * 100
df['art_work_age'] = df['date'] - df['year']
df2 = df.groupby(['author', 'technique', 'category']).agg({'end_price':['sum'], 'overbid_%':['mean']})
df2.columns = ['total_sales', 'overbid_%']
df2 = df2.reset_index()

fig = px.treemap(df2, path=['category', 'technique', 'author'], values='total_sales',
                  color='overbid_%', hover_data=['author'],
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df2['overbid_%'], weights=df2['total_sales']),
                  range_color = (0, df['overbid_%'].mean() + df['overbid_%'].std()))


st.plotly_chart(fig, use_container_width=True)

st.subheader('Relationship between the age of the art work and price')

df = df.dropna(subset=["decade"])
fig = px.scatter(df, x="art_work_age", y="overbid_%", color="category",
                 size='decade', hover_data=['author'])

st.plotly_chart(fig, use_container_width=True)

st.text('Markus Sulg, Julian Kaljuvee')
st.text('Source: Haus Auctions')
