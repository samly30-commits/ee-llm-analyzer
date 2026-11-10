import streamlit as st
import pandas as pd
from analyzer import parse_oscilloscope_csv, calculate_electrical_metrics, analyze_frequency_domain
from bom_verifier import extract_refdes_from_text, verify_gerber_vs_bom

st.set_page_config(page_title="EE LLM 통합 자동화 툴킷", layout="wide")
st.title("⚡ EE LLM-Based Engineering & Automation Dashboard")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 파형 데이터 분석기", "🔍 Gerber-BOM 정합성 검증기"])

with tab1:
    st.header("1) 회로 소자 및 파형 신호처리 분석")
    uploaded_csv = st.file_uploader("오실로스코프/LTspice CSV 파일 업로드", type=["csv"])
    
    if uploaded_csv:
        df = parse_oscilloscope_csv(uploaded_csv)
        if "Time(s)" in df.columns and "Voltage(V)" in df.columns:
            metrics = calculate_electrical_metrics(df["Voltage(V)"].values)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Peak-to-Peak 전압 (Vpp)", f"{metrics['Vpp']:.3f} V")
            c2.metric("실효 전압 (Vrms)", f"{metrics['Vrms']:.3f} V")
            c3.metric("리플 전율 (Ripple Factor)", f"{metrics['RippleFactor']:.2f} %")
            
            st.subheader("시간 영역 그래프")
            st.line_chart(df.set_index("Time(s)")["Voltage(V)"], height=250)
            
            freq, mag = analyze_frequency_domain(df["Time(s)"].values, df["Voltage(V)"].values)
            df_fft = pd.DataFrame({"Frequency(Hz)": freq, "Magnitude": mag})
            
            st.subheader("주파수 영역 분석 (FFT 스펙트럼)")
            st.area_chart(df_fft[df_fft["Frequency(Hz)"] <= 50000].set_index("Frequency(Hz)"), height=250)
        else:
            st.error("CSV 필수 컬럼('Time(s)', 'Voltage(V)')이 누락되었습니다. 샘플 데이터를 확인하세요.")

with tab2:
    st.header("2) Gerber Layout vs 구매 BOM 크로스 체크")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        gerber_input = st.text_area("Gerber 추출 RefDes 목록 입력 (예: R1-R5, C1)", value="R1-R5, C1, C2, U1, L1")
    with col_t2:
        uploaded_bom = st.file_uploader("구매팀 제출용 Excel BOM 업로드", type=["xlsx"])
        
    if st.button("정합성 교차 검증 실행") and uploaded_bom:
        gerber_refs = extract_refdes_from_text(gerber_input)
        results = verify_gerber_vs_bom(gerber_refs, uploaded_bom)
        
        if "error" in results:
            st.error(results["error"])
        else:
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                if results["missing_in_bom"]:
                    st.error(f"⚠️ Gerber엔 있으나 BOM에 누락됨 ({len(results['missing_in_bom'])}건)")
                    st.dataframe(pd.DataFrame(results["missing_in_bom"], columns=["누락 부품 부호"]))
                else:
                    st.success("✅ BOM 누락 부품 없음")
            with res_c2:
                if results["untracked_in_gerber"]:
                    st.warning(f"ℹ️ BOM에만 존재하는 미배치 부품 ({len(results['untracked_in_gerber'])}건)")
                    st.dataframe(pd.DataFrame(results["untracked_in_gerber"], columns=["미배치 부품 부호"]))
                else:
                    st.success("✅ 미배치 초과 발주 부품 없음")
