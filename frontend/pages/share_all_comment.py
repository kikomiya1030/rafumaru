import streamlit as st
import socket
import requests
import time

from streamlit.components.v1 import html
 
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

from streamlit_elements import elements
from pages.main_items.pie import Pie


set_con()
 
hide_header()
 
# ヘッダー
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
session_list = ["path", "check_user", "check_title", "check_year", "check_month", "check_week", "check_public_no", "check_unique_key"]
if any(session not in st.session_state for session in session_list):
    st.switch_page("pages/main.py")
    st.stop()

# セッションからデータを取り出す
user_id = st.session_state["user_id"]
path = st.session_state["path"]

check_user = st.session_state["check_user"]
check_title = st.session_state["check_title"]
check_year = st.session_state["check_year"]
check_month = st.session_state["check_month"]
check_week = st.session_state["check_week"]
check_public_no = st.session_state["check_public_no"]
check_unique_key = st.session_state["check_unique_key"] + "-1"

col_A, col_B = st.columns([1,20])
with col_A:
    if st.button("⬅︎", key="back"):
        st.switch_page("pages/share_all.py")
    if st.button("🔃"):
        st.switch_page("pages/share_all_comment.py")
with col_B:
    st.subheader(check_title)


col_left, col_mid, col_mid2, col_right = st.columns([1,4,4,1])
with col_mid:
    with st.container():
        # APIリクエストでカテゴリーデータを取得
        category_total_url = f"http://{path}:8000/api/category_total/"  # ローカル
        category_total_response = requests.post(category_total_url, json={"user_id": check_user, "year": check_year, "month": check_month, "week": check_week})
        category_total_data = category_total_response.json()
        data = {}
        for item in category_total_data:
            category_id = item.get("category_id", "Unknown")
            category_name = item.get("category_name", "Unknown")
            total_amount = item.get("total_amount", 0)
            if category_id != 1: # 収入(category_id=1)以外のデータをリストに保存する
                data[category_name] = total_amount
        item_list = list(data.values())
        if sum(item_list) == 0:
            st.write("支出登録をするとグラフが表示されます")
        else:
            # Pie インスタンスを作成してグラフを表示
            pie = Pie()
            pie.create_chart(data, unique_key=check_unique_key, height=450)
            
    with col_mid2:
        with st.container():
            st.write("")
            st.write("")
            st.write("**カテゴリ別の収支**")
            st.markdown('---')

            table_html = """
            <style>
                .custom-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .custom-table td, .custom-table th {
                    padding: 8px;
                    text-align: left;
                    border: none !important;
                }

                .custom-table tr {
                    border: none !important;
                }

            </style>
            <div class="outer-container">
                <table class="custom-table">
            """

            for item in category_total_data:
                if item["category_id"] != 1:
                    category_name = item.get("category_name", "Unknown")
                    total_amount = f"¥{item.get('total_amount', 0):,}"
                    table_html += f"<tr><td>{category_name}</td><td>{total_amount}</td></tr>"

            table_html += "</table></div>"

            st.markdown(table_html, unsafe_allow_html=True)

# コメント入力欄
col_1, col_2, col_3, col_4 = st.columns([2,10,4,3])
with col_2:
    comment = st.text_input('コメント入力', key="comment")
    message = st.empty()
    st.markdown('---')
with col_3:
    st.write("")
    st.write("")

    # NGリスト
    NG_WORDS = [
        "死ね", "しね", "シネ", "4ね", "４ね", "馬鹿", "ばか", "baka", "バカ", "あほ", "アホ", 
        "きえろ", "消えろ", "キエロ", "ボケ", "ぼけ", "まぬけ", "間抜け", "aho", "kiero", 
        "boke", "manuke", "くそ", "糞", "クソ", "kuso", "がき", "ガキ", "餓鬼", "gaki", "ぶす", 
        "ブス", "busu", "殺す", "ころす", "コロス", "korosu", "かす", "カス", "stupid", 
        "fuck", "きも", "キモ"
    ]
    
    # NG確認
    def contains_ng_word(text):
        temp_text = text.replace("ー", "")  # Remove all "ー"
        for word in NG_WORDS:
            if word in temp_text:
                return True
        return False
    
    if st.button("Ok", key="submit", use_container_width=True):
        if len(comment) > 100:
            message.error("コメントは100文字以下になります。")
        elif contains_ng_word(comment):
            message.error("不適切な言葉が含まれています。")
        elif len(comment) > 0:
            comment_url = f"http://{path}:8000/api/public_comment_input/"  # ローカル
            comment_response = requests.post(comment_url, json={"user_id": user_id, "comment": comment, "public_no": check_public_no})
            if comment_response.status_code == 200:
                message.success("コメントしました。")
                time.sleep(1)
                st.switch_page("pages/share_all_comment.py")
            elif comment_response.status_code == 400:
                st.switch_page("error.py")
        else:
            message.error("コメントを入力してください。")


# コメント参照、削除
comment_check_url = f"http://{path}:8000/api/public_comment_detail/"  # ローカル
comment_check_response = requests.post(comment_check_url, json={"public_no": check_public_no})

if comment_check_response.status_code == 200:
    all_comment_data = comment_check_response.json()
    all_comment_data = all_comment_data[::-1]
    if not isinstance(all_comment_data, list):
        st.write("コメントがありません。")
    else:
        for cm in all_comment_data:
            comment_id = cm["comment_id"]
            nickname = cm["nickname"]
            comment_text = cm["comment"]
            like_point = cm["like_point"]
            comment_user_id = cm["user_id"]

            col_6, col_7, col_8, col_9, col_10, col_11 = st.columns([2,10,1,1,2,3])
            with col_7:
                st.write(f'{nickname}: {comment_text}')
                msg = st.empty()
            with col_8:
                if st.button("♥", key=f"like_btn_{comment_id}"):
                    like_url = f"http://{path}:8000/api/public_like/"
                    response = requests.post(like_url, json={"comment_id": comment_id})
                    if response.status_code == 200:
                        st.switch_page("pages/share_all_comment.py")
                    else:
                        msg.error("エラー")
            with col_9:
                st.markdown(f"{like_point}")
            with col_10:
                if comment_user_id == user_id:
                    if st.button("削除", key=f"delete_btn_{comment_id}", use_container_width=True):
                        delete_url = f"http://{path}:8000/api/public_comment_delete/"
                        response = requests.post(delete_url, json={"comment_id": comment_id})
                        if response.status_code == 200:
                            msg.success("コメントを削除しました。")
                            time.sleep(1)
                            st.switch_page("pages/share_all_comment.py")
                        else:
                            msg.error("削除に失敗しました。")
else:
    st.error("コメントデータの取得に失敗しました。")