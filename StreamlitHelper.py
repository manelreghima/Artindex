import streamlit as st
import os
import base64
import pandas as pd
import numpy as np

# https://discuss.streamlit.io/t/table-of-contents-widget/3470/12
class Toc:

    def __init__(self):
        self._items = []
        self._placeholder = None
    
    def title(self, text):
        self._markdown(text, "h1")

    def header(self, text):
        self._markdown(text, "h2", " " * 2)

    def subheader(self, text):
        self._markdown(text, "h3", " " * 4)

    def placeholder(self, sidebar=False):
        self._placeholder = st.sidebar.empty() if sidebar else st.empty()

    def generate(self):
        if self._placeholder:
            contents = "\n".join(self._items)
            contents_wrapped = "<div style='margin-bottom:8px;'>" + contents +  "</div>"
            self._placeholder.markdown(contents_wrapped, unsafe_allow_html=True)
    
    def _markdown(self, text, level, space=""):
        import re
        key = re.sub('[^0-9a-zA-Z]+', '-', text).lower()
        st.markdown(f"<div id='{key}'></div>", unsafe_allow_html=True)
        st.markdown(f"<{level}>{text}</{level}>", unsafe_allow_html=True)
        text_removed = re.sub('.*- ', "", text)
        self._items.append(f"<div style='border-bottom:solid;padding:4px 0px;'> {space}{space} <a href='#{key}' style='color:black;'>{text_removed}</a></div>")

# LOGO
# https://discuss.streamlit.io/t/href-on-image/9693/4
@st.cache(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url, max_width):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" style="max-width:{max_width};width:100%" />
        </a>'''
    return html_code

@st.cache(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def read_df(path:str):
    return pd.read_csv(path)

@st.cache(ttl=60*60*24*7, max_entries=300, allow_output_mutation=True)
def create_table(df, category_column:str, _category_list:list, calculate_volume:bool, table_height:int):
    category_returns = []
    for cat in _category_list:
        df_cat = df[df[category_column]==cat]

        dates = np.sort(df_cat["date"].unique())

        prices = []
        start_year = df_cat["date"].min()
        if pd.isna(start_year):
            continue
        df_cat_date = df_cat[df_cat["date"]==start_year]
        if calculate_volume: 
            prices.append(df_cat_date["end_price"].sum())
        else:
            prices.append(df_cat_date["end_price"].mean())
        price_changes = []
        last_year = start_year
        for date in dates[1:]:
            df_cat_date = df_cat[df_cat["date"]==date]

            start_sum = prices[-1]
            end_sum = 0
            if calculate_volume: 
                end_sum = df_cat_date["end_price"].sum()
            else:
                end_sum = df_cat_date["end_price"].mean()

            if start_sum == 0 or end_sum == 0:
                continue
            price_change = (end_sum - start_sum) / start_sum * 100 / (date-last_year)
            price_changes.append(price_change) # Kasvu arvutus
            prices.append(end_sum) # Jätame meelde selle aasta hinna
            last_year = date
        annual_return = round(np.mean(price_changes), 4)
        total_return = round(annual_return * len(dates), 4)
        if len(dates) == 1:
            annual_return = 0
            total_return = 0
        year_span = " - ".join(map(str, [round(start_year), round(last_year)]))
        category_returns.append([cat, year_span, total_return, annual_return])
    col = ""
    # check if english language
    is_english = df["category"].str.contains('Graphics').any() or "category_parent" in df.columns and df["category_parent"].str.contains("Graphics").any()
    

    if is_english:
        if category_column == "author":
            col = "Author"
        else:
            col = "Technique"
        df_cat_returns = pd.DataFrame(category_returns, columns=[col, "Time span", "Kogukasv algusest (%)", "Yearly growth (%)"]) 
        return df_cat_returns.drop("Kogukasv algusest (%)", axis=1)
    else:
        if category_column == "author":
            col = "Autor"
        else:
            col = "Tehnika"
        df_cat_returns = pd.DataFrame(category_returns, columns=[col, "Aastavahemik", "Kogukasv algusest (%)", "Iga-aastane kasv (%)"]) 

    #df_cat_returns = df_cat_returns.sort_values(by="Iga-aastane kasv (%)", ascending=False)
        return df_cat_returns.drop("Kogukasv algusest (%)", axis=1)