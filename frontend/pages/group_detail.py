import datetime
import streamlit as st
import streamlit_calendar as st_calendar
import socket
import random

from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import requests

from calendar import isleap # うるう年判定モジュール

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

# 最初のアクセスする時、現在の日付を取得
if "year" not in st.session_state:
    st.session_state["year"] = datetime.today().year
if "month" not in st.session_state:
    st.session_state["month"] = datetime.today().month
if "today" not in st.session_state:
    st.session_state["today"] = datetime.today().date()
if "filter" not in st.session_state:
    st.session_state["filter"] = False
if "gp_calendar" not in st.session_state:
    st.session_state["gp_calendar"] = False

# セッション確認
session_list = ["path", "group_id", "group_name", "income_input", "year", "month", "today"]
if any(session not in st.session_state for session in session_list):
    st.switch_page("pages/main.py")
    st.stop()

# セッションからデータを取り出す
user_id = st.session_state["user_id"]
path = st.session_state["path"]

group_id = st.session_state["group_id"]
group_name = st.session_state["group_name"]
year = st.session_state["year"]
month = st.session_state["month"]
income_input = st.session_state["income_input"]


# ランダムカラー
def get_random_color():
    colors = [
        "#66FFFF", # akiyama
        "#6666FF", # nozawa
        "#33FF99", # sotokawa
        "#FF9999",
        "#FFCC00",
        "#66CC66",
        "#6699FF",
        "#FF66CC",
        "#FF6600",
        "#9966FF",
        "#CCCCCC",
        "#FFCCFF",
        
    ]
    return random.choice(colors)

col_A, col_B = st.columns([1,20])
with col_A:
    if st.button("⬅︎", key="back"):
        st.session_state["filter"] = False
        st.session_state["invite"] = False
        st.session_state["gp_calendar"] = False
        st.session_state["chat_box"] = False
        st.switch_page("pages/group_main.py")
with col_B:
    st.subheader(group_name) 

# ページタイトル
colA, colB, colC, colC2, colD1, colD2, colD3 = st.columns([1, 4.5, 0.8, 3, 5.5, 1, 1.5])
with colA:
    last_month = st.button("◀") # 前月
    if last_month:
        st.session_state["filter"] = False
        month = st.session_state["month"] - 1
        if month < 1:
            month = 12
            year = st.session_state["year"] - 1
            st.session_state["year"] = year
        st.session_state["month"] = month
        st.rerun()

with colB:
    current_year = st.session_state["year"]
    current_month = st.session_state["month"]
    st.subheader(f"{current_year}年{current_month}月の使用状況") # 何年何月のデータ

with colC:
    next_month = st.button("▶") # 次月
    if next_month:
        st.session_state["filter"] = False
        month = st.session_state["month"] + 1
        if month > 12:
            month = 1
            year = st.session_state["year"] + 1
            st.session_state["year"] = year
        st.session_state["month"] = month
        st.rerun()

# カレンダーボタン
with colC2:
    gp_calendar_btn = st.button("📅")
    if gp_calendar_btn and st.session_state["gp_calendar"] == True:
        st.session_state["gp_calendar"] = False
        st.switch_page("pages/group_detail.py")
    elif gp_calendar_btn and st.session_state["gp_calendar"] == False:
        st.session_state["gp_calendar"] = True
        st.switch_page("pages/group_detail.py")
    else:
        pass

# 検索欄
with colD1:
    date_search = st.date_input('日付から詳細検索', value=st.session_state["today"])
with colD2:
    st.write("")
    st.write("")
    date_button = st.button('検索')
    if date_button:
        st.session_state["filter"] = True
        st.session_state["year"] = date_search.year
        st.session_state["month"] = date_search.month
        
with colD3:
    st.write("")
    st.write("")
    close_button = st.button('クリア')
    if close_button:
        st.session_state["filter"] = False
        st.session_state["gp_calendar"] = False


# メイン画面分割
col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 3, 3, 3, 3, 3, 4])

url = f"http://{path}:8000/api/share_account_book_detail/" # ローカル 
response = requests.post(url, json={"group_id": group_id, "user_id": user_id, "year": current_year, "month": current_month, "date": date_search.isoformat() if st.session_state.get("filter") else None})
data = response.json()
weekly_data = data.get('weekly_data', {})
weekly_totals = data.get('weekly_totals', {})

# カレンダー用カラー設定
if "random_colors" not in st.session_state:
    st.session_state["random_colors"] = {}

    for week_num in weekly_data:
        for item in weekly_data[week_num]:
            st.session_state["random_colors"][item["date"]] = get_random_color()

# 週の詳細表示
cols = [col2, col3, col4, col5, col6]

if st.session_state["filter"]:
    if response.status_code == 200:
        col2, col3, col4, col5, col6, col7 = st.columns([5, 0.1, 0.1, 0.1, 0.1, 0.1])
        with col2:
            st.write(f"**検索結果**：{date_search}")
            for week_num in range(1, 6):
                with st.container(border=True):
                    # データ表示ループ
                    if str(week_num) in weekly_data:
                        # 日付順番調整
                        sorted_week_data = sorted(
                        weekly_data[str(week_num)], key=lambda item: item.get('date'))
                        item_no_print=1
                        for item in weekly_data[str(week_num)]:
                            st.caption(f"データ{item_no_print}")
                            item_no_print+=1
                            st.write(item.get('nickname'))
                            st.write(f"{item.get('category_name')}")
                            st.write(f"¥{item.get('amount'):,}")
                            if item.get('memo'):
                                st.markdown('--')
                                st.caption('メモ')
                                st.write(f"{item.get('memo')}")
                            st.markdown('---')
                        st.caption(f"**{date_search.isoformat()}**")

