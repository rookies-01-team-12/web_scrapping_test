import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from streamlit_plotly_events import plotly_events
import re

def autopct_func(pct):
    return f"{pct:.1f}%"


def count_skills(df, exclude_skills=None):
    skill_counts = Counter()
    for index, row in df.iterrows():
        skills_str = row["skill"]
        if pd.notna(skills_str):
            skills = [skill.strip().upper() for skill in skills_str.split(",")]
            skill_counts.update(skills)

    if exclude_skills:
        exclude_skills_upper = [skill.upper() for skill in exclude_skills]
        skill_counts = {
            skill: count
            for skill, count in skill_counts.items()
            if skill not in exclude_skills_upper
        }

    return pd.Series(skill_counts).sort_values(ascending=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_csv_data(file_name):
    try:
        # 상대 경로로 시도
        file_path = f"data/{file_name}"
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        try:
            # 절대 경로로 시도
            file_path = f"C:\\Users\\user\\PJT1_job\\project-data-scraping\\data\\{file_name}"
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            st.warning(f"{file_name} 파일을 찾을 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return None


def load_all_data():
    data = {
        'total': load_csv_data("merged_data_total.csv"),
        'backend': load_csv_data("merged_data_backend.csv"),
        'frontend': load_csv_data("merged_data_frontend.csv")
    }
    return data

def create_animated_bar_chart(data_df, x_col, y_col, title, orientation="v", color_scale="Plasma"):

    if data_df.empty:
        return None
        
    # 애니메이션 프레임 설정 - 최적화
    animation_frames = []
    # 최대 8개 프레임으로 제한
    for i in range(1, 8):
        subset = data_df.copy()
        subset["animated_count"] = (subset[y_col] * (i / 7)).round(1)
        
        if orientation == "h":
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=subset["animated_count"],
                        y=subset[x_col],
                        orientation="h",
                        marker=dict(
                            color=subset["animated_count"],
                            colorscale=color_scale,
                            showscale=True,
                            colorbar=dict(title="빈도"),
                        ),
                        text=subset["animated_count"].round(0).astype(int),
                        textposition="outside",
                        hovertemplate="<b>%{y}</b><br>빈도: %{x:,}",
                    )
                ],
                name=f"frame{i}",
            )
        else:
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=subset[x_col],
                        y=subset["animated_count"],
                        marker=dict(
                            color=subset["animated_count"],
                            colorscale=color_scale,
                            showscale=True,
                            colorbar=dict(title="빈도"),
                        ),
                        text=subset["animated_count"].round(0).astype(int),
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>빈도: %{y:,}",
                    )
                ],
                name=f"frame{i}",
            )
        animation_frames.append(frame)

    # 처음에는 빈 값으로 시작
    empty_vals = [0] * len(data_df)
    
    # 그래프 생성
    if orientation == "h":
        fig = go.Figure(
            data=[
                go.Bar(
                    x=empty_vals,
                    y=data_df[x_col],
                    orientation="h",
                    marker=dict(
                        color=empty_vals,
                        colorscale=color_scale,
                        showscale=True,
                        colorbar=dict(title="빈도"),
                    ),
                    text=empty_vals,
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>빈도: %{x:,}",
                )
            ],
            frames=animation_frames,
        )
        
        # x축 범위 설정 (최대값의 1.1배까지)
        xmax = max(data_df[y_col]) * 1.1
        fig.update_layout(
            xaxis_title="빈도",
            yaxis_title="",
            xaxis_range=[0, xmax],
            yaxis={"categoryorder": "total ascending"},
        )
    else:
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data_df[x_col],
                    y=empty_vals,
                    marker=dict(
                        color=empty_vals,
                        colorscale=color_scale,
                        showscale=True,
                        colorbar=dict(title="빈도"),
                    ),
                    text=empty_vals,
                    textposition="outside",
                    hovertemplate="<b>%{x}</b><br>빈도: %{y:,}",
                )
            ],
            frames=animation_frames,
        )
        
        # y축 범위 설정 (최대값의 1.1배까지)
        ymax = max(data_df[y_col]) * 1.1
        fig.update_layout(
            xaxis_title="",
            yaxis_title="빈도", 
            yaxis_range=[0, ymax],
            xaxis=dict(tickangle=-45),
        )

    # 공통 레이아웃 설정
    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        height=600,
        margin=dict(l=20 if orientation == "v" else 150, r=20, t=70, b=100 if orientation == "v" else 70),
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "▶️ 그래프 표시",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 200, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 10},
                "showactive": False,
                "x": 0.5,
                "y": 1.15,
                "xanchor": "center",
                "yanchor": "top",
            }
        ],
    )

    return fig


