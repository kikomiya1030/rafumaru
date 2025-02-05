import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import requests
import time
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

# ユーザーIDと認証コードを取得
pass_user_id = st.session_state.get("pass_user_id")

with col_1:
    pass
with col_2:
    with st.form(key="reset"):
        # タイトル
        register_html = """
        <style>
            .center {
                text-align: center;
            }
        </style>
        <h1 class='center'>パスワードリセット</h1>
        """
        st.markdown(register_html, unsafe_allow_html=True)

        # スペースを作成
        space_html = """
        <style>
            .space {
                padding: 20px 0px;
            }
        </style>
        <div class='space'></div>
        """
        st.markdown(space_html, unsafe_allow_html=True)

        # メッセージエリア
        message = st.empty()

        # プレースホルダーを追加
        new_pass = st.text_input("新しいパスワード", key="new_pass", placeholder="パスワードは8桁以上16桁以下で入力してください。", type="password")
        confirmed_pass = st.text_input("パスワード確認", key="confirmed_pass", placeholder="もう一度入力してください", type="password")

        st.markdown(space_html, unsafe_allow_html=True)

        # エラーメッセージを確定ボタンの上に表示
        error_msg = st.empty()

        # 確定ボタン
        col_4, col_5, col_6 = st.columns(3)
        with col_4:
            pass
        with col_5:
            submit_btn = st.form_submit_button("確定", use_container_width=True)
            if submit_btn:
                if not new_pass or not confirmed_pass:
                    error_msg.error("パスワードを入力してください。")
                elif new_pass != confirmed_pass:
                    error_msg.error("パスワードは一致していません。")
                elif (len(new_pass) < 8 or len(new_pass) > 16) or (len(confirmed_pass) < 8 or len(new_pass) > 16):
                    error_msg.error("パスワードは8桁以上16桁以下で入力してください。")          
                else:
                    path = st.session_state["path"]
                    reset_url = f"http://{path}:8000/api/new_pw/" # ローカル
                    response = requests.post(reset_url, json={"user_id": pass_user_id, "new_pass": new_pass})

                    if response.status_code == 200: # リクエスト成功
                        message.success("パスワードリセットしました！")
                        time.sleep(1)
                        st.switch_page("pages/password_reset_comp.py")
                    else:
                        st.switch_page("pages/error.py")
        with col_6:
            pass
with col_3:
    pass