# カレンダー表示画面
elif st.session_state["gp_calendar"]:
    col2, col3, col4 = st.columns([1,10,1])
    with col3:
        # カレンダーの設定
        selected_date = datetime.date(st.session_state["year"], st.session_state["month"], 1)     
        events = []

        for week_num in weekly_data:
            for item in weekly_data[week_num]:
                event = {
                    "title": f"{item.get('nickname')}：{item.get('category_name')}　¥{item.get('amount'):,}",
                    "start": item.get('date'),
                    "backgroundColor": st.session_state["random_colors"].get(item["date"], "#66CC66"),
                }
                events.append(event)
        
        options={
            "initialDate": selected_date.isoformat(),
            'locale': 'ja', # 日本語に変更
            "headerToolbar": False, # 日付選択ボタンの表示を取り消す
            "editable": False,
            "events": events,
            "dayMaxEventRows": 3,
            "contentHeight": "auto",
            }
        
        st_calendar.calendar(options=options)

else:
    if response.status_code == 200:
        col2, col3, col4, col5, col6 = st.columns([3, 3, 3, 3, 3])
        try:
            # 週1から週5のループ
            day1 = 1
            day2 = 7
            for week_num in range(1, 6):
                col = cols[week_num - 1]
                with col:
                    with st.container(border=True):
                        if int(current_month) == 2:
                            if isleap(current_year) == False and week_num == 5:
                                pass
                            else:
                                if day1 <= 28:
                                    st.write(f"**{day1}日～{day2}日**")
                                    day1 += 7
                                    day2 += 7
                                    st.markdown('---')
                                else:
                                    st.write("**29日～**")
                                    st.markdown('---')
                                    
                                # データ表示ループ
                                if str(week_num) in weekly_data:
                                    for item in weekly_data[str(week_num)]:
                                        st.write(f"{item.get('date')}")
                                        st.write(f"{item.get('nickname')}")
                                        st.write(f"{item.get('category_name')}")
                                        st.write(f"¥{item.get('amount'):,}")
                                        st.markdown('---')

                                # 週総計
                                weekly_total = weekly_totals.get(str(week_num), 0)
                                st.text(f"小計: ¥{weekly_total:,}")

                                # 更新ボタン
                                if st.button(f"更新", key=f"week_button{week_num}", use_container_width=True):
                                    # 当週のデータをセッションに保存して、画面を遷移する
                                    st.session_state['update_week'] = week_num
                                    st.session_state['update_year'] = current_year
                                    st.session_state['update_month'] = current_month
                                    st.switch_page("pages/group_update.py")
                        else: 
                            if day1 <= 28:
                                st.write(f"**{day1}日～{day2}日**")
                                day1 += 7
                                day2 += 7
                                st.markdown('---')
                            else:
                                st.write("**29日～**")
                                st.markdown('---')
                                
                            # データ表示ループ
                            if str(week_num) in weekly_data:
                                for item in weekly_data[str(week_num)]:
                                    st.write(f"{item.get('date')}")
                                    st.write(f"{item.get('nickname')}")
                                    st.write(f"{item.get('category_name')}")
                                    st.write(f"¥{item.get('amount'):,}")
                                    st.markdown('---')

                            # 週総計
                            weekly_total = weekly_totals.get(str(week_num), 0)
                            st.text(f"小計: ¥{weekly_total:,}")

                            # 更新ボタン
                            if st.button(f"更新", key=f"week_button{week_num}", use_container_width=True):
                                # 当週のデータをセッションに保存して、画面を遷移する
                                st.session_state['update_week'] = week_num
                                st.session_state['update_year'] = current_year
                                st.session_state['update_month'] = current_month
                                st.switch_page("pages/group_update.py")

        except ValueError as e:
            st.switch_page("error.py")
    else:
        st.switch_page("error.py")

    # 当月のカテゴリ別の収支表示
    with col7:
        category_total_url = f"http://{path}:8000/api/category_total_group/" # ローカル 
        category_total_response = requests.post(category_total_url, json={"group_id": group_id, "year": current_year, "month": current_month})
        category_total_data = category_total_response.json()

        today = st.session_state["today"] # 今日の日付を取得する
        gp_url = f"http://{path}:8000/api/share_account_book/" # ローカル 
        gp_response = requests.post(gp_url, json={"user_id": user_id, "group_id": group_id, "year": current_year, "month": current_month, "today" : today.isoformat()})
        all_amount = gp_response.json()

        with st.container(border=True):
            st.write("**カテゴリ別の収支**")
            st.markdown('---')

            # 収入入力可・不可設定による、収入(category_id=1)を表示するかどうか
            filtered_data = category_total_data if income_input else [
                    item for item in category_total_data if item.get("category_id") != 1
                ]
            
            table_html = """
            <style>
                .custom-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .custom-table td {
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

            for item in filtered_data:
                category_name = item.get("category_name", "Unknown")
                total_amount = f"¥{item.get('total_amount', 0):,}"
                table_html += f"<tr><td>{category_name}</td><td>{total_amount}</td></tr>"

            table_html += """<tr class="separator-row"><td colspan="2"><hr/></td></tr>"""

            # 総計
            total_monthly = f"¥{all_amount.get('total_month'):,}"
            table_html += f"""<tr><td><strong>総計</strong></td><td><strong>{total_monthly}</strong></td></tr>"""
            
            table_html += "</table></div>"

            st.markdown(table_html, unsafe_allow_html=True)