def create_clickable_bar_chart(data_df, title, key_prefix):
    """
    클릭 가능한 막대 그래프를 생성하는 함수
    
    Args:
        data_df: skill과 count 컬럼이 있는 데이터프레임
        title: 그래프 제목
        key_prefix: 고유한 키를 만들기 위한 접두사
    """
    # 그래프 고유 키 생성
    graph_key = f"{key_prefix}_{st.session_state.render_id}"
    
    # Plotly 그래프 생성
    fig = px.bar(
        data_df,
        x="skill", 
        y="count",
        title=title,
        color="count",
        color_continuous_scale="Viridis",
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=40, r=40, t=60, b=60),
        title_x=0.5,
    )
    
    # 클릭 이벤트 처리
    clicked = plotly_events(fig, click_event=True, key=graph_key)
    
    # 클릭 이벤트 처리 로직
    if clicked:
        with st.spinner('데이터 처리 중...'):
            selected_keyword = clicked[0]['x']
            if selected_keyword not in st.session_state.selected_skills:
                st.session_state.selected_skills.append(selected_keyword)
                # render_id를 증가시켜 다음 렌더링에서 새 키를 사용
                st.session_state.render_id += 1
    
    # 선택된 스킬 표시 - 별도 컨테이너에 표시
    with st.container():
        if st.session_state.selected_skills:
            st.write("선택된 기술 스택:", ", ".join(st.session_state.selected_skills))
            
            # 선택 초기화 버튼 추가
            if st.button("선택 초기화", key=f"clear_{key_prefix}"):
                st.session_state.selected_skills = []
                st.session_state.render_id += 1
                st.rerun()


def setup_page():
    st.set_page_config(
        page_title="IT 채용정보 분석 대시보드", 
        page_icon="📊", 
        layout="wide"
    )
    
    # 세션 상태 초기화
    if 'selected_skills' not in st.session_state:
        st.session_state.selected_skills = []
    if 'render_id' not in st.session_state:
        st.session_state.render_id = 0
    
    # 앱 제목
    st.title("🚀 IT 채용정보 분석")

def render_sidebar(data):
    st.sidebar.title("💻 검색 옵션")
    
    # 필터링 옵션 추가
    st.sidebar.subheader("🔍 키워드 검색")
    search_term = st.sidebar.text_input("검색어 입력 (회사명, 직무, 기술스택)")
    
    # 회사명 필터링 옵션
    all_companies = ["전체"] + sorted(data['total']["company"].unique().tolist())
    selected_company = st.sidebar.selectbox("회사 선택", all_companies)
    
    # 기술 스택 검색 옵션
    common_skills = [
        "Java", "Python", "JavaScript", "React", "Spring", 
        "AWS", "TypeScript", "Docker", "SQL", "HTML",
    ]
    selected_skills = st.sidebar.multiselect("기술 스택 선택", common_skills)
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 IT 채용정보 분석 대시보드")
    
    return search_term, selected_company, selected_skills


