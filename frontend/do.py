import socket
import streamlit as st 
import datetime
from streamlit.runtime.scriptrunner import get_script_run_ctx

st.set_page_config(page_title="らふまる", page_icon="🥺")

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "mail_address" not in st.session_state:
    st.session_state["mail_address"] = None
if "password" not in st.session_state:
    st.session_state["password"] = None
if "nickname" not in st.session_state:
    st.session_state["nickname"] = None
if "last_login" not in st.session_state:
    st.session_state["last_login"] = None
if "month" not in st.session_state:
    st.session_state["month"] = datetime.datetime.today().month
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

st.switch_page("pages/main.py")