import streamlit as st  
import datetime
import socket
import requests
import time

from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con

set_con()

hide_header()

# ヘッダー
create_header("らふまる")

user_id = st.session_state["user_id"]

# パス設定
if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

# ユーザーがログインしてない場合
if "user" not in st.session_state:
    st.switch_page("pages/main.py")

# ログインしているユーザーIDを取得する
user_id = st.session_state["user"].user_id
path = st.session_state["path"]

colA, colB = st.columns([1,20])
with colA:
    if st.button("⬅︎", key="back"):
        st.switch_page("pages/share_all.py")
with colB:
    st.subheader("公開情報設定")

# メイン画面分割
col_1, col_2, col_3 = st.columns([5, 5, 4])

# 日付設定
with col_1:
    if "month" not in st.session_state:
        st.session_state["month"] = datetime.today().month
    if "year" not in st.session_state:
        st.session_state["year"] = datetime.today().year
    if "today" not in st.session_state:
        st.session_state["today"] = datetime.today().date()

    
    # 日付変更設定
    col_1, col_2, col_3 = st.columns([0.5, 1.3, 1.1])
    with col_1:
        last_month = st.button("◀") # 前月
        if last_month:
            month = st.session_state["month"] - 1
            if month < 1:
                month = 12
                year = st.session_state["year"] - 1
                st.session_state["year"] = year
            st.session_state["month"] = month
            st.rerun()
    with col_2:
        current_year = st.session_state["year"]
        current_month = st.session_state["month"]
        st.subheader(f"{current_year}年{current_month}月") # 何年何月のデータ
    with col_3:
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


# 各週の処理
weeks_data = []
has_valid_data = False # ボタン表示設定

with st.container(border=True):
    cola, colb, colc = st.columns([1,2,3])
    with cola:
        st.write("公開状態")
    with colb:
        st.write("データ")
    
    st.markdown("---")

    day1 = 1
    day2 = 7
    for week_num in range(1, 6):
        col_left, col_mid, col_right = st.columns([1, 2, 3])
        week_entry = {"week": week_num, "public": False, "title": ""}

        public_status_url = f"http://{path}:8000/api/public_status/"
        public_status_response = requests.post(public_status_url, json={"user_id": user_id, "year": current_year, "month": current_month, "week": week_num})
        status = public_status_response.json()
        public_status = status.get("status", "Error")
        title = status.get("title", "")
        public = status.get("public", False)
        
        # 公開状態確認
        with col_left:
            # line-heightで文字上下を設定する
            # データあり
            if public_status_response.status_code == 200:
                st.markdown(
                    f"""
                    <div style="display: flex; line-height: 43px; height: 100%; font-size: 16px;">
                        {public_status}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            # エラー
            else:
                st.markdown(
                    f"""
                    <div style="display: flex; line-height: 43px; height: 100%; font-size: 16px;">
                        エラー
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # 公開状態設定のチェックボックス
        with col_mid:
            if public_status == "データなし":
                if day2 <= 28:
                    st.write(f"{current_month}月{day1}日～{day2}日")
                else:
                    st.write(f"{current_month}月29日～")
            else:
                has_valid_data = True
                if day2 <= 28:
                    public = st.checkbox(label=f"{current_month}月{day1}日～{day2}日", key=f"public{week_num}", value=public)
                else:
                    public = st.checkbox(label=f"{current_month}月29日～", key=f"public{week_num}", value=public)
                week_entry["public"] = public
            day1+=7
            day2+=7

        # チェックされた場合、右側にタイトル入力欄を表示
        with col_right:
            if public:
                title_input = st.text_input('タイトル入力', key=f"input{week_num}", value=title)
                week_entry["title"] = title_input
        # データをリストに追加
        weeks_data.append(week_entry)

        if week_num < 5:
            st.markdown("---")

message = st.empty()
if has_valid_data:
    button_col1, button_col2, button_col3 = st.columns([0.1, 1, 3])
    with button_col2:  
        if st.button("OK"):
            public_url = f"http://{path}:8000/api/public_setting/"
            for entry in weeks_data:
                response = requests.post(public_url,
                    json={
                        "user_id": user_id,
                        "year": current_year,
                        "month": current_month,
                        "week": entry["week"],
                        "public": "true" if entry["public"] else "false",
                        "title": entry["title"],
                    }
                )
            if response.status_code == 200:
                message.success('公開状態を更新しました！')
                time.sleep(1)
                st.switch_page("pages/share_all_public_open.py")
            else:
                st.switch_page("pages/error.py")
else:
    message.info("公開可能なデータがありません。")