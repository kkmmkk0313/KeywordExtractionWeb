import streamlit as st
import re
from functools import lru_cache  # 함수 결과를 캐시하기 위한 데코레이터
import random
import time
import colorsys  # 색상 시스템 변환
import threading

# 설정
MIN_KEYWORD_COUNT = 3  # 최소 키워드 수
MAX_KEYWORD_COUNT = 10  # 최대 키워드 수
DEFAULT_KEYWORD_COUNT = 5  # 기본 키워드 수
MIN_WORD_LENGTH = 1  # 최소 단어 길이

TEXTS = {
    'title': "AX KyfoAI 🔑",  # 애플리케이션 제목
    'keyword_count_label': "추출할 키워드 수",  # 키워드 수 라벨
    'extract_button': "키워드 추출",  # 키워드 추출 버튼 텍스트
    'reset_button': "초기화",  # 초기화 버튼 텍스트
    'content_title': "원문 기사",  # 원본 텍스트 제목
    'keywords_title': "키워드",  # 추출된 키워드 제목
    'error_message': "An error occurred while extracting keywords: "  # 에러
}

DEMO_TEXT = """
물 마시는 습관 만들기 어렵다면, 이렇게 해보세요

운동이던 물 섭취던 습관 형성을 위해선 환경 조성도 필요하다. 먼저 휴대용 물통을 준비해 미리 냉장고에 놔두는 것이 좋다.

외출 시 바로 가지고 나갈 수 있기 때문. 이외에도 간식거리처럼 평소에 손이 닿기 쉬운 곳에 큰 물통을 놔두는 것이 좋다. 

만약 미지근한 물이 싫다면 물병을 얼음으로 가득 채운 후 물을 따라두면 계속해서 시원한 물을 마실 수 있다. 

물 마시는 게 귀찮아도 수분 섭취는 필수다. 만약 물 마시기를 자꾸만 잊어버리게 된다면 애초에 수분이 많은 음식을 먹는 것도 방법이다. 

여름철 대표 과일·채소인 수박, 오이를 비롯해 딸기, 토마토 등처럼 수분 함량이 높은 음식을 먹으면 영양분과 수분을 동시에 섭취할 수 있다."""

KEYWORDS_AND_SCORES = {
    '운동': 0.8588922023773193,
    '수박': 0.8409304022789001,
    '음식': 0.5753307938575745,
    '얼음': 0.47479820251464844,
    '물': 0.4170352518558502,
    '딸기': 0.3694803714752197,
    '여름철': 0.268786758184433,
    '냉장고': 0.1421666294336319,
    '물병': 0.07270066440105438,
    '채소': 0.06898552179336548,
    '물통': 0.06540211290121078,
    '간식': 0.058810602873563766,
    '외출': 0.053684886544942856,
    '환경': 0.022230491042137146,
    '수분': 0.0
}

# 카피 딕셔너리 생성
COPY_KEYWORDS_AND_SCORES = KEYWORDS_AND_SCORES.copy()
def insert_new_keyword(new_word,keyword_count):
    # 세션 상태의 custom_keywords에 새 키워드 추가
    st.session_state.custom_keywords[new_word] = 1
    # COPY_KEYWORDS_AND_SCORES 업데이트
    global COPY_KEYWORDS_AND_SCORES
    COPY_KEYWORDS_AND_SCORES = {**KEYWORDS_AND_SCORES, **st.session_state.custom_keywords}
    total_keywords = keyword_count + len(st.session_state.custom_keywords)
    keyword_Extract(total_keywords)
    
@lru_cache(maxsize=None)
def get_keywords(_, n):
    try:
        all_keywords = {**KEYWORDS_AND_SCORES, **st.session_state.custom_keywords}
        # 키워드를 점수 기준으로 정렬하고 상위 n개를 선택
        sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:n]
        return [(word, round(score, 5)) for word, score in sorted_keywords]
    except Exception as e:
        st.error(f"{TEXTS['error_message']}{str(e)}")
        return []

