import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 구글 시트 연결 설정 ---


def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "secrets.json", scope)
    client = gspread.authorize(creds)

    # 사장님의 구글 시트 이름과 똑같이 맞춰주세요!
    sheet = client.open("출석부_DB").sheet1
    return sheet


# 에러 방지를 위해 예외 처리 추가
try:
    sheet = connect_google_sheet()
except Exception as e:
    st.error(f"구글 시트 연결 실패! secrets.json 파일과 시트 이름을 확인하세요. \n에러: {e}")
    st.stop()

st.title("📱 온라인 연동 QR 출석 시스템")

# 주소창 이름 파라미터 읽기
query_params = st.query_params
scanned_name = query_params.get("name")

if scanned_name:
    st.header(f"👋 안녕하세요, {scanned_name}님!")
    # 최신 버전에 맞춰 width='stretch' 적용
    if st.button("✅ 출석하기", width='stretch'):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, scanned_name, "출석"])
        st.success("구글 시트에 출석이 기록되었습니다!")
        st.balloons()

# 실시간 현황 확인
st.divider()
st.subheader("📋 실시간 출석 현황 (From Google Sheets)")
if st.button("현황 새로고침", width='stretch'):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    # 최신 버전에 맞춰 width='stretch' 적용
    st.dataframe(df, width='stretch')
