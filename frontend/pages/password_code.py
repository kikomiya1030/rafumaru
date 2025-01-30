import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import requests
import time
import socket

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
            .small {
                font-size: 18px;
            }
        </style>
        <h1 class='center'>パスワードリセット</h1>
        <h2 class='small'>メールを送信しました。</h2>
        <h3 class='small'>送信されたメールから認証コードを確認してください。</h3>
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

        # エラーメッセージ用の空要素
        message = st.empty()
        
        # ユーザーIDと認証コードを取得
        pass_user_id = st.session_state["pass_user_id"]
        code = st.session_state["code"]
        print(pass_user_id)
        print(code)

        # 認証コード入力フィールド
        attestation_cd = st.text_input("認証コード", key="attestation_cd")

        st.markdown(space_html, unsafe_allow_html=True)

        # エラーメッセージを確定ボタンの上に表示
        error_msg = st.empty()

        # 確定ボタンの配置
        col_4, col_5, col_6, col_7 = st.columns(4)
        with col_4:
            pass
        with col_5:
            submit_btn = st.form_submit_button("確定", use_container_width=True)
            if submit_btn:
                # 認証コードが入力されているか確認
                if attestation_cd == "":
                    error_msg.error("認証コードを入力してください")
                else:
                    # 認証コード確認 # 11.17追加
                    path = st.session_state["path"]
                    reset_url = f"http://{path}:8000/api/attestation_cd/" # ローカル
                    response = requests.post(reset_url, json={"attestation_cd": attestation_cd, "code": code, "user_id": pass_user_id}) #11.17

                    if response.status_code == 200: # リクエスト成功
                        message.success("認証コードを確認しました！")
                        time.sleep(1)
                        st.switch_page("pages/password_new.py")
                    else:
                        error_msg.error("無効な認証コードです。再度確認してください。")

        with col_6:
            submit_btn = st.form_submit_button("メール再送", use_container_width=True)
            # もう一度メールに送信する
            if submit_btn:
                message.success("該当メールアドレスにもう一度送信しました！")
                time.sleep(1)
                path = st.session_state["path"]
                reset_url = f"http://{path}:8000/api/password_reset/" # ローカル
                response = requests.post(reset_url, json={"user_id": pass_user_id})

                data = response.json()
                pass_user_id = data.get('user_id')
                code = data.get("code")
                st.session_state["pass_user_id"] = pass_user_id
                st.session_state["code"] = code
                
                st.switch_page("pages/password_code.py")
with col_3:
    pass