def generate_softer_colors(n):
    hue_step = 1.0 / n
    colors = []
    for i in range(n):
        hue = i * hue_step
        saturation = 0.3 + random.random() * 0.3
        value = 0.8 + random.random() * 0.2
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(f"rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})")
    random.shuffle(colors)
    return colors

def create_highlighted_text(text, keywords, colors):
    highlighted_text = text
    for (keyword, _), color in zip(keywords, colors):
        pattern = re.compile(re.escape(keyword), re.IGNORECASE | re.UNICODE)
        replacement = f'<span class="keyword" style="background-color: {color};">\g<0></span>'
        highlighted_text = pattern.sub(replacement, highlighted_text)
    return highlighted_text

def update_state(keywords, highlighted_text):
    st.session_state.keywords = keywords
    st.session_state.highlighted_text = highlighted_text

def reset_state():
    st.session_state.add_num = 0
    update_state([], DEMO_TEXT)

def setup_page_config():
    st.set_page_config(layout="wide", page_title=TEXTS['title'], page_icon="🔑")

def initialize_session_state():
    if 'keywords' not in st.session_state:
        st.session_state.keywords = []
    if 'highlighted_text' not in st.session_state:
        st.session_state.highlighted_text = DEMO_TEXT
    if 'custom_keywords' not in st.session_state:
        st.session_state.custom_keywords = {}    

def keyword_Extract(total_keywords):
    with st.spinner('키워드를 추출하는 중...'):
        time.sleep(1.2)
        keywords = get_keywords(DEMO_TEXT, total_keywords)
        colors = generate_softer_colors(total_keywords)
        highlighted_text = create_highlighted_text(DEMO_TEXT, keywords, colors)
        update_state(keywords, highlighted_text)
        st.session_state.colors = colors
        st.rerun()

def show_temporary_message(message, type="success", duration=3):
    """
    임시 메시지를 표시하고 일정 시간 후에 제거함
    """
    if type == "success":
        placeholder = st.empty()
        placeholder.success(message)
    elif type == "warning":
        placeholder = st.empty()
        placeholder.warning(message)
    else:
        placeholder = st.empty()
        placeholder.info(message)
    # 별도의 스레드에서 시간을 계산하고 메시지를 제거
    threading.Timer(duration, placeholder.empty).start()

