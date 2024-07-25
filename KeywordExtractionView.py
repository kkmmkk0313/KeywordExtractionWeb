import streamlit as st
import re
from functools import lru_cache
import random
import time
import colorsys

# Configuration
MIN_KEYWORD_COUNT = 3
MAX_KEYWORD_COUNT = 10
DEFAULT_KEYWORD_COUNT = 5
MIN_WORD_LENGTH = 2

# Localization
TEXTS = {
    'title': "Keyword Explorer 🚀",
    'keyword_count_label': "Number of Keywords",
    'extract_button': "Extract Keywords",
    'reset_button': "Reset",
    'content_title': "Original Text",
    'keywords_title': "Extracted Keywords",
    'error_message': "An error occurred while extracting keywords: "
}

# Sample text (이전과 동일)
DEMO_TEXT = """
헥토헬스케어, '드시모네로 자란다, 드시모네가 잘한다' 캠페인 오픈

IT헬스케어기업 헥토헬스케어가 드시모네와 함께 성장하는 아이들을 응원하는 의미로 7월 한 달간 '드시모네로 자란다, 드시모네가 잘한다' 캠페인을 진행한다.

이번 캠페인에서는 드시모네 프로바이오틱스와 함께 건강하게 성장하는 아이들의 모습을 담은 캠페인 영상을 다양한 온·오프라인 채널을 통해 공개한다. 영상에는 식약처로부터 '장 면역을 조절해 장 건강에 도움을 줄 수 있음'을 개별인정 받아 안전성과 기능성을 검증 받은 드시모네 프로바이오틱스를 통해 아이가 건강하게 자라길 바란다는 마음을 담았다.

더불어 베이비, 키즈, 패밀리 등 생애주기별 맞춤 세트를 최대 34% 특가로 만날 수 있다. 국내 최대 함량 프로바이오틱스 드시모네4500 세트를 구매하면 19% 혜택과 함께 법랑웨어 브랜드 크로우캐년 시리얼 세트와 멀티비타민을, 성장하는 어린이를 위한 드시모네 키즈 세트 구매시 최대 34% 혜택과 또박케어LAB(랩) 키즈 멀티비타민 구미, 미니 보냉백을 증정한다.

고객 참여 이벤트, 구매왕 이벤트 등 다양한 이벤트와 선물도 마련했다. 먼저 캠페인 기간 중 제품을 구매한 고객 전원에게 네이버페이 5000원권을 증정한다. 드시모네가 인정 받은 기능성 관련 퀴즈를 맞추면 총 10명을 추첨해 50만원 상당의 '우리가족 건강세트'를 제공한다. 이외에도 구매왕으로 선정된 8명에게는 제주 히든클리프 호텔 숙박권을 증정한다. 캠페인 관련 자세한 내용은 드시모네 홈페이지 및 앱을 통해 확인 가능하다.

드시모네 유산균은 세계적인 유산균 권위자이자 의사인 이탈리아의 클라우디오 드시모네(Claudio De Simone) 교수가 개발한 드시모네 포뮬러를 원료로 한다. 장 건강에 유익한 8가지 생균을 이상적으로 배합한 드시모네 포뮬러는 260편 이상의 SCI 등재 논문을 통해 세계적으로 우수성과 안전성을 인정 받았다. 특히 생애주기 및 장 환경에 따라 ▲베이비 스텝 1(3 ~ 12개월), 2(12 ~ 24개월) ▲키즈 스텝 1(3 ~ 7세), 2(8 ~ 13세) ▲키즈 프리미엄(3 ~ 13세) 등 다양한 제품을 선택할 수 있다.

헥토헬스케어 관계자는 "베이비, 키즈, 패밀리까지 온 가족이 장 건강과 장 면역을 챙길 수 있도록 특별한 캠페인 혜택을 마련했다"며 "프리미엄 프로바이오틱스 드시모네를 합리적인 가격에 경험할 수 있는 이번 캠페인 혜택을 놓치지 마시길 바란다"고 말했다.
"""

# 전역 변수로 키워드와 점수를 정의 (이전과 동일)
KEYWORDS_AND_SCORES = {
    "드시모네" : 0.9528017722366333,
    "헥토헬스케어": 0.705151011981070042,
    "유산균": 0.9140244722366333,
    "장": 0.120146906375885,
    "안전성": 0.005151011981070042,
    "캠페인": 0.0,
    "키즈": 0.307547390460968,
    "영상": 0.1891193687915802,
    "응원": 0.18563103675842285,
    "패밀리": 0.09801000356674194,
    "건강": 0.56248614937067032,
    "오프라인": 0.07405633479356766,
    "면역": 0.451058072596788406,
    "자란다": 0.03860612213611603,
    "어린이": 0.03225423023104668,
    "아이": 0.030163010582327843,
    "이벤트": 0.00464617321267724
}

