from datetime import datetime
import streamlit as st
import time
from streamlit_elements import elements
from streamlit_lottie import st_lottie

from pages.main_items.pie import Pie

from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

import requests
import socket
import json

set_con()
hide_header()

# ヘッダー
create_header("らふまる")

# ユーザー確認
if "user_id" not in st.session_state:
    st.switch_page("pages/main.py")

# パス設定
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# 家計簿
if st.session_state["user_id"] is not None:
    # メイン画面分割
    col_1, col_2, col_3 = st.columns([5, 5, 4])

    # ログインしているユーザーIDを取得する
    user_id = st.session_state["user_id"]
    path = st.session_state["path"]

    # 収支表示
    with col_1:
        if "month" not in st.session_state:
            st.session_state["month"] = datetime.today().month
        if "year" not in st.session_state:
            st.session_state["year"] = datetime.today().year
        if "today" not in st.session_state:
            st.session_state["today"] = datetime.today().date()
        # メインページタイトル
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            last_month = st.button("◀") # 前月
            if last_month:
                month = st.session_state["month"] - 1
                if month < 1:
                    month = 12
                    year = st.session_state["year"] - 1
                    st.session_state["year"] = year
                st.session_state["month"] = month
                st.rerun()
        with col2:
            current_year = st.session_state["year"]
            current_month = st.session_state["month"]
            st.subheader(f"{current_year}年{current_month}月の総計") # 何年何月のデータ
        with col3:
            next_month = st.button("▶") # 次月
            if next_month:
                month = st.session_state["month"] + 1
                if month > 12:
                    month = 1
                    year = st.session_state["year"] + 1
                    st.session_state["year"] = year
                st.session_state["month"] = month
                st.rerun()

        st.text("") # 空欄

        # 画面分割
        col_4, col_5 = st.columns([3,5])
        today = st.session_state["today"] # 今日の日付を取得する
        url = f"http://{path}:8000/api/account_book/" # ローカル 
        response = requests.post(url, json={"user_id": user_id, "year": current_year, "month": current_month, "today" : today.isoformat()})
        all_amount = response.json()
        with col_4:
            if datetime.today().month == st.session_state["month"] and datetime.today().year == st.session_state["year"]:
                st.text("今月")
                st.text("今週")
                st.text("今日")
            else:
                st.text("当月")
        # データベースから収支を取り出す
        with col_5:
            if datetime.today().month == st.session_state["month"] and datetime.today().year == st.session_state["year"]:
                this_monthly_amount = st.text("¥ " + f"{all_amount.get('total_month'):,}")
                this_weekly_amount = st.text("¥ " + f"{all_amount.get('total_week_today'):,}")
                this_daily_amount = st.text("¥ " + f"{all_amount.get('total_today'):,}")
            else:
                monthly_amount = st.text("¥" + f"{all_amount.get('total_month'):,}")

    # グラフ
    with col_2:
        with elements("dashboard"):
            # APIリクエストでカテゴリーデータを取得
            category_total_url = f"http://{path}:8000/api/category_total/"  # ローカル
            category_total_response = requests.post(category_total_url, json={"user_id": user_id, "year": current_year, "month": current_month, "week": None})
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
                pie.create_chart(data, unique_key="unique_key", height=300)

        col_6, col_7, col_8 = st.columns([6, 3, 5]) # ボタンの位置設定
        with col_7 :
            # 詳細画面に遷移
            if sum(item_list) == 0:
                pass
            else:
                if st.button("詳細"):
                    st.session_state["calendar"] = False
                    st.switch_page("pages/account_book_detail.py") 

    # 収支入力フォーム
    with col_3:
        with st.form("form", clear_on_submit=True):
            st.subheader("入力欄")
            # 日付入力
            date = st.date_input('日付', value="today")
            # 金額入力
            amount = st.number_input('金額', value=None, min_value=0, max_value=1500000000, step=1)
            st.markdown("""
                <style>
                .stNumberInput > div > div > button {
                    display: none;
                }
                </style>
            """, unsafe_allow_html=True)

            # カテゴリセレクトボックス
            path = st.session_state["path"]
            url = f"http://{path}:8000/api/get_category/" # ローカル       
            response = requests.post(url)
            data = response.json()
            categorys =  [(category["name"], category["id"]) for category in data]
            selected_category_name, selected_category_id = st.selectbox(
                label="カテゴリ",
                options=categorys,
                format_func=lambda x: x[0],
                key="category"
            )
            # メモ入力
            memo = st.text_area('メモ', value=None, max_chars=200)

            # メッセージ
            message = st.empty()

            # 登録ボタン
            submit = st.form_submit_button(label="登録")

            # エラー確認
            if submit:
                if date == None:
                    message.error("日付を入力してください。")
                elif amount == None:
                    message.error("金額を入力してください。")
                elif amount > 1500000000:
                    message.error("最大15億円まで入力可能です。")
                elif selected_category_id is None:
                    message.error("カテゴリを入力してください。")
                elif memo:
                    if memo > 200:
                        message.error("200文字まで入力可能です。")
                else: # 登録
                    message.empty() # エラーメッセージがあれば消す
                    url = f"http://{path}:8000/api/account_book_input/" # ローカル 
                    response = requests.post(url, data={"user_id": user_id, "date": date.isoformat(), "amount": amount, "category_id": selected_category_id, "memo": memo})
                    if response.status_code == 200:
                        message.success("収支を登録しました。")
                        time.sleep(1)
                        st.switch_page("pages/main.py")
                    elif response.status_code == 400:
                        st.switch_page("error.py")

# 紹介
else:
    col_left, col_mid, col_right = st.columns([2,10,2])
    with col_mid:
        st.subheader("**About Rafumaru...**")
        with st.container(border=True):
            colA, colB = st.columns([1, 3])
            def load_lottie_local(filepath: str):
                with open(filepath, "r") as f:
                    return json.load(f)
            with colA:
                lottie_json_1 = load_lottie_local("json/buta.json")
                if lottie_json_1:
                    st_lottie(lottie_json_1, speed=1, key="lottie_animation_1")
            with colB:
                st.subheader("個人家計簿")
                st.write("家計簿は、収入と支出をまとめた帳簿で、お金の使い方の傾向を把握したり、節約すべき項目を洗い出したりすることができます。")
                st.write("定期的に家計簿を確認することで、貯金ができるようになったり節約を意識できるようになったりします。")

        with st.container(border=True):
            colC, colD = st.columns([1, 3])
            with colC:
                lottie_json_1 = load_lottie_local("json/share.json")
                if lottie_json_1:
                    st_lottie(lottie_json_1, speed=1, key="lottie_animation_2")
            with colD:
                st.subheader("公開")
                st.write("他のユーザーの共有データを参考にして、自分の生活プランを立てることできます。")
                st.write("コメントを使用し、他のユーザーと交流することができます。")

        with st.container(border=True):
            colE, colF = st.columns([1, 3])
            with colE:
                st.image("images/pic3.png", use_column_width=True)
            with colF:
                st.subheader("共同家計簿")
                st.write("家族や夫婦、カップルなど複数人数で家計簿を管理したい人にぴったりの共有できます。")
                st.write("家計を管理する以外にも、グループ行動など費用を分担する必要の時も使えます。")