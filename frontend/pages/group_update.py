import streamlit as st
import datetime
import socket
import requests
import time

from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con
from streamlit_modal import Modal

set_con()

# CSSを使用して背景の色を変更
st.markdown(
    """
    <style>
    
    </style>
    """,
    unsafe_allow_html=True
)

hide_header()

create_header("らふまる")

# パス設定
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# ユーザーがログインしてない場合
if "user_id" not in st.session_state:
    st.switch_page("pages/main.py")

# ユーザーID、グループIDを取得する
user_id = st.session_state["user_id"]
group_id = st.session_state['group_id']
group_name = st.session_state['group_name']
income_input = st.session_state['income_input']
path = st.session_state["path"]

# セッションから年月週を取得する
update_week = st.session_state['update_week']
update_year = st.session_state['update_year']
update_month = st.session_state['update_month']


colA, colB = st.columns([1,20])
with colA:
    if st.button("⬅︎", key="back"):
        st.switch_page("pages/group_detail.py")
with colB:
    st.subheader(f"{update_year}年 {update_month}月 第{update_week}週の詳細")

colA, colB, colC, colD = st.columns([1, 1.3, 1, 8])

# 最初のアクセスする時、現在の日付を取得
if "month" not in st.session_state:
    st.session_state.month = datetime.datetime.today().month

# カラム
col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([5, 0.5, 4, 0.5, 4, 1, 4, 2, 2])
with col1:
    st.subheader("ユーザー")
    st.markdown("---")
with col3:
    st.subheader("日付")
    st.markdown("---")
with col5:
    st.subheader("カテゴリ")
    st.markdown("---")
with col7:
    st.subheader("金額")
    st.markdown("---")

# データを取得して表示
url = f"http://{path}:8000/api/share_account_book_detail/"
response = requests.post(url, json={"group_id": group_id, "user_id": user_id, "year": update_year,"month": update_month})

if response.status_code == 200:
    data = response.json()
    weekly_data = data.get('weekly_data', {})
    week_data = weekly_data.get(str(update_week), [])

for item in week_data:
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([5, 0.5, 4, 0.5, 4, 1, 4, 2, 2])
    # ユーザー
    with col1:
        st.subheader(item.get('nickname', None))
        st.session_state['nickname'] = item['nickname']

    # 日付
    with col3:
        st.subheader(item.get('date', None))
        st.session_state['date'] = item['date']

    # カテゴリ
    with col5:
        st.subheader(item.get('category_name', None))
        st.session_state['category_id'] = item['category_id']

    # 金額
    with col7:
        st.subheader(f"¥{item.get('amount', 0):,}")
        st.session_state['amount'] = item['amount']
        # メモ
        st.session_state['memo'] = item['memo']
    

    # ボタンを交互に配置
    if item['user_id'] == user_id:
        with col8:
            if st.button("更新", key=f"update_{item['shareditem_id']}", use_container_width=True):
                st.session_state['shareditem_id'] = item['shareditem_id']
                st.switch_page("pages/group_item_update.py")

        with col9:
            delete_modal = Modal(title="削除確認", key=f"delete_modal_{item['shareditem_id']}") # 削除用のポップアップ
            if st.button("削除", key=f"delete_button_{item['shareditem_id']}", use_container_width=True):
                delete_modal.open()

        # 削除実行部分
        if delete_modal.is_open():
            with delete_modal.container():
                st.write("この項目を削除しますか？")
                
                # 確認ボタン
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                # はいをクリックする場合、削除を実行する
                    if st.button("はい", key=f"confirm_delete_{item['shareditem_id']}"):
                        delete_url = f"http://{path}:8000/api/share_account_book_item_delete/"
                        delete_response = requests.post(delete_url, json={"group_id": group_id, "user_id": user_id, "shareditem_id": item['shareditem_id']})

                        if delete_response.status_code == 200:
                            st.success("削除されました。")
                            time.sleep(1)
                        else:
                            st.error("削除に失敗しました。")
                        delete_modal.close()
                        st.switch_page("pages/group_update.py")

                # いいえをクリックする場合、ポップアップを閉じる
                with col_cancel:
                    if st.button("いいえ", key=f"cancel_delete_{item['shareditem_id']}"):
                        delete_modal.close()