def main():
    st.session_state.add_num = 0 #추가된 키워드 수
    setup_page_config()
    initialize_session_state()

    # CSS, JS스타일
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    body {
        font-family: 'Poppins', sans-serif;  /* 폰트 */
        background-color: #f0f2f6;  /* 배경색 */
        color: #1e1e1e;  /* 텍스트 색 */
    }
    .gradient-text {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);  /* 제목에 그라데이션 */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        color: #4a4a4a;  /* 부제목 색상 설정 */
        border-bottom: 2px solid #4ecdc4;  /* 부제목 아래 경계선 */
        padding-bottom: 0.5rem;
    }
    .text-content {
        background-color: white;  /* 텍스트 배경색*/
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  /* 그림자 효과 */
        height: 60vh;
        overflow-y: auto;  /* 세로 스크롤 허용 */
    }
    .keyword {
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: bold;
        transition: background-color 0.3s ease;  /* 배경색 전환 효과 */
    }
    .keyword:hover {
        filter: brightness(90%);  /* 호버 밝기 조정 */
    }
    .keyword-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        animation: slideIn 0.5s ease-out forwards;  /* 슬라이드 인 애니메이션 */
        opacity: 0;
    }
    .keyword-text {
        width: 100px;
        font-weight: bold;
        margin-right: 10px;
    }
    .importance-bar {
        flex-grow: 1;
        height: 20px;
        background-color: #E7DFCF;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.2);  /* 내부 그림자 */
    }
    .importance-fill {
        height: 100%;
        animation: fillBar 1s ease-out;  /* 필바 채우기 애니메이션 */
    }
    .keyword-score {
        width: 100px;
        text-align: right;
        font-size: 0.9em;
        color: #666;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    @keyframes fillBar {
        from {
            width: 0%;
        }
    }
    .stButton>button {
        height: 2.4rem;
        margin-top: 1.55rem;
    }
    </style>

    <script>
    function animateKeywords() {
        // 키워드 항목들을 선택
        const keywords = document.querySelectorAll('.keyword-item');
        // 각 키워드 항목에 대해 애니메이션 적용
        keywords.forEach((keyword, index) => {
            setTimeout(() => {
                keyword.style.opacity = 1;
                keyword.style.transform = 'translateX(0)';
            }, index * 100);  // 항목마다 0.1초 간격으로 애니메이션 시작
        });
    }

    // 페이지 로드 완료 시 애니메이션 함수 호출
    document.addEventListener('DOMContentLoaded', animateKeywords);
    </script>
    """, unsafe_allow_html=True)
    
    st.logo("HectoLogo.png")  # 로고
    st.markdown(f"<h1 class='gradient-text'>{TEXTS['title']}</h1>", unsafe_allow_html=True)

    col1_text, col2_keyword = st.columns([3, 2])

    with col1_text:
        st.markdown(f"<h3 class='subheader'>{TEXTS['content_title']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='text-content'>{st.session_state.highlighted_text}</div>", unsafe_allow_html=True)

    with col2_keyword:
        st.markdown(f"<h3 class='subheader'>{TEXTS['keywords_title']}</h3>", unsafe_allow_html=True)
        keyword_count = st.slider(TEXTS['keyword_count_label'], MIN_KEYWORD_COUNT, MAX_KEYWORD_COUNT, DEFAULT_KEYWORD_COUNT)
        
        with st.form(key='add_keyword_form'):
            col_input, col_button = st.columns([3, 1])
            with col_input:
                # 사용자 키워드 입력 필드
                new_keyword = st.text_input("새로운 키워드를 추가할까요?", "")
            with col_button:
                add_keyword = st.form_submit_button("추가", use_container_width=True)  
        
        # 알림 메시지를 두 열 아래에 표시
        if add_keyword:
            if new_keyword and len(new_keyword) >= MIN_WORD_LENGTH:
                st.session_state.add_num += 1
                show_temporary_message(f"성공적으로 '{new_keyword}'를 추가했습니다.", "success", 3)
                insert_new_keyword(new_keyword,keyword_count)
            else:
                show_temporary_message(f"키워드는 최소 {MIN_WORD_LENGTH}자 이상이어야 합니다.", "warning", 3)

        col_extract, col_reset  = st.columns(2)
        
        with col_extract:
            if st.button(TEXTS['extract_button'], key="extract_button", use_container_width=True):
                total_keywords = keyword_count + len(st.session_state.custom_keywords)
                keyword_Extract(total_keywords)
        
        with col_reset :
            if st.button(TEXTS['reset_button'], key="reset_button", use_container_width=True):
                reset_state()
                st.session_state.custom_keywords = {}  # 커스텀 키워드도 초기화
                st.experimental_rerun()

        if st.session_state.keywords:
            for i, ((keyword, score), color) in enumerate(zip(st.session_state.keywords, st.session_state.colors)):
                rgb = [int(c) for c in color[4:-1].split(',')]
                lighter_color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.6)"
                importance = int(score * 100)  # 점수를 퍼센트로 변환하여 중요도로 사용
                st.markdown(f"""
                <div class='keyword-item' style='animation-delay: {i*0.1}s;'>
                    <div class='keyword-text'>{keyword}</div>
                    <div class='importance-bar'>
                        <div class='importance-fill' style='width: {importance}%; background: linear-gradient(to right, {color}, {lighter_color});'></div>
                    </div>
                    <div class='keyword-score'>{importance}</div>
                </div>
                """, unsafe_allow_html=True)
        
    

if __name__ == "__main__":
    main()  # 메인 함수 실행
