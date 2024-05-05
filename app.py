import streamlit as st
import area_list


st.set_page_config(
    page_title="농업용 코파일럿",
    #page_icon="🧊",
    initial_sidebar_state="collapsed",
)

sido = area_list.sido
sido_list = area_list.sido_list


if "api_key" not in st.session_state:
    st.session_state['api_key'] = None

if "sido" not in st.session_state: #시/도
    st.session_state['sido'] = None

if "gugun" not in st.session_state: #구/군
    st.session_state['gugun'] = None

st.title("농업용 코파일럿")

#st.subheader("지역을 선택해주세요")
with st.container():
    col1, col2 = st.columns(2)

    selected_sido = col1.selectbox(
        label="시/도 선택",
        options=sido_list,
        index=None,
        placeholder="시/도를 선택해주세요."
    )

    gugun_list = []
    for i in sido:
        if selected_sido is list(i.keys())[0]:
            gugun_list = i[selected_sido]

    selected_gugun = col2.selectbox(
        label="구/군 선택",
        options=gugun_list,
        index=None,
        placeholder="군/구를 선택해주세요."
    )
    
    #api_key = st.text_input("API키 입력", type="password") 수정

    submitted = st.button("확인")
    if submitted:
        st.session_state['sido'] = selected_sido
        st.session_state['gugun'] = selected_gugun
        st.session_state['api_key'] = st.secrets['openai_api_key']
        st.switch_page("pages/chat_page.py")