import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con
import datetime
import requests
import time
import socket

set_con()


# CSSを使用して背景の色を変更
st.markdown(
    """
    <style>
    /* Streamlitのウィジェットボックスのスタイル */
    .stButton > button {
        background-color: #ffffff; /* ボタンの背景色 */
        color: #000000; /* ボタンの文字色 */
        border: 1px solid #cccccc; /* ボタンの境界線 */
        padding: 5px 10px;
    }

    /* 列の間隔やコンテンツのカスタマイズ */
    .css-1aumxhk {
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# セッション確認
session_list = ["path", "group_id", "income_input", "update_year", "update_month", "update_week", "shareditem_id", "category_id", "amount", "date", "memo"]
if any(session not in st.session_state for session in session_list):
    st.switch_page("pages/main.py")
    st.stop()

# セッションからすべてのデータを取得する
user_id = st.session_state["user_id"]
path = st.session_state["path"]
group_id = st.session_state["group_id"]
income_input = st.session_state["income_input"]

update_year = st.session_state["update_year"]
update_month = st.session_state["update_month"]
update_week = st.session_state["update_week"]
update_shareditem_id = st.session_state["shareditem_id"]
update_category_id = st.session_state["category_id"]
update_amount = st.session_state["amount"]
update_date = st.session_state["date"]
update_memo = st.session_state["memo"]


colA, colB = st.columns([1,20])
with colA:
    if st.button("⬅︎"):
        st.switch_page("pages/group_update.py")
with colB:
    st.subheader("項目修正")


col_1, col_2, col_3 = st.columns([1, 2, 1])
with col_1:
    pass
with col_2:
    with st.form(key="detail"):
        # 日付
        update_date = datetime.datetime.strptime(update_date, "%Y-%m-%d").date()
        date = st.date_input(label="日付", value=update_date)
        
        # カテゴリ
        category_url = f"http://{path}:8000/api/get_category/"
        category_response = requests.post(category_url)
        data = category_response.json()
        # 収入入力可・不可のフィルター設定
        if income_input:
            categorys = [(category["name"], category["id"]) for category in data]
        else:
            categorys = [(category["name"], category["id"]) for category in data if category["id"] != 1]
        # デフォルトカテゴリを取得する
        default_index = next((i for i, (_, cat_id) in enumerate(categorys) if cat_id == update_category_id), 0)
        selected_category_name, selected_category_id = st.selectbox(
            label="カテゴリ",
            options=categorys,
            format_func=lambda x: x[0],
            key="category",
            index=default_index # デフォルト表示
        )
        
        # 金額
        amount = st.number_input(label="金額", value=update_amount, min_value=0,)

        # メモ
        memo = st.text_area(label="メモ", value=update_memo)

        message = st.empty() # メッセージを表示する
        
        col_2_left, col_2_center, col_2_right = st.columns([1, 1, 1])    
        with col_2_left:
            pass
        with col_2_center:
            submit_update = st.form_submit_button("更新", use_container_width=True)
            if submit_update:
                if not date:
                    message.error("日付を入力してください。")
                elif not selected_category_id or selected_category_id == 0:
                    message.error("カテゴリを入力してください。")
                elif not amount:
                    message.error("金額を入力してください。")
                else:
                    submit_url = f"http://{path}:8000/api/share_account_book_item_update/"
                    submit_response = requests.post(submit_url, data={"group_id": group_id, "user_id": user_id, "shareditem_id": update_shareditem_id, "date": date, "category_id": selected_category_id, "amount": amount, "memo": memo})

                    if submit_response.status_code == 200:
                        message.success("収支を更新しました。")
                        time.sleep(1)
                        st.switch_page("pages/group_update.py")
                    else:
                        st.switch_page("pages/error.py")
        with col_2_right:
            pass
with col_3:
    pass
