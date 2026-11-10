import numpy as np
import pandas as pd
import scipy.fft as fft

def parse_oscilloscope_csv(file_path):
    """오실로스코프 CSV 파일 읽기 및 데이터 추출"""
    # 헤더에 텍스트가 섞여 있을 경우를 대비해 쉼표 구조 분석 후 로드
    df = pd.read_csv(file_path)
    # 컬럼명 표준화 (공백 제거)
    df.columns = [col.strip() for col in df.columns]
    return df

def calculate_electrical_metrics(voltages):
    """핵심 전기적 파라미터 연산 (Vpp, Vrms, Ripple)"""
    v_max = np.max(voltages)
    v_min = np.min(voltages)
    v_pp = v_max - v_min
    v_rms = np.sqrt(np.mean(voltages**2))
    
    # 리플률 계산 (AC 성분의 진폭 / DC 평균값)
    v_dc = np.mean(voltages)
    ripple_factor = (v_pp / 2) / v_dc * 100 if v_dc != 0 else 0
    
    return {
        "Vpp": v_pp,
        "Vrms": v_rms,
        "Vdc": v_dc,
        "RippleFactor": ripple_factor
    }

def analyze_frequency_domain(times, voltages):
    """주파수 도메인 분석 (FFT) - LLM 프롬프트 피드백 수정 반영"""
    n = len(voltages)
    dt = np.mean(np.diff(times)) # 샘플링 주기 계산
    fs = 1.0 / dt                # 샘플링 주파수
    
    # DC 오프셋 제거 후 FFT 수행 (하모닉 성분 명확화)
    v_detrend = voltages - np.mean(voltages)
    fft_values = fft.fft(v_detrend)
    fft_frequencies = fft.fftfreq(n, d=dt)
    
    # Nyquist 주파수 범위 절반만 사용
    half_n = n // 2
    frequencies = fft_frequencies[:half_n]
    magnitudes = np.abs(fft_values[:half_n]) * 2 / n
    
    return frequencies, magnitudes
