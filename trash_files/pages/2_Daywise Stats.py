import streamlit as st
# For Logo Display
from PIL import Image

#Show logo 
a1, a2 = st.columns(2)
logo = Image.open('resources/ESoftLogo.png')
logo = logo.resize((150, 40))#and make it to whatever size you want.#
a1.image(logo)

# Subheader
# st.header("Yesterday and Today's Count")
st.markdown("""<div style="display:flex; justify-content: space-around;">
        <p style="height:25px; border-style:double; background-color:#fcfbfb; border-radius:50%; display:inline-block; padding:75px 40px 125px; text-align:center;">Yesterday's Count <br>1041</p>
        <p style="height:25px; border-style:double; background-color:#fcfbfb; border-radius:50%; display:inline-block; padding:75px 50px 125px; text-align:center;">Today's Count <br>1041</p>
       </div>""",unsafe_allow_html=True)