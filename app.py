import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image

# --- 1. 구글 시트 연결 설정 (로컬/서버 공용) ---


def connect_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # 스트림릿 클라우드(Secrets) 설정이 있는지 확인
    if "project_id" in st.secrets:
        # [서버 모드]
        creds_dict = dict(st.secrets)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope)
    else:
        # [로컬 모드] 사장님 PC에 secrets.json이 있어야 함
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "secrets.json", scope)
        except Exception:
            st.error("로컬에서 실행 시 'secrets.json' 파일이 필요합니다.")
            st.stop()

    client = gspread.authorize(creds)
    # 구글 시트 이름 확인 (실제 시트 이름과 똑같이 맞추세요)
    sheet = client.open("출석부_DB").sheet1
    return sheet


# 시트 연결
try:
    sheet = connect_google_sheet()
except Exception as e:
    st.error(f"구글 시트 연결 실패: {e}")
    st.stop()

# --- 2. 화면 구성 ---
st.set_page_config(page_title="QR 출석 시스템", page_icon="📱")
st.title("📱 스마트 QR 출석 시스템")

# 주소창에서 이름 파라미터(?name=xxx) 읽기
query_params = st.query_params
scanned_name = query_params.get("name")

# --- 3. 출석 체크 로직 (학생이 QR 찍었을 때 보이는 화면) ---
if scanned_name:
    st.success(f"👋 {scanned_name}님, 환영합니다!")
    if st.button("✅ 지금 출석하기", use_container_width=True):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, scanned_name, "출석"])
        st.balloons()
        st.info("출석이 완료되었습니다. 창을 닫으셔도 됩니다.")
else:
    st.info("관리자 페이지입니다. 아래에서 QR 코드를 생성하세요.")

# --- 4. QR 코드 생성기 (관리자용) ---
st.divider()
st.subheader("🛠️ 출석용 QR 코드 생성")

# [중요] 현재 접속한 주소 자동 감지
# 로컬일 땐 localhost, 배포 후엔 실제 도메인 주소를 사용합니다.
if "project_id" in st.secrets:
    # 배포된 서버의 실제 주소 (사장님의 배포 주소를 직접 적는게 가장 확실합니다)
    base_url = "https://my-qr-attendance-jxye92bqfhseeax37kohj.streamlit.app"
else:
    base_url = "http://localhost:8501"

name_to_generate = st.text_input("학생 이름을 입력하세요 (예: 홍길동)")

if st.button("QR 코드 생성하기"):
    if name_to_generate:
        # 학생 이름이 포함된 주소 생성
        final_url = f"{base_url}/?name={name_to_generate}"

        # QR 생성
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(final_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # 화면 표시를 위해 변환
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.image(
            byte_im, caption=f"{name_to_generate}님의 출석 QR (주소: {final_url})")
        st.download_button("QR 이미지 다운로드", data=byte_im,
                           file_name=f"QR_{name_to_generate}.png", mime="image/png")
    else:
        st.warning("이름을 입력해 주세요.")

# --- 5. 실시간 출석 현황 확인 ---
st.divider()
st.subheader("📋 실시간 출석 명단")
if st.button("새로고침"):
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.table(df)
    else:
        st.write("아직 출석 데이터가 없습니다.")
