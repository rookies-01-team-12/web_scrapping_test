import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events

# 예시 데이터
data = {
    "기술 스택": ["Python", "JavaScript", "Java", "C++", "Go"],
    "언급 횟수": [120, 90, 80, 60, 40]
}
fig = px.bar(data, x="기술 스택", y="언급 횟수", title="기술 스택 언급 횟수")

# 클릭 이벤트 처리
clicked_data = plotly_events(fig, click_event=True, key="bar_click")

# 결과 출력
if clicked_data:
    clicked_keyword = clicked_data[0]["x"]
    st.success(f"클릭한 키워드: {clicked_keyword}")
