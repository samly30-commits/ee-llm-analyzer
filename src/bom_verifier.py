import re
import pandas as pd

def extract_refdes_from_text(text):
    """비정형 문자열 텍스트나 Gerber 데이터에서 단일 RefDes 추출"""
    if not isinstance(text, str):
        return []
    
    # R1-R5 같은 범위 문자열 확장 처리 로직 (LLM 협업 설계 코드)
    ranges = re.findall(r'\b([A-Z]+)(\d+)-([A-Z]+)?(\d+)\b', text.upper())
    expanded = []
    for prefix1, start, prefix2, end in ranges:
        pref = prefix1
        for i in range(int(start), int(end) + 1):
            expanded.append(f"{pref}{i}")
            
    # 범위 패턴 제거 후 개별 패턴 매칭 (R1, C1, U12 등)
    clean_text = re.sub(r'\b[A-Z]+\d+-[A-Z]?\d+\b', '', text.upper())
    individuals = re.findall(r'\b[A-Z]+\d+\b', clean_text)
    
    return list(set(expanded + individuals))

def verify_gerber_vs_bom(gerber_refdes_list, bom_excel_path):
    """Gerber 리스트와 Excel BOM 대조 크로스 체크"""
    df_bom = pd.read_excel(bom_excel_path)
    
    # Excel 내 Designator나 RefDes 컬럼 자동 스캔
    col_name = None
    for col in df_bom.columns:
        if any(keyword in col.lower() for keyword in ['designator', 'ref', 'component', '부품']):
            col_name = col
            break
            
    if not col_name:
        return {"error": "BOM 내 부품 기호(Designator) 열을 찾을 수 없습니다."}
    
    bom_refdes_set = set()
    for item in df_bom[col_name].dropna():
        bom_refdes_set.update(extract_refdes_from_text(str(item)))
        
    gerber_set = set(gerber_refdes_list)
    
    # 차집합 연산 수행
    missing_in_bom = gerber_set - bom_refdes_set
    untracked_in_gerber = bom_refdes_set - gerber_set
    
    return {
        "missing_in_bom": list(missing_in_bom),
        "untracked_in_gerber": list(untracked_in_gerber)
    }