def filter_data(df, search_term, selected_company, selected_skills):
    filtered_df = df.copy()
    
    # 검색어로 필터링
    if search_term:
        search_mask = (
            filtered_df["company"].str.contains(search_term, case=False, na=False)
            | filtered_df["position"].str.contains(search_term, case=False, na=False)
            | filtered_df["skill"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # 선택한 회사로 필터링
    if selected_company != "전체":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]
    
    # 선택한 기술 스택으로 필터링
    for skill in selected_skills:
        filtered_df = filtered_df[
            filtered_df["skill"].str.contains(skill, case=False, na=False)
        ]
    
    return filtered_df


def render_summary_metrics(filtered_df):
    st.header("📈 채용정보 요약")
    
    # KPI 지표를 3개 컬럼으로 나눠 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="총 채용공고 수", value=f"{len(filtered_df):,}")
    
    with col2:
        company_count = filtered_df["company"].nunique()
        st.metric(label="기업 수", value=f"{company_count:,}")
    
    with col3:
        job_count = filtered_df["position"].nunique()
        st.metric(label="고유 직무 수", value=f"{job_count:,}")


def render_company_analysis(filtered_df):
    st.subheader("채용공고가 많은 상위 20개 기업")
    
    # 전체 기업 채용 공고 수 (상위 20개)
    company_counts = filtered_df["company"].value_counts().head(20).reset_index()
    company_counts.columns = ["company", "count"]
    
    if not company_counts.empty:
        fig = create_animated_bar_chart(
            company_counts, 
            x_col="company", 
            y_col="count", 
            title="",
            orientation="v",
            color_scale="Plasma"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("필터링된 데이터가 없습니다.")


def render_job_analysis(filtered_df):
    """직무 분석 탭 렌더링"""
    st.subheader("상위 20개 직무")
    
    # 직무명(position) 열의 상위 빈도 항목 출력
    position_counts = filtered_df["position"].value_counts().head(20).reset_index()
    position_counts.columns = ["position", "count"]
    
    if not position_counts.empty:
        fig = create_animated_bar_chart(
            position_counts, 
            x_col="position", 
            y_col="count", 
            title="", 
            orientation="h",
            color_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("필터링된 데이터가 없습니다.")


def render_skill_analysis(data, filtered_df):
    """기술 스택 분석 탭 - session_state 수정 오류 해결"""
    st.subheader("기술 스택 분석")
    
    # 제외할 스킬 목록 정의
    excluded_skills = ["AI", "UI", "UIUX", "NATIVE", "BOOT", "API", "WEB", "SW"]
    
    # 현재 활성 탭 추적을 위한 세션 상태 초기화
    if 'active_stack_tab' not in st.session_state:
        st.session_state.active_stack_tab = "total"
    
    # 탭별 선택된 스킬 추적
    if 'tab_skills' not in st.session_state:
        st.session_state.tab_skills = {"total": [], "backend": [], "frontend": []}
    
    # 선택 추가 상태 관리
    if 'add_skill' not in st.session_state:
        st.session_state.add_skill = {"total": False, "backend": False, "frontend": False}
    
    # 선택 처리 함수 정의
    def handle_skill_selection(tab_name, skill):
        if skill != "선택하세요...":
            if skill not in st.session_state.tab_skills[tab_name]:
                st.session_state.tab_skills[tab_name].append(skill)
                st.session_state.add_skill[tab_name] = True
    
    if data['backend'] is not None and data['frontend'] is not None:
        # 스택별 분석을 위한 서브 탭 생성
        stack_tab1, stack_tab2, stack_tab3 = st.tabs(
            ["전체 기술 스택", "백엔드 기술 스택", "프론트엔드 기술 스택"]
        )
        
        # 전체 기술 스택 탭
        with stack_tab1:
            # 탭 선택 감지 및 처리
            prev_tab = st.session_state.active_stack_tab
            st.session_state.active_stack_tab = "total"
            
            # 전체 데이터 기술 스택 분석
            total_skill_counts = count_skills(
                filtered_df, exclude_skills=excluded_skills
            )
            
            # 데이터 준비
            skill_df = total_skill_counts.head(15).reset_index()
            skill_df.columns = ["skill", "count"]
            
            # 막대 그래프 생성
            fig = px.bar(
                skill_df,
                x="skill", 
                y="count",
                title="전체 기술 스택 상위 15개",
                color="count",
                color_continuous_scale="Viridis",
            )
            
            fig.update_layout(
                height=500,
                margin=dict(l=30, r=30, t=50, b=50),
                title_x=0.5,
                xaxis_tickangle=-45,
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 선택 추가 상태 확인 및 초기화
            if st.session_state.add_skill["total"]:
                st.session_state.add_skill["total"] = False
                st.rerun()
            
            # 기술 스택 선택용 셀렉트 박스 추가
            selected_skill = st.selectbox(
                "기술 스택 선택",
                ["선택하세요..."] + skill_df["skill"].tolist(),
                key="select_total"
            )
            
            # 선택 처리
            handle_skill_selection("total", selected_skill)
            
            # 선택된 스킬 표시
            with st.container():
                if st.session_state.tab_skills["total"]:
                    st.write("선택된 기술 스택:", ", ".join(st.session_state.tab_skills["total"]))
                    
        # 백엔드 기술 스택 탭
        with stack_tab2:
            # 탭 선택 감지 및 처리
            prev_tab = st.session_state.active_stack_tab
            st.session_state.active_stack_tab = "backend"
            
            # 백엔드 데이터 기술 스택 분석
            backend_skill_counts = count_skills(
                data['backend'], exclude_skills=excluded_skills
            )
            
            # 데이터 준비
            backend_skill_df = backend_skill_counts.head(15).reset_index()
            backend_skill_df.columns = ["skill", "count"]
            
            # 막대 그래프 생성
            fig = px.bar(
                backend_skill_df,
                x="skill", 
                y="count",
                title="백엔드 기술 스택 상위 15개",
                color="count",
                color_continuous_scale="Viridis",
            )
            
            fig.update_layout(
                height=500,
                margin=dict(l=30, r=30, t=50, b=50),
                title_x=0.5,
                xaxis_tickangle=-45,
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 선택 추가 상태 확인 및 초기화
            if st.session_state.add_skill["backend"]:
                st.session_state.add_skill["backend"] = False
                st.rerun()
            
            # 기술 스택 선택용 셀렉트 박스 추가
            selected_skill = st.selectbox(
                "기술 스택 선택",
                ["선택하세요..."] + backend_skill_df["skill"].tolist(),
                key="select_backend"
            )
            
            # 선택 처리
            handle_skill_selection("backend", selected_skill)
            
            # 선택된 스킬 표시
            with st.container():
                if st.session_state.tab_skills["backend"]:
                    st.write("선택된 기술 스택:", ", ".join(st.session_state.tab_skills["backend"]))
        
        # 프론트엔드 기술 스택 탭
        with stack_tab3:
            # 탭 선택 감지 및 처리
            prev_tab = st.session_state.active_stack_tab
            st.session_state.active_stack_tab = "frontend"
            
            # 프론트엔드 데이터 기술 스택 분석
            frontend_skill_counts = count_skills(
                data['frontend'], exclude_skills=excluded_skills
            )
            
            # 데이터 준비
            frontend_skill_df = frontend_skill_counts.head(15).reset_index()
            frontend_skill_df.columns = ["skill", "count"]
            
            # 막대 그래프 생성
            fig = px.bar(
                frontend_skill_df,
                x="skill", 
                y="count",
                title="프론트엔드 기술 스택 상위 15개",
                color="count",
                color_continuous_scale="Viridis",
            )
            
            fig.update_layout(
                height=500,
                margin=dict(l=30, r=30, t=50, b=50),
                title_x=0.5,
                xaxis_tickangle=-45,
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 선택 추가 상태 확인 및 초기화
            if st.session_state.add_skill["frontend"]:
                st.session_state.add_skill["frontend"] = False
                st.rerun()
            
            # 기술 스택 선택용 셀렉트 박스 추가
            selected_skill = st.selectbox(
                "기술 스택 선택",
                ["선택하세요..."] + frontend_skill_df["skill"].tolist(),
                key="select_frontend"
            )
            
            # 선택 처리
            handle_skill_selection("frontend", selected_skill)
            
            # 선택된 스킬 표시
            with st.container():
                if st.session_state.tab_skills["frontend"]:
                    st.write("선택된 기술 스택:", ", ".join(st.session_state.tab_skills["frontend"]))
                    
    
    else:
        st.info("백엔드 또는 프론트엔드 데이터 파일을 찾을 수 없습니다.")


def render_data_table(filtered_df):
    """데이터 테이블 탭 렌더링"""
    st.subheader("데이터 테이블")
    
    # 페이지네이션을 위한 설정
    page_size = st.selectbox("페이지 크기", [10, 25, 50, 100])
    
    if not filtered_df.empty:
        total_pages = len(filtered_df) // page_size + (
            1 if len(filtered_df) % page_size > 0 else 0
        )
        page_number = st.number_input(
            "페이지 번호", min_value=1, max_value=max(1, total_pages), value=1
        )
        
        # 현재 페이지 데이터 가져오기
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        
        st.write(
            f"전체 {len(filtered_df)}개 중 {start_idx+1}~{end_idx}개 데이터를 표시합니다."
        )
        st.dataframe(filtered_df.iloc[start_idx:end_idx])
    else:
        st.info("필터링된 데이터가 없습니다.")


def main():
    """메인 함수"""
    # 페이지 설정
    setup_page()
    
    # 데이터 로드
    data = load_all_data()
    
    if data['total'] is not None:
        # 사이드바 렌더링
        search_term, selected_company, selected_skills = render_sidebar(data)
        
        # 필터링 적용
        filtered_df = filter_data(data['total'], search_term, selected_company, selected_skills)
        
        # 요약 정보 렌더링
        render_summary_metrics(filtered_df)
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 기업 분석", "🔍 직무 분석", "🧩 기술 스택 분석", "📋 데이터 테이블"]
        )
        
        # 각 탭 렌더링
        with tab1:
            render_company_analysis(filtered_df)
        
        with tab2:
            render_job_analysis(filtered_df)
        
        with tab3:
            render_skill_analysis(data, filtered_df)
        
        with tab4:
            render_data_table(filtered_df)
    
    else:
        st.error("데이터를 불러오는데 실패했습니다. 파일 경로를 확인해주세요.")


if __name__ == "__main__":
    main()