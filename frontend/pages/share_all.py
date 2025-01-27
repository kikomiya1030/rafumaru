import streamlit as st
import socket
import requests

from datetime import datetime
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

if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# ユーザー確認
user_id = st.session_state["user_id"]
path = st.session_state["path"]
if st.session_state["user_id"] == None:
    st.switch_page("pages/main.py")

url = st.session_state["path"]

colA, colB, colC, colD = st.columns([1, 4.5, 3, 8])
col_1, col_2, col_3 = st.columns([9, 1, 4])

with col_1:
    url = f"http://{path}:8000/api/public_all_contents/"  # ローカル
    if st.session_state["myself"]:
        user = user_id
    else:
        user = None

    if st.session_state["show_calendar"]:
        selected_date = st.session_state["selected_date"]
        selected_date = selected_date.strftime('%Y-%m-%d')
    else:
        selected_date = None

    response = requests.post(url, json={"user_id": user, "selected_date": selected_date})
    weekly_data = response.json()

    
    if not weekly_data or len(weekly_data) == 0:
        st.markdown('データが存在してません')
    else:
        st.header('公開中！')
        st.write('あなたの周りの人は、どんな生活していますか？')

        number = 1
        for key, entries in weekly_data.items():
            for entry in entries:
                user = entry.get("user_id", "Unknown")
                st.session_state["check_user"] = user
                nickname = entry.get("nickname", "Unknown")
                title = entry.get("title", "No Title")
                st.session_state["check_title"] = title
                year = entry.get("year", "")
                st.session_state["check_year"] = year
                month = entry.get("month", "")
                st.session_state["check_month"] = month
                week = entry.get("week", "")
                st.session_state["check_week"] = week
                public_no = entry.get("public_no", "")
                st.session_state["check_public_no"] = public_no
                unique_key = f"{user}-{year}-{month}-{week}"
                st.session_state["check_unique_key"] = unique_key

                if week == 1:
                    week_date = "1日～7日"
                elif week == 2:
                    week_date = "8日～14日"
                elif week == 3:
                    week_date = "15日～21日"
                elif week == 4:
                    week_date = "22日～28日"
                else:
                    week_date = "29日～"

                col_left, col_right = st.columns(2)

                with col_left:
                    # 表示
                    st.write('')
                    st.write('')
                    st.write('')
                    st.write('')
                    st.subheader(f"{number}. {title}")
                    st.markdown(f"日付： {year}年{month}月{week_date}")
                    st.markdown(f"ユーザー： {nickname}")
                    number += 1
                    
                with col_right:
                    with st.container():
                        # APIリクエストでカテゴリーデータを取得
                        category_total_url = f"http://{path}:8000/api/category_total/"  # ローカル
                        category_total_response = requests.post(category_total_url, json={"user_id": user, "year": year, "month": month, "week": week})
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
                            pie.create_chart(data, unique_key=unique_key,height=250)
                col_A, col_B, col_C = st.columns([12.5, 2, 3]) # ボタンの位置設定
                with col_B :
                    if st.button("詳細", key=unique_key):
                        st.switch_page("pages/share_all_comment.py")
                st.markdown('---')  


with col_3:
    if st.button("公開情報", use_container_width=True):
        st.switch_page("pages/share_all_public_open.py")

    with st.form("form"):
        st.subheader("条件検索")

        # カレンダーを選択する
        if "show_calendar" not in st.session_state: # 初期値
                st.session_state["show_calendar"] = False

        if st.form_submit_button("カレンダーを表示", use_container_width=True):
            if st.session_state.get("show_calendar", False):
                st.session_state["show_calendar"] = False
            else:
                st.session_state["show_calendar"] = True

        if st.session_state.get("show_calendar", False):
            selected_date = st.date_input("日付を選択してください")   
            st.session_state["selected_date"] = selected_date     
        

        # 自分の投稿を選択する
        if "myself" not in st.session_state:  # 初期値
            st.session_state["myself"] = False

        # 自分の投稿絞り込みボタン     
        if st.checkbox("自分の投稿絞り込み"):
            st.session_state["myself"] = True
        else:
            st.session_state["myself"] = False

        # フォーム完了設定
        submit = st.form_submit_button("OK", use_container_width=True)
        if submit:
            st.switch_page("pages/share_all.py")