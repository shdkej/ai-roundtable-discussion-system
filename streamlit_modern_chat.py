import streamlit as st
import os
import datetime
import time
from dotenv import load_dotenv
from chat_roundtable import ChatRoundtable, ChatMessage

# 환경 변수 로드
load_dotenv()

def get_avatar(sender):
    """발언자별 아바타 반환"""
    avatar_map = {
        "사용자": "👤",
        "시스템": "🔔",
        "토론 진행자": "🎭",
        "디자인팀 팀장 김창의": "🎨",
        "영업팀 팀장 박매출": "💼",
        "생산팀 팀장 이현실": "⚙️",
        "마케팅팀 팀장 최홍보": "📢",
        "IT팀 팀장 박테크": "💻"
    }
    return avatar_map.get(sender, "🤖")

def get_role_color(sender):
    """발언자별 색상 반환"""
    color_map = {
        "사용자": "#1f77b4",
        "시스템": "#2ca02c", 
        "토론 진행자": "#ff7f0e",
        "디자인팀 팀장 김창의": "#d62728",
        "영업팀 팀장 박매출": "#9467bd",
        "생산팀 팀장 이현실": "#8c564b",
        "마케팅팀 팀장 최홍보": "#e377c2",
        "IT팀 팀장 박테크": "#17becf"
    }
    return color_map.get(sender, "#7f7f7f")

