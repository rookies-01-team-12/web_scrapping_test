import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# 페이지 설정
st.set_page_config(
    page_title="IT 채용정보 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

# 앱 제목
st.title("🚀 IT 채용정보 분석 대시보드")
st.write("이 대시보드는 CSV 파일 데이터를 기반으로 한 시각화 애플리케이션입니다.")

# 사이드바
st.sidebar.title("💻 검색 옵션")

# 데이터 로드 함수 - CSV 파일에서 직접 데이터 읽어오기
@st.cache_data
def load_data():
    try:
        # 정확한 파일 경로 지정
        file_path = 'data/merged_data_total.csv'
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        try:
            # 절대 경로 시도
            file_path = r'C:\Users\user\PJT1_job\project-data-scraping\data\merged_data_total.csv'
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            st.error("CSV 파일을 찾을 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return None

# 백엔드/프론트엔드 데이터 로드 함수
@st.cache_data
def load_backend_data():
    try:
        # 정확한 파일 경로 지정
        file_path = 'data/merged_data_backend.csv'
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        try:
            # 절대 경로 시도
            file_path = r'C:\Users\user\PJT1_job\project-data-scraping\data\merged_data_backend.csv'
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            st.warning("백엔드 데이터 파일을 찾을 수 없습니다.")
            return None
@st.cache_data
def load_frontend_data():
    try:
        # 정확한 파일 경로 지정
        file_path = 'data/merged_data_frontend.csv'
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        try:
            # 절대 경로 시도
            file_path = r'C:\Users\user\PJT1_job\project-data-scraping\data\merged_data_frontend.csv'
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            st.warning("프론트엔드 데이터 파일을 찾을 수 없습니다.")
            return None

# 데이터 로드
df_total = load_data()
df_back = load_backend_data()
df_front = load_frontend_data()

# 기존 그래프 그리기 함수 (plotly로 대체될 예정이지만 코드 유지)
def draw_bar(data, df_name):
    figure, ax = plt.subplots()
    figure.set_size_inches(18, 10)

    # 위에 만든 df의 column 하나씩 그래프로 그리기
    colors = sns.color_palette("hls", len(data.index))
    ax = sns.barplot(x=data.values, y=data.index, hue=data.index, palette=colors, ax=ax, dodge=False)  # dodge=False 추가
    ax.set_title(df_name, fontsize=20)
    ax.set_ylabel('')
    ax.legend(data.index, ncol=2, loc='lower right', labelcolor=colors, fontsize=16)

    # 각 bar 위에 해당하는 숫자를 넣기
    max_value = max(data.values)
    for j, (x_val, y_val) in enumerate(zip(data.index, data.values)):
        ax.text(x=y_val + max_value * 0.02, y=j, s=f'{y_val:.0f}', ha='center', va='center', fontsize=12, color=colors[j])
    
    return figure

def autopct_func(pct):
    return f'{pct:.1f}%'

def draw_circle(data, df_name):
    figure, ax = plt.subplots()
    figure.set_size_inches(20, 10)

    colors = sns.color_palette("hls", len(data.index))

    # 원형 그래프 그리기 autopct=비율 표시, pctdistance=중앙으로부터 pct거리, startangle=시작 각도
    autotexts = ax.pie(data.values, labels=data.index, colors=colors, autopct=autopct_func, pctdistance=0.8,
                      startangle=90, rotatelabels=False, textprops={'fontsize': 12})  # rotatelabels=False, labels=data.index 추가
    # 범례 위치 조정 및 겹침 방지
    ax.legend(data.index, ncol=3, loc='lower left', bbox_to_anchor=(0.0, 0.0), fontsize=10)
    ax.set_title(df_name, fontsize=20, x=0.5, y=1.05)  # 제목 위치 중앙으로 조정
    ax.axis('equal')  # 원이 찌그러지지 않게 1:1비율 고정

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # 범례와 제목이 겹치지 않도록 레이아웃 조정
    
    return figure

# Plotly로 동적 막대 그래프 그리기 함수
def draw_bar_plotly(data, title):
    # 데이터프레임으로 변환
    df = pd.DataFrame({'skill': data.index, 'count': data.values})
    
    # 애니메이션 효과를 위한 설정
    fig = go.Figure()
    
    # 막대 그래프 트레이스 추가
    fig.add_trace(go.Bar(
        x=df['count'],
        y=df['skill'],
        orientation='h',
        marker=dict(
            color=df['count'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="빈도")
        ),
        text=df['count'],
        textposition='outside',
        texttemplate='%{text:,}',
        hovertemplate='<b>%{y}</b><br>빈도: %{x:,}'
    ))
    
    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='빈도',
        yaxis_title='기술 스택',
        yaxis={'categoryorder':'total ascending'},
        height=600,
        margin=dict(l=100, r=20, t=70, b=70),
        # 애니메이션 효과 설정
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {
                    'label': '▶️ 애니메이션 재생',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}]
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 10},
            'showactive': False,
            'x': 0.1,
            'y': 1.15,
            'xanchor': 'right',
            'yanchor': 'top'
        }]
    )
    
    # 애니메이션 프레임 설정
    frames = []
    for i in range(1, len(df) + 1):
        subset = df.iloc[:i].copy()
        frame = go.Frame(
            data=[go.Bar(
                x=subset['count'],
                y=subset['skill'],
                orientation='h',
                marker=dict(
                    color=subset['count'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="빈도")
                ),
                text=subset['count'],
                textposition='outside',
                texttemplate='%{text:,}',
                hovertemplate='<b>%{y}</b><br>빈도: %{x:,}'
            )]
        )
        frames.append(frame)
    
    fig.frames = frames
    
    return fig

