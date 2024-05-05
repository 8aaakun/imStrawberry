import streamlit as st
from st_multimodal_chatinput import multimodal_chatinput
import openai
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
import io
import base64

st.set_page_config(
    page_title="농업용 코파일럿",
    #page_icon="🧊",
    initial_sidebar_state="expanded",
)


if "api_key" not in st.session_state:
    st.session_state['api_key'] = None

if not st.session_state['api_key']:
    st.switch_page("app.py")

client = openai
client.api_key = st.session_state['api_key']

#응답 요청 함수
def get_completion(prompt, model, temperature):
    messages = []
    for i in st.session_state['chat']:
        messages.append({"role": i.sender, "content": i.msg})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

#tts 요청함수
def text_speech(text):
    tts = gTTS(text=text, lang='ko')

    # Save speech to a BytesIO object
    speech_bytes = io.BytesIO()
    tts.write_to_fp(speech_bytes)
    speech_bytes.seek(0)

    # Convert speech to base64 encoding
    b64 = base64.b64encode(speech_bytes.read()).decode('utf-8')
    md = f"""
            <audio id="audioTag" controls autoplay>
            <source src="data:audio/mp3;base64,{b64}"  type="audio/mpeg" format="audio/mpeg">
            </audio>
            """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )
    
#side bar
sidebar = st.sidebar

sidebar.header("Chatbot")
sidebar.text("copilot")

#st.session_state['api_key'] = True
if not st.session_state['api_key']:
    sidebar.error(":x: API 인증 안됨")
else :
    sidebar.success(":white_check_mark: API 인증 완료")

sidebar.subheader("Models and parameters")

model = sidebar.selectbox(
    label="모델 선택",
    options=["gpt-3.5-turbo", "gpt-4-turbo", "모델3"]
)
                    

params = sidebar.expander("Parameters")

#temperature
temperature = params.slider(
    label="temperature",
    min_value=0.01,
    max_value=5.00,
    step=0.01
)

#top_p
top_p = params.slider(
    label="top_p",
    min_value=0.01,
    max_value=1.00,
    step=0.01,
    value=0.90
)

#max_length
max_length = params.slider(
    label= "max_length",
    min_value=32,
    max_value=128,
    step = 1,
    value=120
)

# sidebar.button(
#     label= "Clear Chat History"
# )  

#chat
class chat:
    img = None
    msg: str = None
    sender: str = None
    isTTS = None
    def __init__(self, img = None, msg = None, sender = None):
         self.msg = msg
         self.sender = sender
         self.img = img
        

if 'chat' not in st.session_state:
    st.session_state['chat'] = []
    st.session_state['chat'].append(chat(msg = "무엇을 도와드릴까요?", sender='assistant')) ##첫 채팅
        
chatContainer = st.container(height=450)
userInput = multimodal_chatinput()

for i in st.session_state['chat']:
    with chatContainer:
        with st.chat_message(i.sender):
            if i.img:
                st.image(i.img)
            st.write(i.msg)

if "userinput_check" not in st.session_state: #이전에 썼는지 체크
    st.session_state['userinput_check'] = None

if userInput and userInput['text'] != st.session_state['userinput_check']:
    #유저 입력
    chatting = chat()
    if userInput['images']:
        chatting.img = userInput['images']
    chatting.msg = userInput['text']
    chatting.sender = 'user'
    st.session_state['chat'].append(chatting)
    st.session_state['userinput_check'] = userInput['text']
    #메시지 출력
    with chatContainer:
        with st.chat_message('user'):
            if userInput['images']:
                st.image(userInput['images'])
            st.write(userInput['text'])
        # for i in st.session_state['chat']:
        #     with st.chat_message(i.sender):
        #         if i.img:
        #             st.image(i.img)
        #         st.write(i.msg)
    #챗봇
    response_message = get_completion(userInput['text'], model, temperature)
    response = chat()
    response.msg = response_message
    response.sender = 'assistant'
    st.session_state['chat'].append(response)
    #메시지 출력
    with chatContainer:
        with st.chat_message('assistant'):
            st.write(response_message)
    # with chatContainer:
    #     for i in st.session_state['chat']:
    #         if i.sender is 'ai':
    #             with st.chat_message(i.sender):
    #                st.write(i.msg)
    userInput = None


# stt 사용
if "tts_check" not in st.session_state: #이전에 썼는지 체크
    st.session_state['tts_check'] = None


stt_button = Button(label="말하기", width=100, button_type="success")
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))


with sidebar:
    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=40,
        debounce_time=0,)
        

if result :
    if "GET_TEXT" in result and result.get("GET_TEXT") != st.session_state['tts_check']:
        speech = chat()
        #if result.get("GET_TEXT") != st.session_state['chat'][-1].msg:
        speech.msg = result.get("GET_TEXT")
        speech.sender = 'user'
        st.session_state['chat'].append(speech)
        #유저 메시지 출력
        with chatContainer:
            with st.chat_message('user'):
                st.write(result.get("GET_TEXT"))
        st.session_state['tts_check'] = result.get("GET_TEXT")

        #챗봇
        response_message = get_completion(result.get("GET_TEXT"), model, temperature)
        response = chat()
        response.msg = response_message
        response.sender = 'assistant'
        response.isTTS = True
        st.session_state['chat'].append(response)
        
        #챗봇 메시지 출력
        with chatContainer:
            with st.chat_message('assistant'):
                st.write(response_message)
                text_speech(response_message)
        