def display_chat_message(msg, show_time=True, in_container=False):
    """채팅 메시지를 예쁘게 표시"""
    avatar = get_avatar(msg.sender)
    
    if in_container:
        # 컨테이너 내부에서는 HTML로 직접 렌더링
        color = get_role_color(msg.sender)
        time_str = msg.timestamp.strftime('%H:%M:%S') if show_time else ""
        
        if msg.message_type == "system":
            st.markdown(f"""
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <strong>🔔 {msg.sender}</strong><br>
                {msg.content}
                {f'<br><small style="color: #666;">⏰ {time_str}</small>' if show_time else ''}
            </div>
            """, unsafe_allow_html=True)
        elif msg.sender == "사용자":
            st.markdown(f"""
            <div style="background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 15px; margin-left: 50px;">
                <strong>👤 사용자</strong><br>
                {msg.content}
                {f'<br><small style="color: #666;">⏰ {time_str}</small>' if show_time else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            # 전문가 메시지
            bg_color = "#fff" if msg.message_type == "message" else "#e8f5e8" if msg.message_type == "conclusion" else "#fff3e0"
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 10px; margin: 10px 0; border-radius: 15px; margin-right: 50px; border: 1px solid #eee;">
                <strong style="color: {color};">{avatar} {msg.sender}</strong><br>
                {msg.content}
                {f'<br><small style="color: #666;">⏰ {time_str}</small>' if show_time else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        # 기존 chat_message 방식
        if msg.message_type == "system":
            with st.chat_message("assistant", avatar="🔔"):
                st.info(f"**{msg.sender}**\n\n{msg.content}")
                if show_time:
                    st.caption(f"⏰ {msg.timestamp.strftime('%H:%M:%S')}")
            return
        
        # 사용자 메시지
        if msg.sender == "사용자":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg.content)
                if show_time:
                    st.caption(f"⏰ {msg.timestamp.strftime('%H:%M:%S')}")
        else:
            # 전문가 메시지
            with st.chat_message("assistant", avatar=avatar):
                # 발언자 이름을 색상있게 표시
                color = get_role_color(msg.sender)
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{msg.sender}</span>", 
                           unsafe_allow_html=True)
                
                # 메시지 타입에 따른 스타일링
                if msg.message_type == "conclusion":
                    st.success(msg.content)
                elif msg.message_type == "response":
                    st.info(msg.content)
                elif msg.message_type == "question":
                    st.warning(msg.content)
                else:
                    st.markdown(msg.content)
                
                if show_time:
                    st.caption(f"⏰ {msg.timestamp.strftime('%H:%M:%S')}")

def handle_auto_discussion_update():
    """자동 토론 업데이트 처리"""
    if not st.session_state.chat_system or not st.session_state.chat_system.auto_discussion_enabled:
        return
    
    # 마지막 업데이트로부터 8초 이상 경과시 새 메시지 생성
    current_time = datetime.datetime.now()
    time_diff = (current_time - st.session_state.last_auto_update).total_seconds()
    
    if time_diff >= 8:  # 8초마다 새 메시지
        try:
            # 타이핑 상태가 아직 설정되지 않았다면 먼저 설정
            if not st.session_state.generating_response:
                st.session_state.generating_response = True
                st.rerun()
                return
            
            # 실제 응답 생성
            new_msg = st.session_state.chat_system.generate_auto_response()
            if new_msg:
                st.session_state.chat_messages.append(new_msg)
                st.session_state.last_auto_update = current_time
                st.session_state.generating_response = False
                
                # 사용자 개입이 요청된 경우 자동 업데이트 중지
                if st.session_state.chat_system.user_intervention_pending:
                    st.session_state.auto_discussion_enabled = False
                
                st.rerun()
        except Exception as e:
            st.error(f"자동 토론 중 오류 발생: {str(e)}")
            st.session_state.auto_discussion_enabled = False
            st.session_state.generating_response = False

def setup_auto_refresh():
    """자동 새로고침 설정"""
    if (st.session_state.chat_system and 
        st.session_state.chat_system.auto_discussion_enabled and 
        not st.session_state.chat_system.user_intervention_pending):
        
        # 더 빠른 새로고침으로 실시간 느낌 향상
        st.markdown("""
        <script>
        setTimeout(function() {
            if (window.location.href.indexOf('streamlit') !== -1) {
                window.location.reload();
            }
        }, 2000);
        </script>
        """, unsafe_allow_html=True)

def display_auto_discussion_status():
    """자동 토론 상태 표시"""
    if not st.session_state.chat_system:
        return
    
    # 응답 생성 중일 때
    if getattr(st.session_state, 'generating_response', False):
        next_speaker = st.session_state.chat_system.current_speaker
        speaker_name = next_speaker.role if next_speaker else "전문가"
        avatar = get_avatar(speaker_name)
        
        st.markdown(f"""
        <div class="typing-indicator">
            {avatar} <b>{speaker_name}</b>이(가) 답변을 준비하고 있습니다...
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.chat_system.auto_discussion_enabled:
        current_time = datetime.datetime.now()
        time_diff = (current_time - st.session_state.last_auto_update).total_seconds()
        next_response_in = max(0, 8 - time_diff)
        
        if next_response_in > 0:
            st.markdown(f"""
            <div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 10px;">
                🤖 자동 토론 진행 중 • 다음 발언까지 {int(next_response_in)}초
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.chat_system.user_intervention_pending:
        st.markdown(f"""
        <div class="typing-indicator" style="background: #ffe6e6; border: 2px solid #ff6b6b;">
            ✋ <b>사용자 발언을 기다리고 있습니다!</b>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="KS 채팅형 원탁토론",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 현대적인 CSS 스타일링
    st.markdown("""
    <style>
    .main-title {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        width: 100%;
    }
    
    .expert-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* 채팅 입력 영역 스타일 */
    .stChatInput {
        position: sticky;
        bottom: 0;
        background: white;
        z-index: 100;
    }
    
    /* 현재 발언자 애니메이션 */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }
        100% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
    }
    
    .speaking-indicator {
        animation: glow 2s ease-in-out infinite;
    }
    
    /* 채팅 컨테이너 스타일 */
    .chat-container-fixed {
        height: 500px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        background: #fafafa;
        margin-bottom: 1rem;
    }
    
    /* 타이핑 인디케이터 */
    .typing-indicator {
        background: #f0f2f6;
        border-radius: 20px;
        padding: 10px 15px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .typing-dots {
        display: flex;
        gap: 3px;
        margin-left: 10px;
    }
    
    .typing-dot {
        width: 6px;
        height: 6px;
        background: #667eea;
        border-radius: 50%;
        animation: typing-bounce 1.4s ease-in-out infinite both;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typing-bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 타이틀
    st.markdown('<h1 class="main-title">💬 KS 채팅형 원탁토론</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">실시간 채팅으로 전문가들과 토론하세요</p>', unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'chat_system' not in st.session_state:
        st.session_state.chat_system = None
    if 'discussion_started' not in st.session_state:
        st.session_state.discussion_started = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'auto_discussion_enabled' not in st.session_state:
        st.session_state.auto_discussion_enabled = False
    if 'last_auto_update' not in st.session_state:
        st.session_state.last_auto_update = datetime.datetime.now()
    if 'generating_response' not in st.session_state:
        st.session_state.generating_response = False
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 토론 설정")
        
        # 토론이 시작되지 않은 경우에만 설정 가능
        if not st.session_state.discussion_started:
            # 토론 주제
            st.subheader("📋 토론 주제")
            default_topics = [
                "새로운 프리미엄 제품 라인 출시 전략",
                "고객 불만 대응을 위한 품질 개선 방안", 
                "비용 절감을 위한 생산 프로세스 혁신",
                "ESG 경영을 위한 친환경 제품 개발",
                "디지털 전환을 통한 업무 효율성 향상"
            ]
            
            topic_method = st.radio(
                "주제 선택 방식",
                ["추천 주제", "직접 입력"],
                horizontal=True
            )
            
            if topic_method == "추천 주제":
                topic = st.selectbox("토론 주제", default_topics, index=0)
            else:
                topic = st.text_input("직접 입력", placeholder="토론 주제를 입력하세요...")
            
            # 참석자 선택
            st.subheader("👥 참석자 선택")
            all_participants = [
                "디자인팀 김창의",
                "영업팀 박매출", 
                "생산팀 이현실",
                "마케팅팀 최홍보",
                "IT팀 박테크"
            ]
            
            participants = st.multiselect(
                "참여할 팀 선택",
                all_participants,
                default=all_participants[:3]
            )
            
            # 회사 정보 (간소화)
            with st.expander("🏢 회사 정보", expanded=False):
                company_size = st.text_input("회사 규모", value="중견 제조업체")
                industry = st.text_input("사업 분야", value="아웃도어 의류")
                revenue = st.text_input("연 매출", value="800억원")
                current_challenge = st.text_area("주요 과제", placeholder="해결하고 싶은 문제...")
            
            # 토론 시작 버튼
            if st.button("🚀 채팅 토론 시작", type="primary"):
                if not topic or len(participants) < 3:
                    st.error("주제와 최소 3명의 참석자를 선택해주세요.")
                elif not os.getenv("OPENAI_API_KEY"):
                    st.error("OpenAI API 키가 설정되지 않았습니다.")
                else:
                    # 컨텍스트 구성
                    context = {
                        'company_size': company_size,
                        'industry': industry,
                        'revenue': revenue,
                        'current_challenge': current_challenge
                    }
                    
                    # 채팅 시스템 초기화
                    with st.spinner("토론을 준비하는 중..."):
                        st.session_state.chat_system = ChatRoundtable()
                        start_msg = st.session_state.chat_system.start_discussion(topic, context, participants)
                        st.session_state.discussion_started = True
                        st.session_state.chat_messages = [start_msg]
                        
                        # 초기 의견 수집
                        initial_opinions = st.session_state.chat_system.get_initial_opinions()
                        st.session_state.chat_messages.extend(initial_opinions)
                    
                    st.success("토론이 시작되었습니다!")
                    st.rerun()
        
        else:
            # 토론 중 도구들
            st.success("✅ 토론 진행 중")
            
            # 자동 토론 제어
            st.subheader("🤖 자동 토론")
            
            col1, col2 = st.columns(2)
            with col1:
                if not st.session_state.chat_system.auto_discussion_enabled:
                    if st.button("▶️ 시작", use_container_width=True, type="primary"):
                        start_msg = st.session_state.chat_system.start_auto_discussion()
                        st.session_state.chat_messages.append(start_msg)
                        st.session_state.auto_discussion_enabled = True
                        st.rerun()
                else:
                    if st.button("⏸️ 일시정지", use_container_width=True):
                        pause_msg = st.session_state.chat_system.pause_auto_discussion()
                        st.session_state.chat_messages.append(pause_msg)
                        st.session_state.auto_discussion_enabled = False
                        st.rerun()
            
            with col2:
                if st.session_state.chat_system.discussion_state == "paused":
                    if st.button("🔄 재개", use_container_width=True):
                        resume_msg = st.session_state.chat_system.resume_auto_discussion()
                        st.session_state.chat_messages.append(resume_msg)
                        st.session_state.auto_discussion_enabled = True
                        st.rerun()
                elif st.session_state.chat_system.auto_discussion_enabled:
                    if st.button("✋ 개입요청", use_container_width=True):
                        intervention_msg = st.session_state.chat_system.request_user_intervention()
                        st.session_state.chat_messages.append(intervention_msg)
                        st.rerun()
            
            # 빠른 기능 버튼들
            st.subheader("⚡ 빠른 기능")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 결론", use_container_width=True):
                    with st.spinner("결론 정리 중..."):
                        conclusion = st.session_state.chat_system.get_conclusion()
                        st.session_state.chat_messages.append(conclusion)
                    st.rerun()
            
            with col2:
                if st.button("💾 저장", use_container_width=True):
                    filename = st.session_state.chat_system.save_chat_log()
                    st.success(f"저장됨: {filename}")
            
            # 고급 기능
            with st.expander("🧠 고급 기능"):
                if st.button("🔍 심화 질문", use_container_width=True):
                    st.session_state.show_deep_dive = not getattr(st.session_state, 'show_deep_dive', False)
                    st.rerun()
                
                if st.button("💡 브레인스토밍", use_container_width=True):
                    st.session_state.show_brainstorm = not getattr(st.session_state, 'show_brainstorm', False)
                    st.rerun()
                
                if st.button("📋 실행 계획", use_container_width=True):
                    st.session_state.show_implementation = not getattr(st.session_state, 'show_implementation', False)
                    st.rerun()
            
            # 참석자 현황
            st.subheader("👥 참석자")
            experts = [
                ("🎨", "김창의", "디자인"),
                ("💼", "박매출", "영업"),  
                ("⚙️", "이현실", "생산"),
                ("📢", "최홍보", "마케팅"),
                ("💻", "박테크", "IT")
            ]
            
            for emoji, name, dept in experts:
                st.markdown(f"<div class='expert-card'>{emoji} <b>{name}</b><br><small>{dept} 전문가</small></div>", 
                           unsafe_allow_html=True)
            
            # 토론 통계
            st.subheader("📊 토론 현황")
            if st.session_state.chat_messages:
                total_messages = len(st.session_state.chat_messages)
                start_time = st.session_state.chat_messages[0].timestamp
                duration = (datetime.datetime.now() - start_time).seconds // 60
                discussion_rounds = st.session_state.chat_system.discussion_rounds
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>{total_messages}</h3>
                    <p>총 메시지</p>
                </div>
                <div class='metric-card'>
                    <h3>{duration}분</h3>
                    <p>토론 시간</p>
                </div>
                <div class='metric-card'>
                    <h3>{discussion_rounds}</h3>
                    <p>토론 라운드</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 토론 재시작
            if st.button("🔄 새 토론 시작", use_container_width=True):
                st.session_state.chat_system = None
                st.session_state.discussion_started = False
                st.session_state.chat_messages = []
                st.session_state.auto_discussion_enabled = False
                st.session_state.generating_response = False
                st.session_state.last_auto_update = datetime.datetime.now()
                # 임시 상태들도 초기화
                for key in list(st.session_state.keys()):
                    if key.startswith('show_'):
                        del st.session_state[key]
                st.rerun()
    
    # 메인 채팅 영역
    if st.session_state.discussion_started:
        # 자동 토론 업데이트 처리
        handle_auto_discussion_update()
        
        # 채팅 메시지 표시
        st.subheader("💬 실시간 채팅")
        
        # 스크롤 가능한 채팅 컨테이너 (Streamlit container 사용)
        chat_container = st.container()
        chat_container.markdown("""
        <style>
        .main .block-container {
            max-height: 500px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with chat_container:
            # 채팅 메시지들을 스크롤 가능한 영역에 표시
            st.markdown('<div style="max-height: 500px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 10px; padding: 1rem; background: #fafafa; margin-bottom: 1rem;">', unsafe_allow_html=True)
            
            for msg in st.session_state.chat_messages:
                display_chat_message(msg, in_container=True)
            
            # 자동 토론 상태 표시 (채팅창 하단)
            display_auto_discussion_status()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 자동 스크롤을 위한 JavaScript
            st.markdown("""
            <script>
            setTimeout(function() {
                var chatDivs = document.querySelectorAll('div[style*="max-height: 500px"]');
                if (chatDivs.length > 0) {
                    var chatDiv = chatDivs[chatDivs.length - 1];
                    chatDiv.scrollTop = chatDiv.scrollHeight;
                }
            }, 100);
            </script>
            """, unsafe_allow_html=True)
        
        # 고급 기능 모달들
        if getattr(st.session_state, 'show_deep_dive', False):
            with st.expander("🔍 심화 질문", expanded=True):
                deep_question = st.text_area(
                    "구체적인 질문을 입력하세요",
                    placeholder="예: 이 전략의 성공률은? 리스크는? 비용은?",
                    key="deep_question_input"
                )
                
                focus_area = st.selectbox(
                    "답변받을 전문가",
                    ["전체", "디자인팀", "영업팀", "생산팀", "마케팅팀", "IT팀"]
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("질문하기", key="send_deep"):
                        if deep_question.strip():
                            with st.spinner(f"{focus_area} 전문가 답변 준비 중..."):
                                response = st.session_state.chat_system.deep_dive_question(
                                    deep_question, focus_area
                                )
                                st.session_state.chat_messages.append(response)
                            st.session_state.show_deep_dive = False
                            st.rerun()
                
                with col2:
                    if st.button("취소", key="cancel_deep"):
                        st.session_state.show_deep_dive = False
                        st.rerun()
        
        if getattr(st.session_state, 'show_brainstorm', False):
            with st.expander("💡 브레인스토밍", expanded=True):
                brainstorm_problem = st.text_area(
                    "브레인스토밍할 문제",
                    placeholder="예: 고객 만족도 향상 방법",
                    key="brainstorm_input"
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("시작하기", key="start_brainstorm"):
                        if brainstorm_problem.strip():
                            with st.spinner("전문가들이 아이디어를 생각하는 중..."):
                                responses = st.session_state.chat_system.brainstorm_solutions(
                                    brainstorm_problem
                                )
                                st.session_state.chat_messages.extend(responses)
                            st.session_state.show_brainstorm = False
                            st.rerun()
                
                with col2:
                    if st.button("취소", key="cancel_brainstorm"):
                        st.session_state.show_brainstorm = False
                        st.rerun()
        
        if getattr(st.session_state, 'show_implementation', False):
            with st.expander("📋 실행 계획", expanded=True):
                solution_text = st.text_area(
                    "계획을 세울 솔루션",
                    placeholder="예: 프리미엄 제품 출시",
                    key="implementation_input"
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("계획 수립", key="create_plan"):
                        if solution_text.strip():
                            with st.spinner("실행 계획 수립 중..."):
                                plan = st.session_state.chat_system.get_implementation_plan(
                                    solution_text
                                )
                                st.session_state.chat_messages.append(plan)
                            st.session_state.show_implementation = False
                            st.rerun()
                
                with col2:
                    if st.button("취소", key="cancel_plan"):
                        st.session_state.show_implementation = False
                        st.rerun()
        
        # 채팅 입력 - 화면 하단 고정
        st.markdown("---")
        
        # 입력 방식 탭
        input_tab1, input_tab2 = st.tabs(["💬 일반 대화", "🎯 전문가 질문"])
        
        with input_tab1:
            # 일반 채팅 입력
            if prompt := st.chat_input("메시지를 입력하세요..."):
                # 사용자 메시지 표시
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)
                
                # 시스템에 메시지 추가
                user_msg = ChatMessage("사용자", prompt)
                st.session_state.chat_messages.append(user_msg)
                
                # 사용자 개입 후 토론 재개 처리
                if st.session_state.chat_system.user_intervention_pending:
                    continue_msg = st.session_state.chat_system.continue_after_user_intervention()
                    st.session_state.chat_messages.append(continue_msg)
                    st.session_state.auto_discussion_enabled = True
                else:
                    # AI 응답 생성
                    with st.chat_message("assistant", avatar="🎭"):
                        with st.spinner("응답 생성 중..."):
                            response = st.session_state.chat_system.continue_discussion(prompt)
                            st.session_state.chat_messages.append(response)
                            st.markdown(response.content)
                
                st.rerun()
        
        with input_tab2:
            # 전문가별 질문
            col1, col2 = st.columns([2, 3])
            
            with col1:
                expert_options = {
                    "🎨 김창의 (디자인)": "김창의",
                    "💼 박매출 (영업)": "박매출", 
                    "⚙️ 이현실 (생산)": "이현실",
                    "📢 최홍보 (마케팅)": "최홍보",
                    "💻 박테크 (IT)": "박테크"
                }
                selected_expert_display = st.selectbox("질문할 전문가", list(expert_options.keys()))
                selected_expert = expert_options[selected_expert_display]
            
            with col2:
                expert_question = st.text_input(
                    f"{selected_expert_display}에게 질문",
                    placeholder="전문적인 질문을 입력하세요...",
                    key="expert_question"
                )
            
            if st.button("🎯 전문가에게 질문하기", use_container_width=True):
                if expert_question.strip():
                    # 사용자 질문 표시
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(f"@{selected_expert}: {expert_question}")
                    
                    # 시스템에 메시지 추가
                    user_msg = ChatMessage("사용자", f"@{selected_expert}: {expert_question}")
                    st.session_state.chat_messages.append(user_msg)
                    
                    # 전문가 응답
                    avatar = get_avatar(f"{selected_expert}")
                    with st.chat_message("assistant", avatar=avatar):
                        with st.spinner(f"{selected_expert} 전문가가 답변 중..."):
                            response = st.session_state.chat_system.ask_specific_person(
                                selected_expert, expert_question
                            )
                            st.session_state.chat_messages.append(response)
                            st.markdown(response.content)
                    
                    st.rerun()
    
    else:
        # 토론 시작 전 안내
        st.info("👈 사이드바에서 토론 설정을 완료하고 시작 버튼을 클릭하세요.")
        
        # 기능 소개 카드
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 💬 실시간 채팅
            - 자연스러운 대화 흐름
            - 즉시 질문과 응답
            - 현대적인 채팅 UI
            """)
        
        with col2:
            st.markdown("""
            ### 🎯 전문가 상담
            - 5개 분야 전문가
            - 개별 상담 가능
            - 전문성 기반 조언
            """)
        
        with col3:
            st.markdown("""
            ### 🧠 고급 기능
            - 심화 질문 & 분석
            - 브레인스토밍
            - 실행 계획 수립
            """)
    
    # 자동 새로고침 설정
    setup_auto_refresh()

if __name__ == "__main__":
    main()