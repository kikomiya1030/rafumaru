import streamlit as st 
from streamlit_lottie import st_lottie
import time 
import json 

from items.hide_default_header import hide_header
from items.set_config import set_con
from items.balloons import balloons

set_con()
hide_header()

col_1, col_2, col_3 = st.columns([2, 6, 2])

with col_1:
    pass

with col_2:
    def load_lottie_local(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)
    lottie_json = load_lottie_local("json/create_account.json")
    if lottie_json:
        st_lottie(lottie_json, speed=1, key="lottie_animation")
    balloons()
    time.sleep(0.5)
    st.switch_page("pages/main.py")

with col_3:
    pass