# Plotly로 동적 원형 그래프 그리기 함수
def draw_pie_plotly(data, title):
    # 데이터프레임으로 변환
    df = pd.DataFrame({'skill': data.index, 'count': data.values})
    
    # 애니메이션 효과를 위한 설정
    fig = go.Figure()
    
    # 원형 그래프 트레이스 추가
    fig.add_trace(go.Pie(
        labels=df['skill'],
        values=df['count'],
        textinfo='percent+label',
        insidetextorientation='radial',
        textposition='inside',
        hoverinfo='label+percent+value',
        marker=dict(
            colors=px.colors.qualitative.Vivid,
            line=dict(color='#000000', width=1)
        ),
    ))
    
    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=600,
        margin=dict(l=20, r=20, t=70, b=70),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        # 애니메이션 효과 설정
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {
                    'label': '▶️ 애니메이션 재생',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}]
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 10},
            'showactive': False,
            'x': 0.1,
            'y': 1.15,
            'xanchor': 'right',
            'yanchor': 'top'
        }]
    )
    
    # 애니메이션 프레임 설정
    frames = []
    # 순차적으로 조각을 추가하는 애니메이션
    for i in range(1, len(df) + 1):
        subset = df.iloc[:i].copy()
        frame = go.Frame(
            data=[go.Pie(
                labels=subset['skill'],
                values=subset['count'],
                textinfo='percent+label',
                insidetextorientation='radial',
                textposition='inside',
                hoverinfo='label+percent+value',
                marker=dict(
                    colors=px.colors.qualitative.Vivid[:i],
                    line=dict(color='#000000', width=1)
                ),
            )]
        )
        frames.append(frame)
    
    fig.frames = frames
    
    return fig

# skill row의 키워드 개수 count
def count_skills(df, exclude_skills=None):
    skill_counts = Counter()
    for index, row in df.iterrows():
        skills_str = row['skill']
        if pd.notna(skills_str):
            skills = [skill.strip().upper() for skill in skills_str.split(',')]
            skill_counts.update(skills)

    if exclude_skills:
        exclude_skills_upper = [skill.upper() for skill in exclude_skills]
        skill_counts = {skill: count for skill, count in skill_counts.items() if skill not in exclude_skills_upper}

    return pd.Series(skill_counts).sort_values(ascending=False)

