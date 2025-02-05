import streamlit as st
from items.hide_default_header import hide_header
from items.create_header import create_header
from items.set_config import set_con
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
session_list = ["path"]
if any(session not in st.session_state for session in session_list):
    st.switch_page("pages/main.py")
    st.stop()

# セッションからデータを取り出す
user_id = st.session_state["user_id"]
path = st.session_state["path"]

# タイトル
colA, colB = st.columns([1,20])
with colA:
    if st.button("⬅︎"):
        st.switch_page("pages/group.py")
with colB:
    st.subheader("グループ加入")


col_1, col_2, col_3 = st.columns([1, 2, 1])
with col_1:
    pass
with col_2:
    with st.form(key="syousai"):
        # グループ作成フォーム
        group_id = st.text_input("グループ番号", max_chars=9)
        st.caption("9桁のグループ番号を入力してください。")
        group_password = st.text_input("パスワード", type="password")
        st.caption("パスワードは8桁以上16桁以下で入力してください。")

        # バリデーション用のフラグ
        is_valid = True
        error_messages = []
        message = st.empty()

        # ボタンの配置
        col_2_left, col_2_center, col_2_right = st.columns([1, 1, 1])
        with col_2_left:
            pass
        with col_2_center:
            submit_create = st.form_submit_button("加入", use_container_width=True)
            if submit_create:
                # グループ名が空かチェック
                if not group_id.isdigit() or len(group_id) != 9:
                    is_valid = False
                    error_messages.append("9桁のグループ番号を入力してください。")

                # ルーム番号が9桁の数字かチェック
                if not group_password:
                    is_valid = False
                    error_messages.append("パスワードは8桁以上16桁以下で入力してください。")

                # バリデーション成功時
                if is_valid:
                    add_url = f"http://{path}:8000/api/group_add/"
                    add_response = requests.post(add_url, data={"user_id": user_id, "group_id": group_id, "group_password": group_password})
                    # バリデーション成功時
                    if add_response.status_code == 200:
                        message.success("加入！")
                        time.sleep(1)
                        st.switch_page("pages/group.py")
                    elif add_response.status_code == 201:
                        message.error("該当グループはすでに登録されています。")
                    elif add_response.status_code == 202:
                        message.error("グループ番号、またはパスワードが間違っています。")
                    else:
                        st.switch_page("pages/error.py")
                    
                      # ページ遷移

            # グループ作成画面に遷移する
            submit_back = st.form_submit_button("グループ作成", use_container_width=True)
            if submit_back:
                st.switch_page("pages/group_create.py")
        with col_2_right:
            pass

        # エラーがある場合、表示
        if not is_valid:
            for msg in error_messages:
                st.error(msg)

with col_3:
    pass
