from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import socket
import time
import pytz

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
if "info_rev" not in st.session_state:
    st.session_state["info_rev"] = False
if "notice" not in st.session_state:
    st.switch_page("pages/main.py")

col_left, col_mid, col_right = st.columns([3,9,3])


# 登録内容内容の画面
if st.session_state["notice"] == False:
    with col_mid:
        col_mid1, col_mid2 = st.columns([9,1])
        with col_mid1:
            st.subheader("登録内容確認")
        with col_mid2:
            if not st.session_state["info_rev"]:
                if st.button("修正"):
                    st.session_state["info_rev"] = True
                    st.switch_page("pages/user.py")
            else:
                if st.button("戻る"):
                    st.session_state["info_rev"] = False
                    st.switch_page("pages/user.py")
        
        if not st.session_state["info_rev"]:
            with st.container(border=True):
                col1, col2 = st.columns([1,2])
                with col1:
                    st.write("ユーザーID:")
                    st.write("ニックネーム：")
                    st.write("メールアドレス：")

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
        else:
            with st.form("form"):
                nickname = st.text_input(label="ニックネーム",value=nickname)
                email = st.text_input(label="メールアドレス", value=email)
                st.caption("登録されている内容を変更できます。")
                msg = st.empty()
                if st.form_submit_button("修正"):
                    rev_url = f"http://{path}:8000/api/rev_account/"
                    rev_response = requests.post(rev_url, json={"user_id": user_id, "email": email, "nickname": nickname})
                    if rev_response.status_code == 200:
                        msg.success("個人情報を更新しました。")
                        time.sleep(1)
                        st.session_state["nickname"] = nickname
                        st.session_state["mail_address"] = email
                        st.session_state["info_rev"] = False
                        st.switch_page("pages/user.py")
                    else:
                        st.switch_page("pages/error.py")


# 通知画面
else:
    with col_mid:
        colA, colB = st.columns([1,9])
        with colA:
            if st.button("⬅︎", key="back"):
                st.session_state["notice"] = False
                st.switch_page("pages/user.py")
        with colB:
            st.subheader("通知")

        with st.container(border=True):
            notice_url = f"http://{path}:8000/api/notice_view/"
            notice_response = requests.post(notice_url, json={"user_id": user_id})
            if notice_response.status_code == 200:
                notice_data = notice_response.json()
                if notice_data:
                    notice_num = 1
                    for notice in notice_data:
                        notice_id = notice["notice_id"]
                        notice_title = notice["notice_title"]
                        notice_content = notice["notice_content"]
                        notice_date = notice["notice_date"]
                        
                        col_1, col_2 = st.columns([9,1])
                        with col_1:
                            st.write(f"**{notice_num}. {notice_title}**")
                        with col_2:
                            if st.button("削除", key=f"delete{notice_num}"):
                                delete_url = f"http://{path}:8000/api/notice_delete/"  # ローカル
                                delete_response = requests.post(delete_url, json={"user_id": user_id, "notice_id": notice_id})
                                if reject_response.status_code == 200:
                                    st.switch_page("pages/user.py")
                        st.write(f"{notice_content}")
                        # 日付表示
                        notice_date_re = datetime.strptime(notice_date, '%Y-%m-%dT%H:%M:%SZ')
                        japan_tz = pytz.timezone("Asia/Tokyo")
                        notice_date = notice_date_re.replace(tzinfo=pytz.utc).astimezone(japan_tz)
                        st.caption(f"{notice_date.strftime('%Y-%m-%d %H:%M:%S')}")

                        col_3, col_4 = st.columns([1,9])
                        msg = st.empty()
                        with col_3:
                            if st.button("加入", key=f"join{notice_num}"):
                                join_url = f"http://{path}:8000/api/notice_gp/"  # ローカル
                                join_response = requests.post(join_url, json={"user_id": user_id, "notice_id": notice_id})
                                if join_response.status_code == 200:
                                    group_data = join_response.json()
                                    group_id = group_data["gp_id"]
                                    group_pw = group_data["gp_pw"]

                                    add_url = f"http://{path}:8000/api/group_add/"
                                    add_response = requests.post(add_url, data={"user_id": user_id, "group_id": group_id, "group_password": group_pw})
                                    if add_response.status_code == 200:
                                        # 通知を削除する
                                        delete_url = f"http://{path}:8000/api/notice_delete/"
                                        delete_response = requests.post(delete_url, json={"user_id": user_id, "notice_id": notice_id})
                                        msg.success("加入！")
                                        time.sleep(1)
                                        st.switch_page("pages/group.py")
                                else:
                                    msg.error("失敗しました。")
                        with col_4:
                            if st.button("拒否", key=f"reject{notice_num}"):
                                reject_url = f"http://{path}:8000/api/notice_delete/"  # ローカル
                                reject_response = requests.post(reject_url, json={"user_id": user_id, "notice_id": notice_id})
                                if reject_response.status_code == 200:
                                    st.switch_page("pages/user.py")
                                else:
                                    msg.error("失敗しました。")
                        st.write("---")
                        notice_num+=1
                    st.caption(f"{nickname}の通知ボックス")
                else:
                    st.info("通知がありません。")
