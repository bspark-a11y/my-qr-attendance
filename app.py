import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import qrcode
from io import BytesIO

# --- [중요] 불필요한 st.write()나 출력문을 모두 제거한 클린 함수 ---


def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # 1. 서버(Streamlit Cloud) 환경 체크
    if len(st.secrets) > 0:
        creds_dict = dict(st.secrets)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope)
    else:
        # 2. 로컬 환경 체크
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "secrets.json", scope)
        except:
            st.error("비밀번호 설정(Secrets)을 확인해주세요.")
            st.stop()

    client = gspread.authorize(creds)
    # 반드시 구글 시트 이름이 "출석부_DB"여야 합니다.
    return client.open("출석부_DB").sheet1


# --- 화면 구성 시작 ---
st.set_page_config(page_title="QR 출석", page_icon="📱")

# 배경에서 시트 미리 연결 (에러 방지)
try:
    sheet = connect_google_sheet()
except Exception as e:
    st.error("시트 연결에 실패했습니다. 구글 시트 이름을 확인하세요.")
    st.stop()

st.title("📱 스마트 QR 출석")

# 주소에서 이름 파라미터 가져오기
scanned_name = st.query_params.get("name")

if scanned_name:
    st.success(f"👋 {scanned_name}님, 환영합니다!")
    if st.button("✅ 지금 출석하기", use_container_width=True):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, scanned_name, "출석"])
        st.balloons()
        st.info("출석 완료! 창을 닫으셔도 됩니다.")
else:
    # 관리자 화면
    st.subheader("🛠️ QR 코드 생성")

    # [주의] 이 주소를 사장님의 '진짜' 배포 주소로 꼭 바꿔주세요!
    base_url = "https://my-qr-attendance-jxye92bqfhseeax37kohj.streamlit.app"

    name = st.text_input("학생 이름 입력")
    if st.button("QR 생성"):
        if name:
            qr_url = f"{base_url}/?name={name}"
            qr = qrcode.make(qr_url)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption=f"{name}님의 QR")
            st.write(f"접속 주소: {qr_url}")
        else:
            st.warning("이름을 입력하세요.")

    st.divider()
    if st.button("📊 실시간 출석부 보기"):
        df = pd.DataFrame(sheet.get_all_records())
        st.dataframe(df)
