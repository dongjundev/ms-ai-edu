# 환경변수
import os
import openai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

#OpenAI 클라이언트 설정
def get_openapi_client(messages):
    # OpenAI API 호출 예시
    try:
        response = openai.chat.completions.create(
            model = DEPLOYMENT_NAME,
            temperature=0.4,
            messages = messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류 발생: {e}")
        return f"Error: {e}"

def main():
    #Streamlit UI 설정
    st.title("Azure OpenAI Chat Interface")
    st.write("Azure OpenAI API를 사용한 모델과 대화해 보세요~^^")

    #채팅 기록의 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    #채팅 메시지 표시
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    #사용자 입력 받기
    if user_input := st.chat_input("메세지를 입력하세요."):
        #사용자 메시지 추가
        st.session_state.messages.append({"role":"user", "content":user_input})
        st.chat_message("user").write(user_input)

        #OpenAI API 호출
        with st.spinner("응답 생성 중..."):
            response = get_openapi_client(st.session_state.messages)

        #AI 응답 추가
        st.session_state.messages.append({"role":"assistant", "content":response})
        st.chat_message("assistant").write(response)


if __name__ == "__main__":
    main()
