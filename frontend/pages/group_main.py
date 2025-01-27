from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import socket
import time

from streamlit_elements import elements
from pages.main_items.pie import Pie
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con


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

# ユーザーがログインしてない場合
if "user_id" not in st.session_state:
    st.switch_page("pages/main.py")

# ユーザーID、グループIDを取得する
user_id = st.session_state["user_id"]
group_id = st.session_state['group_id']
group_name = st.session_state['group_name']
income_input = st.session_state['income_input']

path = st.session_state["path"]


if "user" in st.session_state:
    col_left, col_right = st.columns([10,4])
    with col_left:
        st.subheader(group_name) 
        st.caption("収入入力可" if income_input else "収入入力不可")
    # 友達招待欄
    with col_right:
        if st.button("ユーザー招待", use_container_width=True):
            st.session_state["invite"] = True
        
        if st.session_state["invite"]:
            msg = st.empty()
            col_left1, col_right1 = st.columns([8,2])
            with col_left1:
                # 受信ユーザーを入力する
                re_user_id = st.text_input("ユーザーID") 
            with col_right1:
                st.caption("")
                st.caption("")
                if st.button("送信", key="notice_submit"):
                    status = "group_invite"
                    notice_url = f"http://{path}:8000/api/notice_input/" # ローカル 
                    notice_response = requests.post(notice_url, json={"user_id": user_id, "re_user_id": re_user_id, "group_id": group_id, "status": status})
                    notice_response_data = notice_response.json()
                    if notice_response.status_code == 200:
                        msg.success("招待を送信しました！")
                        time.sleep(1)
                        st.session_state["invite"] = False
                        st.switch_page("pages/group_main.py")
                        
                    else:
                        msg.error("送信失敗しました。")
        

    # メイン画面分割
    col_1, col_2, col_3 = st.columns([5, 5, 4])

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
                st.session_state["invite"] = False
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
                st.session_state["invite"] = False
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
        url = f"http://{path}:8000/api/share_account_book/" # ローカル 
        response = requests.post(url, json={"user_id": user_id, "group_id": group_id, "year": current_year, "month": current_month, "today" : today.isoformat()})
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
                category_total_url = f"http://{path}:8000/api/category_total_group/"  # ローカル
                category_total_response = requests.post(category_total_url, json={"group_id": group_id, "year": current_year, "month": current_month})
                category_total_data = category_total_response.json()
                data = {}
                for item in category_total_data:
                    category_id = item.get("category_id", "Unknown")
                    category_name = item.get("category_name", "Unknown")
                    total_amount = item.get("total_amount", 0)
                    if category_id != 1: # 収入(category_id=1)以外のデータをリストに保存する
                        data[category_name] = total_amount
                    
                # Pie インスタンスを作成してグラフを表示
                pie = Pie()
                pie.create_chart(data)
    
            col_6, col_7, col_8 = st.columns([6, 3, 5]) # ボタンの位置設定
            with col_7 :
            # 詳細画面に遷移
                if st.button("詳細"):
                    st.switch_page("pages/group_detail.py") 

        # 収支入力欄
        with col_3:
            with st.form("form", clear_on_submit=True):
                st.subheader("入力欄")
                date = st.date_input('日付', value="today") # 日付
                amount = st.number_input('金額', value=None, min_value=0, step=1) # 金額
                st.markdown("""
                    <style>
                    .stNumberInput > div > div > button {
                        display: none;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # カテゴリ取得
                path = st.session_state["path"]
                url = f"http://{path}:8000/api/get_category/" # ローカル       
                response = requests.post(url)
                data = response.json()
                # 収入入力可・不可のフィルター設定
                if income_input:
                    categorys = [(category["name"], category["id"]) for category in data]
                else:
                    categorys = [(category["name"], category["id"]) for category in data if category["id"] != 1]
                selected_category_name, selected_category_id = st.selectbox(
                    label="カテゴリ",
                    options=categorys,
                    format_func=lambda x: x[0],
                    key="category",
                )
                
                # メモ
                memo = st.text_area('メモ', value=None)

                # メッセージ
                message = st.empty()

                # 登録ボタン
                submit = st.form_submit_button(label="登録")

                # エラー確認
                if submit:
                    if date == None:
                        message.error("日付を入力してください")
                    elif amount == None:
                        message.error("金額を入力してください")
                    elif amount > 1500000000:
                        message.error("最大15億円まで入力可能です。")
                    elif selected_category_id is None:
                        message.error("カテゴリを入力してください")
                    else: # 登録
                        message.empty() # エラーメッセージがあれば消す
                        url = f"http://{path}:8000/api/share_account_book_input/" # ローカル 
                        response = requests.post(url, data={"user_id": user_id, "group_id": group_id, "date": date.isoformat(), "amount": amount, "category_id": selected_category_id, "memo": memo})
                        if response.status_code == 200:
                            message.success("収支を登録しました。")
                            time.sleep(1)
                            st.switch_page("pages/group_main.py")
                        elif response.status_code == 400:
                            st.switch_page("error.py")
        st.text("")
        st.text("")
        
    st.markdown("---")
    colA,colB = st.columns([1,4])

    with colA:
        st.subheader(f"{st.session_state['month']}月の個人状況")  # 何月のデータ
            
        st.text("") # 空欄
    with colB:
        if st.button("分割計算"):
            st.switch_page("pages/group_calculation.py")

    colC, colD = st.columns([4, 2])

    with colC:
        # 円マークを設定
        def en_mark(defo_en):
            """Format numbers with a yen symbol."""
            new_list = [f"¥{i:,}" for i in defo_en]
            return new_list
        
        user_data = all_amount.get("user_data", {})
        users = []
        income = []
        expense = []
        total = []

        # データを取り出す
        for user_id, user_info in user_data.items():
            users.append(user_info.get("nickname", "Unknown"))  # ユーザーのニックネーム
            income.append(user_info.get("total_income", 0))  # 収入
            expense.append(user_info.get("total_expense", 0))  # 支出
            total.append(user_info.get("total_month", 0)) # 総計

        income = en_mark(income)
        expense = en_mark(expense)
        total = en_mark(total)

        # 収入入力可・不可のフィルター設定
        if income_input:
            data = {
            "ユーザー": users,
            "収入": income,
            "支出": expense,
            "収支": total,
            }
        else:
            data = {
            "ユーザー": users,
            "支出": expense,
            }

        # DataFrame に変換
        df = pd.DataFrame(data)
        st.table(df)
        
    with colD:
        pass
    
else:
    st.switch_page("pages/main.py")