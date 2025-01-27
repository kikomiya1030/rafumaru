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
year = st.session_state.get("year")
month = st.session_state.get("month")
today = st.session_state["today"]

path = st.session_state["path"]

# ユーザーがログインしてない場合
if "user_id" not in st.session_state:
    st.switch_page("pages/main.py")


col_A, col_B = st.columns([1,20])
with col_A:
    if st.button("⬅︎", key="back"):
        st.session_state["invite"] = False
        st.switch_page("pages/group_main.py")
with col_B:
    st.subheader("分割計算")


with st.container():
    col_left, col_C, col_mid, col_D, col_right = st.columns(5)
        
    category_total_url = f"http://{path}:8000/api/category_total_group/" # ローカル 
    category_total_response = requests.post(category_total_url, json={"group_id": group_id, "year": year, "month": month})
    category_total_data = category_total_response.json()

    filtered_data = category_total_data if income_input else [item for item in category_total_data if item.get("category_id") != 1]

    category_in = 0
    category_out = 0
    for item in filtered_data:
        if item["category_id"] == 1:
            category_in = item["total_amount"]
        else:
            category_out += item["total_amount"]
    
    with col_mid:
        st.write(f"**{year}年{month}月の支出**")
    with col_C:
        st.write("")
        st.write("")
        st.write(f"支出： ¥{category_out:,}")
        
    with col_D:
        st.write("")
        st.write("")
        if income_input == True:
            st.write(f"収入： ¥{category_in:,}")
        else:
            st.write("収入： 入力不可")

col1, col2, col3 = st.columns([1,4,1.3])
with col2:
    with st.form("form", clear_on_submit=False):
        url = f"http://{path}:8000/api/share_account_book/" # ローカル 
        response = requests.post(url, json={"user_id": user_id, "group_id": group_id, "year": year, "month": month, "today" : today.isoformat()})
        all_amount = response.json()
        user_data = all_amount.get("user_data", {})

        user_ids = []
        input_percentages = {}
        # パーセントのデフォルト値を取得
        user_count = len(user_data)
        default_percent = round(100 / user_count, 2) if user_count > 0 else 0.0

        for user_id, user_info in user_data.items():
            col_E, col_F = st.columns(2)
            with col_E: 
                st.write(user_info.get("nickname", "Unknown"))

            with col_F:
                percent = st.number_input("割合", key=f"input{user_id}", min_value=0.0, max_value=100.0, step=0.1, value=default_percent)
                input_percentages[str(user_id)] = percent
                user_ids.append(user_id)
            st.markdown("---")
        
        # 割合総計
        total_percentage = sum(input_percentages.values())
        st.markdown(f"**割合の合計: {total_percentage:.2f}%**")

        calculation_result = None
        message = st.empty() # 割合入力メッセージ
        col_left2, colG, left_3 = st.columns([3.8,4,1])  # ボタン設定
        with col_left2:
            st.markdown('<p style="color: red;">割合の合計は100になる必要です。</p>',unsafe_allow_html=True) 
        with colG:
            st.markdown("")
            st.markdown("")
            submit = st.form_submit_button(label="計算")
            if submit:
                if total_percentage < 100:
                    message.error("割合の合計が100未満です。")
                elif total_percentage > 100:
                    message.error("割合の合計が100を超えています。")
                else:
                    message.success("計算中...")
                    cal_url = f"http://{path}:8000/api/share_account_book_calculation/" # ローカル 
                    cal_response = requests.post(cal_url, json={"user_id": user_ids, "group_id": group_id, "year": year, "month": month, "percent": input_percentages})

                    time.sleep(1)

                    if cal_response.status_code == 200:
                        calculation_result = cal_response.json().get("data", []) # Store the result
                        message.empty()
                    else:
                        st.error("計算に失敗しました。")
    
    # 計算結果を表示する
    if calculation_result:
        st.write("**計算結果**")
        formatted_data = []
        
        for data in calculation_result:
            user_nickname = user_data.get(str(data['user_id']), {}).get("nickname", "Unknown")
            share_expense = f"¥{data['share_expense']:,}"
            
            if data['share_result'] > 0:
                result_not_enough = {"未負担額": "¥0"}
                share_result = {"余り": f"¥{data['share_result']:,}"}
            else:
                p = data['share_result']*2 - data['share_result']*2 - data['share_result']
                result_not_enough = {"未負担額": f"¥{p:,}"}
                share_result = {"余り": f"¥0"}
            
            formatted_entry = {
                "ユーザー": user_nickname,
                "支出負担額": share_expense,
                **result_not_enough,
                **share_result,
            }
            formatted_data.append(formatted_entry)
        
        st.table(formatted_data)