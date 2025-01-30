import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con
from streamlit_modal import Modal

import requests
import time

# set_page_configは最初に記述
set_con()

# CSSを使用して文字のスタイルを変更
st.markdown(
    """
    <style>
        .custom-font {
        font-size: 18px;
        color: #333;
    </style>
    """,
    unsafe_allow_html=True
)

hide_header()

# ヘッダー
create_header("らふまる")

# セッションから年月週を取得する
update_week = st.session_state['update_week']
update_year = st.session_state['update_year']
update_month = st.session_state['update_month']

# ログインしているユーザーIDを取得する
user_id = st.session_state["user"].user_id
path = st.session_state["path"]

# ユーザーがログインしてない場合
if "user_id" not in st.session_state:
    st.switch_page("pages/main.py")


colA, colB = st.columns([1,20])
with colA:
    if st.button("⬅︎"):
        del st.session_state["random_colors"]
        st.switch_page("pages/account_book_detail.py")
with colB:
    st.subheader(f"{update_year}年 {update_month}月 第{update_week}週の詳細")


# カラム
col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1, 3, 1, 3, 2, 2])
with col1:
    st.subheader("日付")
    st.markdown("---")
with col3:
    st.subheader("カテゴリ")
    st.markdown("---")
with col5:
    st.subheader("金額")
    st.markdown("---")

# 画面に表示する
url = f"http://{path}:8000/api/account_book_detail/"
response = requests.post(url, json={"user_id": user_id, "year": update_year,"month": update_month})

if response.status_code == 200:
    data = response.json()
    weekly_data = data.get('weekly_data', {})
    week_data = weekly_data.get(str(update_week), [])

# カラム
for item in week_data:
    col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1, 3, 1, 3, 2, 2])  # Adjust column widths as needed

    # 日付
    with col1:
        st.subheader(item.get('date', None))
        st.session_state['date'] = item['date']

    # カテゴリ
    with col3:
        st.subheader(item.get('category_name', None))
        st.session_state['category_id'] = item['category_id']

    # 金額
    with col5:
        st.subheader(f"¥{item.get('amount', 0):,}")
        st.session_state['amount'] = item['amount']

    # 更新ボタン
    with col6:
        st.session_state['memo'] = item['memo'] # メモ
        if st.button("更新", key=f"update_{item['item_no']}", use_container_width=True):
            st.session_state['item_no'] = item['item_no']
            st.switch_page("pages/account_book_item_update.py")

    # 削除ボタン
    with col7:
        delete_modal = Modal(title="削除確認", key=f"delete_modal_{item['item_no']}") # 削除用のポップアップ
        if st.button("削除", key=f"delete_button_{item['item_no']}", use_container_width=True):
            delete_modal.open()

    # 削除実行部分
    if delete_modal.is_open():
        with delete_modal.container():
            st.write("この項目を削除しますか？")
            
            # 確認ボタン
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
            # はいをクリックする場合、削除を実行する
                if st.button("はい", key=f"confirm_delete_{item['item_no']}"):
                    delete_url = f"http://{path}:8000/api/account_book_item_delete/"
                    delete_response = requests.post(delete_url, json={"user_id": user_id, "item_no": item['item_no']})

                    if delete_response.status_code == 200:
                        st.success("削除されました。")
                        time.sleep(1)
                    else:
                        st.error("削除に失敗しました。")
                    delete_modal.close()
                    st.switch_page("pages/account_update_home.py")

            # いいえをクリックする場合、ポップアップを閉じる
            with col_cancel:
                if st.button("いいえ", key=f"cancel_delete_{item['item_no']}"):
                    delete_modal.close()