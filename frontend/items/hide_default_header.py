import streamlit as st
def hide_header():
    HIDE_ST_STYLE = """
                    <style>
                    div[data-testid="stToolbar"] {
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                    }
                    div[data-testid="stDecoration"] {
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                    }
                    #MainMenu {
                    visibility: hidden;
                    height: 0%;
                    }
                    header {
                    visibility: hidden;
                    height: 0%;
                    }
                    footer {
                    visibility: hidden;
                    height: 0%;
                    }
                            .appview-container .main .block-container{
                                padding-top: 1rem;
                                padding-right: 3rem;
                                padding-left: 3rem;
                                padding-bottom: 1rem;
                            }  
                            .reportview-container {
                                padding-top: 0rem;
                                padding-right: 3rem;
                                padding-left: 3rem;
                                padding-bottom: 0rem;
                            }
                            header[data-testid="stHeader"] {
                                z-index: -1;
                            }
                            div[data-testid="stToolbar"] {
                            z-index: 100;
                            }
                            div[data-testid="stDecoration"] {
                            z-index: 100;
                            }
                    .st-emotion-cache-13ln4jf {
                    width: 100%;
                    padding: 0px;
                    max-width: 46rem;
                    }

                    /* ボタンに影を追加 */
                    button {
                        background-color: #ffffff; /* ボタンの背景色 */
                        color: #000000; /* ボタンの文字色 */
                        border-radius: 5px; /* 角丸 */
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); /* 通常状態の影 */
                        transition: all 0.3s ease-in-out; /* アニメーションのスムーズさ */
                    }

                    /* ホバー時に影を強調 */
                    button:hover {
                        transform: scale(1.05); /* 拡大 */
                        box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.3); /* ホバー時の影 */
                        cursor: pointer; /* ポインタ変更 */
                    }
                   
                    </style>
    """

    st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)

    css = """
        <style>
        .st-emotion-cache-1jicfl2 {
        padding: 0rem 1rem 5rem;
        }
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)
