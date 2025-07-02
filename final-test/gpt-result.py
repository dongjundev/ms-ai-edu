import os
import glob
import openai
from dotenv import load_dotenv
import streamlit as st
from fpdf import FPDF
import tempfile

# 환경변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

def read_source_files(folder_path, exts=['.py', '.java', '.js', '.ts', '.cpp', '.c']):
    """지정된 폴더의 소스코드 파일 목록과 내용을 반환"""
    code_data = []
    for ext in exts:
        for filepath in glob.glob(os.path.join(folder_path, f'**/*{ext}'), recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                code_data.append({'path': filepath, 'content': code})
            except Exception as e:
                continue
    return code_data

def ai_analyze_source(files):
    """AI를 통해 소스코드 요약/분석"""
    if not files:
        return "소스코드 파일을 찾을 수 없습니다."

    # 간단 예시: 파일명만 전달 (실제 분석은 파일 내용을 요약/분석)
    prompt = "아래 소스코드 파일들을 전체적으로 분석해주고, 비즈니스 로직, 주요 특징/구성/주요 함수 및 전반적인 구조와 개선점을 요약해줘. 그리고 다이어그램도 그릴 수 있으면 그려줘\n\n"
    for file in files:
        prompt += f"### 파일: {os.path.basename(file['path'])}\n"
        prompt += f"{file['content'][:1000]}\n\n"  # 토큰 과다 방지, 각 파일별 최대 1000자
    prompt += "\n최대한 구조적으로, 한글로 정리해줘."

    try:
        response = openai.chat.completions.create(
            model=DEPLOYMENT_NAME,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "당신은 훌륭한 소스코드 분석가입니다."},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"분석 중 오류: {e}"

def make_pdf(report, filename="분석_리포트.pdf"):
    """텍스트를 PDF로 저장"""
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('ArialUnicodeMS', '', './fonts/ArialUnicode.ttf', uni=True)
    pdf.set_font('ArialUnicodeMS', '', 12)
    for line in report.split('\n'):
        pdf.cell(0, 10, txt=line, ln=1)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

def main():
    st.title("소스코드 분석 PDF 리포트 생성기")
    st.write("소스코드 폴더 경로를 입력하면, AI가 분석 후 PDF로 결과를 제공합니다.")
    
    folder_path = st.text_input("소스코드 폴더 경로를 입력하세요.", "")

    if folder_path:
        with st.spinner("소스코드 읽는 중..."):
            files = read_source_files(folder_path)
            st.write(f"총 {len(files)}개의 소스코드 파일을 읽었습니다.")
            if files:
                st.write("파일 목록 예시:", [os.path.basename(f['path']) for f in files[:5]])

        if st.button("AI로 분석하고 PDF로 저장"):
            with st.spinner("AI가 소스코드를 분석 중입니다..."):
                report = ai_analyze_source(files)
            st.success("분석 완료!")

            with st.spinner("PDF로 저장 중..."):
                pdf_path = make_pdf(report)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="PDF 리포트 다운로드",
                    data=pdf_file,
                    file_name="분석_리포트.pdf",
                    mime="application/pdf"
                )
            st.write("분석 결과:")
            st.text_area("AI 분석 요약", report, height=400)

if __name__ == "__main__":
    main()