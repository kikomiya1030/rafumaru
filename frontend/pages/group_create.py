import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con
import requests
import time

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

# ユーザーがログインしてない場合
if "user_id" not in st.session_state:
    st.switch_page("pages/main.py")

# ログインしているユーザーIDを取得する
user_id = st.session_state["user_id"]
path = st.session_state["path"]

colA, colB = st.columns([1,20])
with colA:
    if st.button("⬅︎"):
        st.switch_page("pages/group.py")
with colB:
    st.subheader("グループ作成")

col_1, col_2, col_3 = st.columns([1, 2, 1])
with col_1:
    pass
with col_2:
    with st.form(key="group_create"):
        # グループ名前設定
        group_name = st.text_input("グループ名")
        # パスワード設定
        group_password = st.text_input("パスワード", type="password")
        st.text("パスワードは8桁以上16桁以下で入力してください。")
        # 収入入力設定
        allow_income_input = st.checkbox("収入入力可")
        input_income = 1 if allow_income_input else 0 # チェックする場合 True
        

        # バリデーション用のフラグ
        is_valid = True
        message = st.empty()
        error_messages = []
        error_msg = st.empty()

        # ボタンの配置
        col_2_left, col_2_center, col_2_right = st.columns([1, 1, 1])
        with col_2_left:
            pass
        with col_2_center:
            submit_create = st.form_submit_button("作成", use_container_width=True)
            if submit_create:
                # 入力チェック
                if not group_name:
                    is_valid = False
                    error_messages.append("グループ名を入力してください。")
                if not group_password:
                    is_valid = False
                    error_messages.append("パスワードを入力してください。")
                elif (len(group_password) < 8 or len(group_password) > 16):
                    error_msg.error("パスワードは8桁以上16桁以下で入力してください。")
                else:
                    create_url = f"http://{path}:8000/api/group_create/"
                    create_response = requests.post(create_url, data={"user_id": user_id, "group_name": group_name, "group_password": group_password, "income_input": input_income})
                    # バリデーション成功時
                    if create_response.status_code == 200:
                        message.success("グループを作成しました。")
                        time.sleep(1)
                        st.switch_page("pages/group.py")
                    else:
                        st.switch_page("pages/error.py")

        with col_2_right:
            pass

        # エラーがある場合、表示
        if not is_valid:
            for msg in error_messages:
                st.error(msg)

with col_3:
    pass
