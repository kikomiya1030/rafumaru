import streamlit as st
import socket
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import requests

set_con()

if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip


hide_header()
create_header("らふまる")

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
        <h1 class='center'>パスワードリセット</h1>
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

        # メッセージエリア
        message = st.empty()

        # ID入力フィールド
        user_id = st.text_input("ID入力")

        st.markdown(space_html, unsafe_allow_html=True)

        # エラーメッセージを確定ボタンの上に表示
        error_msg = st.empty()

        # 戻る、確定ボタンの配置
        col_4, col_5, col_6 = st.columns(3)
        with col_4:
            pass
        with col_5:
            submit_btn = st.form_submit_button("確定", use_container_width=True)
            if submit_btn:
                # ID入力の確認
                if user_id == "":
                    error_msg.error("IDを入力してください。")
                else:
                    path = st.session_state["path"]
                    reset_url = f"http://{path}:8000/api/password_reset/" # ローカル
                    message.success("該当メールアドレスに送信しました！")
                    response = requests.post(reset_url, json={"user_id": user_id})
                    if response.status_code == 200: # リクエスト成功
                        # 取得された認証コードを保存
                        data = response.json()
                        code = data.get("code")
                        pass_user_id = data.get('user_id')
                        st.session_state["pass_user_id"] = pass_user_id
                        st.session_state["code"] = code
                        
                        st.switch_page("pages/password_code.py")
                    else:
                        message.error("無効なIDです。再度確認してください。")
        with col_6:
            pass
with col_3:
    pass