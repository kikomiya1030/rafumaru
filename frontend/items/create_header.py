import streamlit as st 
import datetime
from browser_detection import browser_detection_engine

def create_header(page_name):
    if "width" not in st.session_state:
        value = browser_detection_engine()
        is_Desktop = value["isDesktop"]
        is_Tablet = value["isTablet"]
        if is_Tablet or is_Desktop:
            st.session_state["width"] = False
        else:
            st.session_state["width"] = True
    if st.session_state["width"]:
        # 初期値設定
        if "user_id" not in st.session_state or st.session_state["user_id"] == "None":
            st.session_state["user_id"] = None
        if "nickname" not in st.session_state or st.session_state["nickname"] == "None":
            st.session_state["nickname"] = None
        if "mail_address" not in st.session_state or st.session_state["mail_address"] == "None":
            st.session_state["mail_address"] = None
        rafu = """
            <style type="text/css" media="screen">
            .center {
                text-align: center;
                color: #4CAF50;
                margin: 0px;
                padding: 0px;
                padding-bottom: 25px;
            }
            </style>
        """ + f"<h1 id='vw' class='center'>{page_name}</h1>"
                   
        st.markdown(rafu, unsafe_allow_html=True)
        if st.session_state["user_id"] is not None:
 
            col_1_left, col_1_mid, col_1_mid2, col_1_right = st.sidebar.columns([1.5, 0.5, 0.5, 1])
            with col_1_left:
                user_name = st.session_state["nickname"]
                rafu = f"<p id='vw_1'>{user_name} さん</p>"
                   
                st.markdown(rafu, unsafe_allow_html=True)
            with col_1_mid:
                if st.sidebar.button(label="👤"):
                    st.session_state["notice"] = False
                    st.session_state["show_confirm"] = False
                    st.session_state["info_rev"] = False
                    st.switch_page("pages/user.py")
            with col_1_mid2:
                if st.sidebar.button(label="📩"):
                    st.session_state["notice"] = True
                    st.switch_page("pages/user.py")
           
            with col_1_right:
                if st.sidebar.button(label="ログアウト"):
                    del st.session_state["user_id"]
                    del st.session_state["mail_address"]
                    del st.session_state["password"]
                    del st.session_state["nickname"]
                    del st.session_state["last_login"]
                    st.session_state["sessionid"] = None
                    #st.rerun()
                    st.switch_page("pages/main.py")
        else:
            if st.sidebar.button(label="ログイン", use_container_width=True):
                st.switch_page("pages/login.py")
            if st.sidebar.button(label="新規登録", use_container_width=True):
                st.switch_page("pages/register.py")
        if st.sidebar.button(label="ホーム", use_container_width=True):
            st.session_state["filter"] = False # 詳細フィルターのデフォルト値
            st.session_state["year"] = datetime.datetime.today().year # 本月のデータを表示
            st.session_state["month"] = datetime.datetime.today().month # 本月のデータを表示
            st.switch_page("pages/main.py")
        if st.sidebar.button(label="公開", use_container_width=True):
            st.session_state["year"] = datetime.datetime.today().year # 本月のデータを表示
            st.session_state["month"] = datetime.datetime.today().month # 本月のデータを表示
            st.session_state["myself"] = False
            st.session_state["selected_date"] = None
            st.session_state["selected_prefecture"] = None
            st.switch_page("pages/share_all.py")
        if st.sidebar.button(label="共同家計簿", use_container_width=True):
            st.session_state["year"] = datetime.datetime.today().year # 本月のデータを表示
            st.session_state["month"] = datetime.datetime.today().month # 本月のデータを表示
            st.session_state["show_confirm_delete"] = False
            st.switch_page("pages/group.py")
    else:
        # 初期値設定
        if "user_id" not in st.session_state or st.session_state["user_id"] == "None":
            st.session_state["user_id"] = None
        if "nickname" not in st.session_state or st.session_state["nickname"] == "None":
            st.session_state["nickname"] = None
        if "mail_address" not in st.session_state or st.session_state["mail_address"] == "None":
            st.session_state["mail_address"] = None
 
        col_1, col_2 = st.columns([5, 9])
        with col_1:
            #if "nickname" in st.session_state:
            if st.session_state["user_id"] is not None:
                col_1_left, col_1_mid, col_1_mid2, col_1_right = col_1.columns([1.5, 0.5, 0.5, 1])
                with col_1_left:
                    user_name = st.session_state["nickname"]
                    rafu = f"<p id='vw_1'>{user_name} さん</p>"
                       
                    st.markdown(rafu, unsafe_allow_html=True)
                with col_1_mid:
                    if st.button(label="👤"):
                        st.session_state["notice"] = False
                        st.session_state["show_confirm"] = False
                        st.session_state["info_rev"] = False
                        st.switch_page("pages/user.py")
                with col_1_mid2:
                    if st.button(label="📩"):
                        st.session_state["notice"] = True
                        st.switch_page("pages/user.py")
               
                with col_1_right:
                    if st.button(label="ログアウト"):
                        del st.session_state["user_id"]
                        del st.session_state["mail_address"]
                        del st.session_state["password"]
                        del st.session_state["nickname"]
                        del st.session_state["last_login"]
                        st.session_state["sessionid"] = None
                        #st.rerun()
                        st.switch_page("pages/main.py")
            else:
                col_1_left, col_1_right = col_1.columns(2)
                with col_1_left:
                    if st.button(label="ログイン", use_container_width=True):
                        st.switch_page("pages/login.py")
 
                with col_1_right:
                    if st.button(label="新規登録", use_container_width=True):
                        st.switch_page("pages/register.py")
        with col_2:
            col_3, col_4, col_5, col_6 = col_2.columns([2, 1, 1, 1])
            with col_3:
                rafu = """
                    <style type="text/css" media="screen">
                    #vw{
                        font-size: 2vw;
                        font-weight: 700;
                        color: #4CAF50;
                    }
                    #vw_1{
                        font-size: 1.3vw;
                        padding-top: 7px;
                        margin: 0px;
                    }
                    .center {
                        text-align: center;
                        margin: 0px;
                        padding: 0px;
                        padding-bottom: 25px;
                    }
                    </style>
                """ + f"<p id='vw' class='center' class='center'>{page_name}</p>"
                   
                st.markdown(rafu, unsafe_allow_html=True)
            with col_4:
                if st.button(label="ホーム", use_container_width=True):
                    st.session_state["filter"] = False # 詳細フィルターのデフォルト値
                    st.session_state["year"] = datetime.datetime.today().year # 本月のデータを表示
                    st.session_state["month"] = datetime.datetime.today().month # 本月のデータを表示
                    st.switch_page("pages/main.py")
            with col_5:
                if st.button(label="公開", use_container_width=True):
                    st.session_state["year"] = datetime.datetime.today().year # 本月のデータを表示
                    st.session_state["month"] = datetime.datetime.today().month # 本月のデータを表示
                    st.session_state["myself"] = False
                    st.session_state["selected_date"] = None
                    st.session_state["selected_prefecture"] = None
                    st.switch_page("pages/share_all.py")
            with col_6:
                if st.button(label="共同家計簿", use_container_width=True):
                    st.session_state["year"] = datetime.datetime.today().year # 本月のデータを表示
                    st.session_state["month"] = datetime.datetime.today().month # 本月のデータを表示
                    st.session_state["show_confirm_delete"] = False
                    st.switch_page("pages/group.py")
           
 
 
        hr = """
            <style>
            hr {
                margin: 0px;
            }
            </style>
            ***
        """
        st.markdown(hr, unsafe_allow_html=True)
 