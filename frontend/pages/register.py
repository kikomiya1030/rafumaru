import streamlit as st
import datetime
import requests
import socket
from items.balloons import balloons
from items.hide_default_header import hide_header
from items.set_config import set_con
from user import User


set_con()

if "path" not in st.session_state:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    st.session_state["path"] = ip

hide_header()

submit_btn = False
is_success = False

col_1, col_2, col_3 = st.columns([1, 8, 1])
with col_1:
    pass
with col_2:
    if is_success == False:
        my_form = st.form(key="register")
        with my_form:
            register_html = """
            <style>
                .center {
                    text-align: center;
                }
            </style>
            <h1 class='center'>新規登録</h1>
            """
            st.markdown(register_html, unsafe_allow_html=True)
            space_html = """
            <style>
                .space {
                    padding: 20px 0px;
                }
            </style>
            <div class='space'></div>
            """
            st.markdown(space_html, unsafe_allow_html=True)

            message = st.text("")
            user_id = st.text_input("ID", key="id")
            mail_address = st.text_input("メールアドレス", key="mail")
            password = st.text_input("パスワード", type="password", key="pass")
            nick_name = st.text_input("ニックネーム", key="nick")

            st.markdown(space_html, unsafe_allow_html=True)

            col_4, col_5, col_6 = st.columns(3)
            with col_4:
                pass
            with col_5:
                submit_btn = st.form_submit_button("登録", use_container_width=True)
                if submit_btn == True:
                    if user_id == "" or user_id == None:
                        message.error("IDを入力してください。")
                    elif len(user_id) > 20:
                        message.error("IDは20文字以下で入力してください。")
                    elif mail_address == "":
                        message.error("メールアドレスを入力してください。")
                    elif password == "":
                        message.error("パスワードを入力してください。")
                    elif nick_name == "":
                        message.error("ニックネームを入力してください。")
                    else:
                        # Initialize connection.
                        path = st.session_state["path"]
                        last_login = str(datetime.datetime.now())
                        response = requests.post(f"http://{path}:8000/api/register/", json={"user_id": user_id, "mail_address":mail_address, "password":password, "nick_name":nick_name, 'last_login': last_login})
                        if response.status_code == 200:
                            is_res_data = response.json()
                            is_res = is_res_data["message"]
                            print(is_res)
                            if is_res == "success":
                                message.success("登録が完了しました！")
                                st.session_state["user_id"] = is_res_data["user_id"]
                                st.session_state["mail_address"] = is_res_data["mail_address"]
                                st.session_state["password"] = is_res_data["password"]
                                st.session_state["nickname"] = is_res_data["nickname"]
                                st.session_state["last_login"] = is_res_data["last_login"]
                                user = User(is_res_data["user_id"], is_res_data["mail_address"], is_res_data["password"], is_res_data["nickname"], is_res_data["last_login"])
                                st.session_state["user"] = user
                                is_success = True
                                
                            else:
                                message.error("登録に失敗しました")
                                is_success = False
            with col_6:
                pass            
    if is_success:
        st.switch_page("pages/register_success.py")
    
with col_3:
    pass