if df_total is not None:
    # 사이드바에 검색 옵션 추가
    st.sidebar.subheader("🔍 키워드 검색")
    search_term = st.sidebar.text_input("검색어 입력 (회사명, 직무, 기술스택)")
    
    # 회사명 필터링 옵션
    all_companies = ['전체'] + sorted(df_total['company'].unique().tolist())
    selected_company = st.sidebar.selectbox("회사 선택", all_companies)
    
    # 기술 스택 검색 옵션
    common_skills = ['Java', 'Python', 'JavaScript', 'React', 'Spring', 'AWS', 'TypeScript', 'Docker', 'SQL', 'HTML']
    selected_skills = st.sidebar.multiselect("기술 스택 선택", common_skills)
    
    # 필터링 적용
    filtered_df = df_total.copy()
    
    # 검색어로 필터링
    if search_term:
        search_mask = (
            filtered_df['company'].str.contains(search_term, case=False, na=False) |
            filtered_df['position'].str.contains(search_term, case=False, na=False) |
            filtered_df['skill'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # 선택한 회사로 필터링
    if selected_company != '전체':
        filtered_df = filtered_df[filtered_df['company'] == selected_company]
    
    # 선택한 기술 스택으로 필터링
    for skill in selected_skills:
        filtered_df = filtered_df[filtered_df['skill'].str.contains(skill, case=False, na=False)]
    
    # 상단 요약 정보
    st.header("📈 채용정보 요약")
    
    # KPI 지표를 3개 컬럼으로 나눠 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="총 채용공고 수", value=f"{len(filtered_df):,}")
    
    with col2:
        company_count = filtered_df['company'].nunique()
        st.metric(label="기업 수", value=f"{company_count:,}")
        
    with col3:
        job_count = filtered_df['position'].nunique()
        st.metric(label="고유 직무 수", value=f"{job_count:,}")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 기업 분석", "🔍 직무 분석", "🧩 기술 스택 분석", "📋 데이터 테이블"])
    
     # 탭 1: 기업 분석
    with tab1:
        st.subheader("채용공고가 많은 상위 20개 기업")
        
        # 전체 기업 채용 공고 수 (상위 20개)
        company_counts = filtered_df['company'].value_counts().head(20).reset_index()
        company_counts.columns = ['company', 'count']
        
        if not company_counts.empty:
            # 애니메이션 프레임 설정
            animation_frames = []
            for i in range(1, 16):  # 15개 프레임
                subset = company_counts.copy()
                subset['animated_count'] = (subset['count'] * (i / 15)).round(1)
                frame = go.Frame(
                    data=[go.Bar(
                        x=subset['company'],
                        y=subset['animated_count'], 
                        marker=dict(
                            color=subset['animated_count'],
                            colorscale='Plasma',
                            showscale=True,
                            colorbar=dict(title="채용공고 수")
                        ),
                        text=subset['animated_count'].round(0).astype(int),
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>채용공고 수: %{y:,}'
                    )],
                    name=f'frame{i}'
                )
                animation_frames.append(frame)
            
            # 처음에는 빈 값으로 시작
            empty_y = [0] * len(company_counts)
            fig = go.Figure(
                data=[go.Bar(
                    x=company_counts['company'],
                    y=empty_y,
                    marker=dict(
                        color=empty_y,
                        colorscale='Plasma',
                        showscale=True,
                        colorbar=dict(title="채용공고 수")
                    ),
                    text=empty_y,
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>채용공고 수: %{y:,}'
                )],
                layout=go.Layout(
                    xaxis_title='기업',
                    yaxis_title='채용공고 수',
                    height=600,
                    margin=dict(l=20, r=20, t=70, b=100),
                    updatemenus=[{
                        'type': 'buttons',
                        'buttons': [
                            {
                                'label': '▶️ 그래프 표시',
                                'method': 'animate',
                                'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True, 'mode': 'immediate'}]
                            }
                        ],
                        'direction': 'left',
                        'pad': {'r': 10, 't': 10},
                        'showactive': False,
                        'x': 0.5,
                        'y': 1.15,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }]
                ),
                frames=animation_frames
            )
            
            # y축 범위 설정 (최대값의 1.1배까지)
            ymax = max(company_counts['count']) * 1.1
            fig.update_layout(yaxis_range=[0, ymax])
            
            # x축 레이블 설정
            fig.update_layout(
                xaxis=dict(
                    tickangle=-45
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("필터링된 데이터가 없습니다.")
    
    # 탭 2: 직무 분석
    with tab2:
        st.subheader("상위 20개 직무")
        
        # 직무명(position) 열의 상위 빈도 항목 출력
        position_counts = filtered_df['position'].value_counts().head(20).reset_index()
        position_counts.columns = ['position', 'count']
        
        if not position_counts.empty:
            # 애니메이션 프레임 설정
            animation_frames = []
            for i in range(1, 16):  # 15개 프레임
                subset = position_counts.copy()
                subset['animated_count'] = (subset['count'] * (i / 15)).round(1)
                frame = go.Frame(
                    data=[go.Bar(
                        x=subset['animated_count'],
                        y=subset['position'],
                        orientation='h',
                        marker=dict(
                            color=subset['animated_count'],
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="채용공고 수")
                        ),
                        text=subset['animated_count'].round(0).astype(int),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>채용공고 수: %{x:,}'
                    )],
                    name=f'frame{i}'
                )
                animation_frames.append(frame)
            
            # 처음에는 빈 값으로 시작
            empty_x = [0] * len(position_counts)
            fig = go.Figure(
                data=[go.Bar(
                    x=empty_x,
                    y=position_counts['position'],
                    orientation='h',
                    marker=dict(
                        color=empty_x,
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="채용공고 수")
                    ),
                    text=empty_x,
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>채용공고 수: %{x:,}'
                )],
                layout=go.Layout(
                    xaxis_title='채용공고 수',
                    yaxis_title='직무',
                    yaxis={'categoryorder':'total ascending'},
                    height=600,
                    margin=dict(l=150, r=20, t=70, b=70),
                    updatemenus=[{
                        'type': 'buttons',
                        'buttons': [
                            {
                                'label': '▶️ 그래프 표시',
                                'method': 'animate',
                                'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True, 'mode': 'immediate'}]
                            }
                        ],
                        'direction': 'left',
                        'pad': {'r': 10, 't': 10},
                        'showactive': False,
                        'x': 0.5,
                        'y': 1.15,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }]
                ),
                frames=animation_frames
            )
            
            # x축 범위 설정 (최대값의 1.1배까지)
            xmax = max(position_counts['count']) * 1.1
            fig.update_layout(xaxis_range=[0, xmax])
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("필터링된 데이터가 없습니다.")
    
    # 탭 3: 기술 스택 분석
    with tab3:
        st.subheader("기술 스택 분석")

        excluded_skills = ['AI', 'UI', 'UIUX', 'NATIVE', 'BOOT', 'API', 'WEB', 'SW']

        if df_back is not None and df_front is not None:
            stack_tab1, stack_tab2, stack_tab3 = st.tabs(["전체 기술 스택", "백엔드 기술 스택", "프론트엔드 기술 스택"])

            stack_tabs = [stack_tab1, stack_tab2, stack_tab3]
            titles = ["전체 - 상위 15개 기술 스택", "백엔드 - 상위 15개 기술 스택", "프론트엔드 - 상위 15개 기술 스택"]
            data_sources = [filtered_df, df_back, df_front]
            colors = ['mediumseagreen', 'cornflowerblue', 'salmon']

            for tab, title, data_source, base_color in zip(stack_tabs, titles, data_sources, colors):
                with tab:
                    skill_counts = count_skills(data_source, exclude_skills=excluded_skills)
                    skill_df = skill_counts.head(15).reset_index()
                    skill_df.columns = ['skill', 'count']

                    st.subheader(title)

                    # 애니메이션 프레임 설정
                    animation_frames = []
                    for i in range(1, 16):  # 15개 프레임
                        current_values = (skill_df['count'] * (i / 15)).round(1)
                        frame = go.Frame(
                            data=[go.Bar(
                                x=skill_df['skill'],
                                y=current_values,
                                marker=dict(
                                    color=current_values,
                                    colorscale='Plasma'
                                ),
                                text=current_values.round(0).astype(int),
                                textposition='outside',
                                hovertemplate='<b>%{x}</b><br>빈도: %{y:,}'
                            )],
                            name=f'frame{i}'
                        )
                        animation_frames.append(frame)

                    # 처음에는 값이 0인 빈 바 차트로 시작
                    empty_y = [0] * len(skill_df)
                    fig = go.Figure(
                        data=[go.Bar(
                            x=skill_df['skill'],
                            y=empty_y,  # 빈 값으로 시작
                            marker=dict(
                                color=empty_y,
                                colorscale='Plasma'
                            ),
                            text=empty_y,
                            textposition='outside',
                            hovertemplate='<b>%{x}</b><br>빈도: %{y:,}'
                        )],
                        layout=go.Layout(
                            xaxis_title='기술 스택',
                            yaxis_title='언급 빈도수',
                            height=600,
                            margin=dict(l=50, r=50, t=100, b=70),
                            # 애니메이션 버튼
                            updatemenus=[dict(
                                type='buttons',
                                showactive=False,
                                buttons=[dict(
                                    label='▶️ 그래프 표시',
                                    method='animate',
                                    args=[None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True, 'mode': 'immediate'}]
                                )],
                                x=0.5,
                                y=1.15,
                                xanchor='center',
                                yanchor='top'
                            )]
                        ),
                        frames=animation_frames
                    )

                    # y축 범위 설정 (최대값의 1.1배까지)
                    ymax = max(skill_df['count']) * 1.1
                    fig.update_layout(yaxis_range=[0, ymax])
                    
                    # x축 레이블 설정
                    fig.update_layout(
                        xaxis=dict(
                            tickangle=-45,
                            tickmode='array',
                            tickvals=skill_df['skill']
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("백엔드 또는 프론트엔드 데이터 파일을 찾을 수 없습니다.")
    # 탭 4: 데이터 테이블
    with tab4:
        st.subheader("데이터 테이블")
        
        # 페이지네이션을 위한 설정
        page_size = st.selectbox("페이지 크기", [10, 25, 50, 100])
        
        if not filtered_df.empty:
            total_pages = len(filtered_df) // page_size + (1 if len(filtered_df) % page_size > 0 else 0)
            page_number = st.number_input("페이지 번호", min_value=1, max_value=max(1, total_pages), value=1)
            
            # 현재 페이지 데이터 가져오기
            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_df))
            
            st.write(f"전체 {len(filtered_df)}개 중 {start_idx+1}~{end_idx}개 데이터를 표시합니다.")
            st.dataframe(filtered_df.iloc[start_idx:end_idx])
        else:
            st.info("필터링된 데이터가 없습니다.")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 IT 채용정보 분석 대시보드")
    
else:
    st.error("데이터를 불러오는데 실패했습니다. 파일 경로를 확인해주세요.")