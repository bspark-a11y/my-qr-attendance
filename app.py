import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 구글 시트 연결 설정 (수정된 부분) ---


def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # [수정 핵심] 파일 대신 Streamlit Secrets에서 직접 정보를 가져옵니다.
    # 이렇게 하면 secrets.json 파일이 없어도 서버에서 잘 작동합니다.
    creds_dict = dict(st.secrets)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)

    # 사장님이 만든 구글 시트 이름을 정확히 적으세요! (예: "출석부_DB")
    sheet = client.open("출석부_DB").sheet1
    return sheet


# 아래 로직은 그대로 두시면 됩니다!
try:
    sheet = connect_google_sheet()
except Exception as e:
    st.error(f"구글 시트 연결 실패! 에러: {e}")
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
