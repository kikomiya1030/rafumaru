import streamlit as st
import socket
from streamlit_modal import Modal
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import requests
import time

set_con()

hide_header()

create_header("らふまる")

# ユーザー確認
if st.session_state["user_id"] is None or "user_id" not in st.session_state:
    st.switch_page("pages/main.py")

# パス設定
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# 削除ボタンの初期設定
if "show_confirm_delete" not in st.session_state:
    st.session_state["show_confirm_delete"] = False    

# セッション確認
session_list = ["path", "show_confirm_delete"]
if any(session not in st.session_state for session in session_list):
    st.switch_page("pages/main.py")
    st.stop()

# セッションからデータを取り出す
user_id = st.session_state["user_id"]
path = st.session_state["path"]


# グループリストを取得
url = f"http://{path}:8000/api/group/"
response = requests.post(url, json={"user_id": user_id})

if response.status_code == 200:
    group_data = response.json()
else:
    group_data = []

# 空白のグループリストの場合
if group_data == []:
    st.switch_page("pages/group_join.py")


# 画面設定
if "user_id" in st.session_state:
    # タイトル設定
    st.subheader("共同家計簿選択")
    st.caption("※既に加入している共同家計簿を見られます。")
    st.write("")
    st.write("")
    # 項目名の設定
    colA, colB, colC = st.columns([8, 1, 3]) 
    with colA:
        col, col_a, col_b, col_c = st.columns([1, 3, 1, 1])
        with col:
            st.write("ID")
            st.markdown("---")
        with col_a:
            st.write("グループ名")
            st.markdown("---")
        with col_c:
            pass

    # グループ内容表示
    col1, col2, col3 = st.columns([8, 1, 3])
    with col1:
        if isinstance(group_data, list) and group_data:
            for group in group_data:
                group_id = group.get("group_id", "Unknown")
                group_name = group.get("group_name", "Unknown")
                income_input = group.get("income_input")

                # 削除モーダル用セッション
                modal_key = f"show_confirm_delete_{group_id}"
                if modal_key not in st.session_state:
                    st.session_state[modal_key] = False
                modal = Modal("グループ削除確認", key=f"delete_modal_{group_id}")

                with st.container(key=f"group_form_{group_id}"):
                    col, col_1, col_2, col_3 = st.columns([1, 3, 1, 1])

                    with col:
                        group_id_str = str(group_id)
                        group_id_str = f"{group_id_str[:3]} {group_id_str[3:6]} {group_id_str[6:]}"
                        st.write(group_id_str)

                    with col_1:
                        st.write(group_name)

                    with col_2:
                            submit_group = st.button(label="📖", key=f"{group_id}",)
                            if submit_group:
                                # グループ番号をセッションに保存する
                                st.session_state['group_id'] = group_id
                                st.session_state['group_name'] = group_name
                                st.session_state['income_input'] = income_input
                                st.session_state["invite"] = False
                                st.session_state["chat_box"] = False
                                st.switch_page("pages/group_main.py")

                    with col_3:
                        # グループ削除用のポップアップ
                        modal = Modal("グループ削除確認", key=f"delete_model_{group_id}")
                        # 項目のボタンをクリックする場合
                        if st.session_state["show_confirm_delete"]:
                            # ボタン設定
                            confirm_delete = st.button(label="削除", key=f"delete_{group_id}", use_container_width=True)
                            if confirm_delete:
                                st.session_state[modal_key] = True

                # グループ削除用のモーダル設定               
                if st.session_state[modal_key]:
                    with modal.container():
                        st.write("このグループを削除しますか？")
                        modal_msg = st.empty()
                        col_confirm, col_cancel = st.columns([1, 9])
                        with col_confirm:
                            # はいをクリックする場合、削除を実行する
                            if st.button("はい", key=f"group_delete_{group_id}"):
                                delete_url = f"http://{path}:8000/api/group_delete/"
                                delete_response = requests.post(delete_url, json={"user_id": user_id, "group_id": group_id})
                                if delete_response.status_code == 200:
                                    modal_msg.success("削除しました。")
                                    time.sleep(1)
                                else:
                                    modal_msg.error("削除に失敗しました。")
                                st.session_state[modal_key] = False
                                st.switch_page("pages/group.py")
                        with col_cancel:
                            # いいえをクリックする場合、ポップアップを閉じる
                            if st.button("いいえ", key=f"group_delete_cancel_{group_id}"):
                                st.session_state[modal_key] = False
                                st.switch_page("pages/group.py")
    with col2:
        pass

    with col3:
        # 右の操作ボタンの配置
        col_a, col_b = st.columns([1,2])  
        with col_a:
            pass
        with col_b:
            # 作成ボタンと削除ボタンをフォーム内に配置
            with st.form(key="create_delete_form"):
                st.text("") # 空白の調整
                # グループ作成
                submit_btn_create = st.form_submit_button("グループ作成", use_container_width=True)
                if submit_btn_create:
                    st.switch_page("pages/group_create.py")

                st.text("") # 空白の調整
                
                # グループ加入
                submit_btn_join = st.form_submit_button("グループ加入", use_container_width=True)
                if submit_btn_join:
                    st.switch_page("pages/group_join.py")
                
                st.text("")

                # 項目の一つ一つの削除ボタンを表示する
                submit_btn_delete = st.form_submit_button("グループ削除", use_container_width=True)
                if submit_btn_delete:
                    st.session_state["show_confirm_delete"] = True
                    st.switch_page("pages/group.py")
                
                st.text("") # 空白の調整