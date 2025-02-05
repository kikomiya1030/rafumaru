import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import socket

set_con()

hide_header()
create_header("らふまる")

# パス設定
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

submit_btn = False
col_1, col_2, col_3 = st.columns([1, 8, 1])
with col_1:
    pass
with col_2:
    with st.form(key="reset"):
        # タイトルのスタイル設定
        register_html = """
        <style>
            .center {
                text-align: center;
            }
        </style>
        <h1 class='center'>パスワードリセット完了</h1>
        """
        st.markdown(register_html, unsafe_allow_html=True)
        
        # スペース設定
        space_html = """
        <style>
            .space {
                padding: 20px 0px;
            }
        </style>
        <div class='space'></div>
        """
        st.markdown(space_html, unsafe_allow_html=True)
        
        # 確定ボタンの配置
        col_4, col_5, col_6 = st.columns(3)
        with col_4:
            pass
        with col_5:
            submit_btn = st.form_submit_button("ログイン画面へ", use_container_width=True)
            if submit_btn:
                # ページを遷移
                st.switch_page("pages/login.py")
        with col_6:
            pass
with col_3:
    pass
