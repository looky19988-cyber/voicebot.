import streamlit as st
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64
from io import BytesIO

def STT(audio_file, apikey):
    client = openai.OpenAI(api_key=apikey)
    audio_file.name = "input.wav"
    response = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return response.text

def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key=apikey)
    response = client.chat.completions.create(
        model=model,
        messages=prompt
    )
    return response.choices[0].message.content

def TTS(response):
    tts = gTTS(text=response, lang='ko')
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    st.audio(buf, format='audio/mp3', autoplay=True)

def main():
    st.set_page_config(
        page_title="음성 비서 프로그램", 
        layout="wide"
        )
# session state 초기화 
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
        
    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""
        
    if "message" not in st.session_state:
        st.session_state["message"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in Korean"}]
    
    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = False
    
    if "check_reset" not in st.session_state:  # ✅ 추가
        st.session_state["check_reset"] = False
        
    if "audio_key" not in st.session_state:
        st.session_state["audio_key"] = 0
        
    # 제목        
    st.header("음성 비서 프로그램")
    # 구분선 
    st.markdown("---")
    # 설명
    with st.expander("음성 비서 프로그램에 관하여", expanded=True):
        st.write("""
            - 음성 비서 프로그램의 UI는 스트림릿을 활용했습니다.
            - STT(Speech-To-Text) 기능은 OpenAI의 Whisper AI를 활용했습니다.
            - TTS(Text-To-Speech) 기능은 gTTS(Google Text-to-Speech)를 활용했습니다.
            - 답변은 OpenAI의 GPT 모델을 활용했습니다.
        """)
    #사이드 바 생성 
    with st.sidebar:
        # open AI API키 입력받기
        st.session_state["OPENAI_API"] = st.text_input(
            label="OPENAI API KEY", 
            placeholder="Enter Your API Key", 
            value="", 
            type="password"
        )
        
        st.markdown("---")

        # GPT 모델 선택하기 위한 라디오 생성 버튼 
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])
        st.markdown("---")

        # 리셋 버튼 생성 
        if st.button(label="초기화"):
            # 리셋 코드
            st.session_state["chat"] = []
            st.session_state["message"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in Korean"}]
            st.session_state["check_reset"] = True
            st.session_state["audio_key"] += 1   # 녹음 위젯 자체를 새로 만들어버림
            st.rerun() # 화면 즉시 새로고침
            
    question = None

    #기능 구현 공간 
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        audio = st.audio_input("클릭하여 녹음하기", sample_rate=16000, key=f"audio_input_{st.session_state['audio_key']}")


    with col2:
        st.subheader("질문/답변")
        if audio is not None and st.session_state["check_reset"] == False and st.session_state["OPENAI_API"]:  # ✅ 수정
            question = STT(audio, st.session_state["OPENAI_API"])

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("user", now, question))
            st.session_state["message"].append({"role": "user", "content": question})

            response = ask_gpt(st.session_state["message"], model, st.session_state["OPENAI_API"])

            st.session_state["message"].append({"role": "assistant", "content": response})
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("bot", now, response))

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:gray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")

            TTS(response)

if __name__ == "__main__":
    main()
