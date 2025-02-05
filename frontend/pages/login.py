import streamlit as st 
import time
import requests
import socket
from user import User
from items.hide_default_header import hide_header
from items.set_config import set_con

set_con()

hide_header()

if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# col-1, col-2, col-3は、全体の画面分割
submit_btn = False
col_1, col_2, col_3 = st.columns([1, 8, 1])
with col_1:
    if st.button("⬅︎"):
        st.switch_page("pages/main.py")
with col_2:
    with st.form(key="login"):
        login_html = """
        <style>
            .center {
                text-align: center;
            }
        </style>
        <h1 class='center'>ログイン</h1>
        """
        st.markdown(login_html, unsafe_allow_html=True)
        space_20_html = """
        <style>
            .space_20 {
                padding: 20px 0px;
            }
        </style>
        <div class='space_20'></div>
        """
        space_45_html = """
        <style>
            .space_45 {
                padding: 45px 0px;
            }
        </style>
        <div class='space_45'></div>
        """
        st.markdown(space_20_html, unsafe_allow_html=True)
        
        message = st.text("")
        user_id = st.text_input("ID", key="user_id_input")
        password = st.text_input("パスワード", type="password", key="password_input")

        st.markdown(space_45_html, unsafe_allow_html=True)
        # col4-, col-5, col-6はログインボタンの画面分割
        col_4, col_5, col_6 = st.columns([1, 2, 1])
        with col_4:
            pass
        with col_5:
            submit_btn = st.form_submit_button("ログイン", use_container_width=True)
        with col_6:
            pass
        col_7, col_8, col_9, col_10 = st.columns([1, 2, 2, 1])
        with col_7:
            pass
        with col_8:
            if st.form_submit_button(label="新規登録", use_container_width=True):
                st.switch_page("pages/register.py")
        with col_9:
            if st.form_submit_button(label="パスワードリセット", use_container_width=True):
                st.switch_page("pages/password_reset.py")
        with col_10:
            pass
        
with col_3:
    pass

if submit_btn == True:
    if user_id == "" or user_id == None:
        message.error("IDを入力してください。")
    elif password == "" or password == None:
        message.error("パスワードを入力してください。")
    else:
        path = st.session_state["path"]
        response = requests.post(f"http://{path}:8000/api/login/", json={"user": user_id, "pass":password})
        if response.status_code == 200:
            response_data = response.json()
            response_message = response_data["message"]
            if response_message == "success":
                in_user_id = response_data["user_id"]
                in_user_mail = response_data["mail_address"]
                in_user_pass = response_data["password"]
                in_user_nick = response_data["nickname"]
                in_last_login = response_data["last_login"]
                message.success("ログインしました！")
                st.session_state["user_id"] = in_user_id
                st.session_state["mail_address"] = in_user_mail
                st.session_state["password"] = in_user_pass
                st.session_state["nickname"] = in_user_nick
                st.session_state["last_login"] = in_last_login
                user = User(in_user_id, in_user_mail, in_user_pass, in_user_nick, in_last_login)
                st.session_state["user"] = user
                time.sleep(1)
                st.switch_page("pages/main.py")
            else:
                print(response_message)
                message.error("ID、またはパスワードが確認できません。")