@lru_cache(maxsize=None)
def get_keywords(_, n):
    try:
        sorted_keywords = sorted(KEYWORDS_AND_SCORES.items(), key=lambda x: x[1], reverse=True)[:n]
        max_score = max(score for _, score in sorted_keywords)
        return [(word, round(score, 5), min(int(score / max_score * 100), 100)) for word, score in sorted_keywords]
    except Exception as e:
        st.error(f"{TEXTS['error_message']}{str(e)}")
        return []

def generate_softer_colors(n):
    hue_step = 1.0 / n
    colors = []
    for i in range(n):
        hue = i * hue_step
        saturation = 0.3 + random.random() * 0.3  # 30-60% saturation 채도
        value = 0.8 + random.random() * 0.2  # 80-100% value 명도
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)   # 겹치지 않게
        colors.append(f"rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})")
    random.shuffle(colors)  # Shuffle to avoid predictable color order
    return colors

def create_highlighted_text(text, keywords, colors):
    highlighted_text = text
    for (keyword, _, _), color in zip(keywords, colors):
        pattern = re.compile(re.escape(keyword), re.IGNORECASE | re.UNICODE)
        replacement = f'<span class="keyword" style="background-color: {color};">\g<0></span>'
        highlighted_text = pattern.sub(replacement, highlighted_text)
    return highlighted_text

def update_state(keywords, highlighted_text):
    st.session_state.keywords = keywords
    st.session_state.highlighted_text = highlighted_text

def reset_state():
    update_state([], DEMO_TEXT)

def setup_page_config():
    st.set_page_config(layout="wide", page_title=TEXTS['title'], page_icon="🚀")

def initialize_session_state():
    if 'keywords' not in st.session_state:
        st.session_state.keywords = []
    if 'highlighted_text' not in st.session_state:
        st.session_state.highlighted_text = DEMO_TEXT

def main():
    setup_page_config()
    initialize_session_state()

    st.markdown(f"<h1 class='gradient-text'>{TEXTS['title']}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"<h3 class='subheader'>{TEXTS['content_title']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='text-content'>{st.session_state.highlighted_text}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<h3 class='subheader'>{TEXTS['keywords_title']}</h3>", unsafe_allow_html=True)
        keyword_count = st.slider(TEXTS['keyword_count_label'], MIN_KEYWORD_COUNT, MAX_KEYWORD_COUNT, DEFAULT_KEYWORD_COUNT)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(TEXTS['extract_button'], key="extract_button", use_container_width=True):
                with st.spinner('키워드를 추출하는 중...'):
                    time.sleep(1.2)          
                keywords = get_keywords(DEMO_TEXT, keyword_count)
                colors = generate_softer_colors(len(keywords))
                highlighted_text = create_highlighted_text(DEMO_TEXT, keywords, colors)
                update_state(keywords, highlighted_text)
                st.session_state.colors = colors  # Store colors in session state

                st.balloons()
                st.experimental_rerun()
        
        with col2:
            if st.button(TEXTS['reset_button'], key="reset_button", use_container_width=True):
                reset_state()
                st.experimental_rerun()

        if st.session_state.keywords:
            for i, ((keyword, freq, importance), color) in enumerate(zip(st.session_state.keywords, st.session_state.colors)):
                rgb = [int(c) for c in color[4:-1].split(',')]
                lighter_color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.6)"
                st.markdown(f"""
                <div class='keyword-item' style='animation-delay: {i*0.1}s;'>
                    <div class='keyword-text'>{keyword}</div>
                    <div class='importance-bar'>
                        <div class='importance-fill' style='width: {importance}%; background: linear-gradient(to right, {color}, {lighter_color});'></div>
                    </div>
                    <div class='keyword-score'>{freq}</div>
                </div>
                """, unsafe_allow_html=True)

    # Custom CSS and JS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    body {
        font-family: 'Poppins', sans-serif;
        background-color: #f0f2f6;
        color: #1e1e1e;
    }
    .gradient-text {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        color: #4a4a4a;
        border-bottom: 2px solid #4ecdc4;
        padding-bottom: 0.5rem;
    }
    .text-content {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 60vh;
        overflow-y: auto;
    }
    .keyword {
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .keyword:hover {
        filter: brightness(90%);
    }
    .keyword-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        animation: slideIn 0.5s ease-out forwards;
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
        box-shadow: inset 0 0 5px rgba(0,0,0,0.2);
    }
    .importance-fill {
        height: 100%;
        animation: fillBar 1s ease-out;
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
    </style>

    <script>
    function animateKeywords() {
        const keywords = document.querySelectorAll('.keyword-item');
        keywords.forEach((keyword, index) => {
            setTimeout(() => {
                keyword.style.opacity = 1;
                keyword.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }

    // Call the animation function when the page loads
    document.addEventListener('DOMContentLoaded', animateKeywords);
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
