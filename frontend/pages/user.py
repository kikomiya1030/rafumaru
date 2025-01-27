from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import socket
import time
from streamlit_modal import Modal

from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con


set_con()

hide_header()

# ヘッダー
create_header("らふまる")

# パス設定
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# ユーザーID取得する
user_id = st.session_state["user_id"]
nickname = st.session_state["nickname"]
email = st.session_state["mail_address"]

path = st.session_state["path"]

# ユーザーがログインしてない場合
if st.session_state["user_id"] == None:
    st.switch_page("pages/main.py")
if "show_confirm" not in st.session_state:
    st.session_state["show_confirm"] = False
if "notice" not in st.session_state:
    st.switch_page("pages/main.py")

col_left, col_mid, col_right = st.columns([3,9,3])


# 登録内容内容の画面
if st.session_state["notice"] == False:
    with col_mid:
        st.subheader("登録内容確認")
        with st.container(border=True):
            col1, col2 = st.columns([1,2])
            with col1:
                st.write("User id:")
                st.write("Nickname:")
                st.write("email:")

            with col2:
                st.write(user_id)
                st.write(nickname)
                st.write(email)
            st.write("")


            # 削除用のボタン
            if st.button("退会", use_container_width=True):
                st.session_state["show_confirm"] = True

            if st.session_state["show_confirm"]:
                st.write("本当にアカウントを削除しますか？")    

                col_confirm, col_cancel = st.columns([1, 9])
                with col_confirm:
                # はいをクリックする場合、削除を実行する
                    if st.button("はい", key="yes"):
                        url = f"http://{path}:8000/api/delete_account/"  # ローカル
                        response = requests.post(url, json={"user_id": user_id})
                        if response.status_code == 200:
                            st.success("退会しました。")
                            time.sleep(1)
                            del st.session_state["user_id"]
                            del st.session_state["mail_address"]
                            del st.session_state["password"]
                            del st.session_state["nickname"]
                            del st.session_state["last_login"]
                            del st.session_state["show_confirm"]
                            st.session_state["sessionid"] = None
                            st.switch_page("pages/main.py")
                        else:
                            st.error("削除に失敗しました。")
                with col_cancel:
                    if st.button("いいえ", key="no"):
                        st.session_state["show_confirm"] = False
                        st.switch_page("pages/user.py")

# 通知画面
else:
    with col_mid:
        colA, colB = st.columns([1,9])
        with colA:
            if st.button("⬅︎", key="back"):
                st.session_state["notice"] = False
                st.switch_page("pages/user.py")
        with colB:
            st.subheader("お知らせ・通知")

        with st.container(border=True):
            notice_view_url = f"http://{path}:8000/api/notice_view/"
            notice_response = requests.post(notice_view_url, json={"re_user_id": user_id})
            if notice_response.status_code == 200:
                notice_data = notice_response.json()
                if notice_data:
                    df = pd.DataFrame(notice_data)
                    df['notice_date'] = pd.to_datetime(df['notice_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.subheader("通知リスト")
                    st.table(df[['notice_title', 'notice_content', 'notice_date']])
                else:
                    st.info("通知がありません。")
