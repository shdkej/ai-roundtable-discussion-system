import os
import datetime
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 기본 페르소나 정의 함수
def get_default_personas():
    """기본 페르소나 정의 반환"""
    return {
        "진행자": {
            "role": "토론 진행자",
            "goal": "토론을 원활하게 진행하고 각 팀의 의견을 조율하여 결론을 도출합니다.",
            "backstory": """
            당신은 KS의 토론 진행자로서 각 팀의 전문적 의견을 종합하여 실행 가능한 결론을 도출하는 전문가입니다.
            채팅 형식으로 실시간 소통이 가능하며, 사용자의 질문이나 의견에 즉시 응답할 수 있습니다.
            
            **응답 원칙:**
            - 모든 응답은 한국어로 작성
            - 간결하고 명확한 답변
            - 필요시 추가 설명 요청 가능
            - 실시간 대화 가능
            
            **도구 활용:**
            - 토론 주제와 관련된 최신 정보가 필요할 때 WebSearchTool을 활용하여 웹 검색을 수행하세요
            - 검색 결과를 바탕으로 더욱 정확하고 최신의 정보를 제공하세요
            """
        },
        "디자인팀": {
            "role": "디자인팀 팀장 김창의",
            "goal": "UI/UX 관점에서 사용자 중심의 혁신적인 디자인 솔루션을 제시합니다.",
            "backstory": """
            당신은 KS의 디자인팀을 이끄는 팀장 김창의입니다. 
            채팅 형식으로 실시간 소통이 가능하며, 디자인 관련 질문에 즉시 답변할 수 있습니다.
            
            **응답 형식**: "디자인팀 김창의: [내용]" 형태로 한국어로 작성
            **전문 분야**: UI/UX, 사용자 경험, 디자인 트렌드, 브랜딩
            
            **도구 활용:**
            - 최신 디자인 트렌드나 UI/UX 동향이 필요할 때 WebSearchTool을 활용하여 웹 검색을 수행하세요
            - 경쟁사 사례나 업계 동향을 파악해야 할 때 웹 검색을 통해 최신 정보를 수집하세요
            """
        },
        "영업팀": {
            "role": "영업팀 팀장 박매출",
            "goal": "시장 분석과 고객 니즈를 바탕으로 실질적인 매출 전략을 제시합니다.",
            "backstory": """
            당신은 KS의 영업팀을 이끄는 팀장 박매출입니다.
            채팅 형식으로 실시간 소통이 가능하며, 영업/마케팅 관련 질문에 즉시 답변할 수 있습니다.
            
            **응답 형식**: "영업팀 박매출: [내용]" 형태로 한국어로 작성
            **전문 분야**: 시장 분석, 고객 관리, 매출 전략, 경쟁사 분석
            """
        },
        "생산팀": {
            "role": "생산팀 팀장 이현실",
            "goal": "생산 효율성과 품질 관리 관점에서 실현 가능한 솔루션을 제시합니다.",
            "backstory": """
            당신은 KS의 생산팀을 이끄는 팀장 이현실입니다.
            채팅 형식으로 실시간 소통이 가능하며, 생산/제조 관련 질문에 즉시 답변할 수 있습니다.
            
            **응답 형식**: "생산팀 이현실: [내용]" 형태로 한국어로 작성
            **전문 분야**: 생산 계획, 품질 관리, 원가 분석, 공정 개선
            """
        },
        "마케팅팀": {
            "role": "마케팅팀 팀장 최홍보",
            "goal": "브랜드 전략과 고객 경험 관점에서 마케팅 솔루션을 제시합니다.",
            "backstory": """
            당신은 KS의 마케팅팀을 이끄는 팀장 최홍보입니다.
            채팅 형식으로 실시간 소통이 가능하며, 마케팅/브랜딩 관련 질문에 즉시 답변할 수 있습니다.
            
            **응답 형식**: "마케팅팀 최홍보: [내용]" 형태로 한국어로 작성
            **전문 분야**: 브랜드 전략, 디지털 마케팅, 고객 경험, 캠페인 기획
            """
        },
        "IT팀": {
            "role": "IT팀 팀장 박테크",
            "goal": "기술적 실현 가능성과 시스템 관점에서 IT 솔루션을 제시합니다.",
            "backstory": """
            당신은 KS의 IT팀을 이끄는 팀장 박테크입니다.
            채팅 형식으로 실시간 소통이 가능하며, IT/기술 관련 질문에 즉시 답변할 수 있습니다.
            
            **응답 형식**: "IT팀 박테크: [내용]" 형태로 한국어로 작성
            **전문 분야**: 시스템 아키텍처, 디지털 전환, 데이터 분석, 기술 트렌드
            """
        }
    }

# 커스텀 웹 검색 도구 구현
from crewai.tools import tool

def openai_research_tool(query: str) -> str:
    """OpenAI GPT를 사용한 상세한 정보 조사 (OPENAI_API_KEY 필요)"""
    try:
        import openai
        import os
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY를 설정해주세요."
        
        client = openai.OpenAI(api_key=api_key)
        
        # GPT-4를 사용하여 상세한 정보 조사
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 비용 효율적인 모델 사용
            messages=[
                {
                    "role": "system", 
                    "content": """당신은 전문적인 정보 조사 전문가입니다. 
                    
주어진 질문에 대해 다음과 같이 답변해주세요:
1. 핵심 내용을 정확하고 상세하게 설명
2. 최신 동향이나 트렌드가 있다면 포함
3. 실용적인 예시나 사례 제공
4. 비즈니스나 실무에 미치는 영향 분석
5. 관련 키워드나 용어 설명

답변은 한국어로 작성하고, 구체적이고 실용적인 정보를 제공해주세요.
답변 길이는 200-400자 정도로 적당히 상세하게 작성해주세요."""
                },
                {
                    "role": "user", 
                    "content": f"다음 주제에 대해 상세히 조사해주세요: {query}"
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        return f"🔍 조사 주제: {query}\n\n📊 상세 정보:\n{result}"
        
    except Exception as e:
        return f"OpenAI 조사 도구 오류: {str(e)}\n\n기본 지식을 바탕으로 답변을 제공하겠습니다."

def duckduckgo_search(query: str) -> str:
    """DuckDuckGo를 통한 기본적인 검색 결과 제공 (API 키 불필요)"""
    try:
        import urllib.parse
        
        # DuckDuckGo Instant Answer API 시도
        encoded_query = urllib.parse.quote(query)
        instant_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(instant_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Abstract (요약 정보)
        if data.get("Abstract") and len(data["Abstract"]) > 10:
            results.append(f"📋 요약: {data['Abstract']}")
            if data.get("AbstractURL"):
                results.append(f"🔗 출처: {data['AbstractURL']}")
        
        # Answer (직접 답변)  
        if data.get("Answer") and len(data["Answer"]) > 3:
            results.append(f"💡 답변: {data['Answer']}")
        
        # Definition (정의)
        if data.get("Definition") and len(data["Definition"]) > 10:
            results.append(f"📚 정의: {data['Definition']}")
            if data.get("DefinitionURL"):
                results.append(f"🔗 출처: {data['DefinitionURL']}")
        
        # Related Topics (관련 주제)
        if data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:
            results.append("\\n🔍 관련 정보:")
            count = 0
            for topic in data["RelatedTopics"][:5]:
                if isinstance(topic, dict) and topic.get("Text") and len(topic["Text"]) > 20:
                    text = topic["Text"]
                    if len(text) > 150:
                        text = text[:150] + "..."
                    results.append(f"  • {text}")
                    count += 1
                    if count >= 3:  # 최대 3개만 표시
                        break
        
        # Infobox 정보
        if data.get("Infobox") and data["Infobox"].get("content"):
            results.append("\\n📊 추가 정보:")
            for item in data["Infobox"]["content"][:3]:
                if item.get("label") and item.get("value"):
                    results.append(f"  • {item['label']}: {item['value']}")
        
        if results:
            return f"검색어: {query}\\n\\n" + "\\n".join(results)
        else:
            # 검색 결과가 없을 때 대안 제안
            return f"검색어 '{query}'에 대한 즉시 답변을 찾을 수 없습니다.\\n\\n💡 제안:\\n• 더 구체적인 키워드 사용\\n• 영어로 검색 시도\\n• 일반적인 용어 사용\\n\\n참고: 웹 검색 기능이 제한되어 있어 최신 정보나 세부 사항은 제공되지 않을 수 있습니다."
            
    except Exception as e:
        return f"웹 검색 중 오류가 발생했습니다: {str(e)}\\n\\n기본 지식을 바탕으로 답변을 제공하겠습니다."


def serper_search(query: str, api_key: str) -> str:
    """SERPER API를 사용한 웹 검색"""
    try:
        # SerpAPI를 사용한 웹 검색 (GET 방식)
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # SerpAPI 응답 형식에 맞게 수정
        if "organic_results" in data and data["organic_results"]:
            results = []
            for result in data["organic_results"][:5]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                results.append(f"제목: {title}\n내용: {snippet}\n링크: {link}\n")
            
            return f"검색어: {query}\n\n검색 결과:\n" + "\n".join(results)
        elif "answer_box" in data:
            answer_box = data["answer_box"]
            answer = answer_box.get("answer", answer_box.get("snippet", ""))
            return f"검색어: {query}\n\n답변: {answer}"
        elif "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            title = kg.get("title", "")
            description = kg.get("description", "")
            return f"검색어: {query}\n\n{title}: {description}"
        else:
            return f"검색어 '{query}'에 대한 결과를 찾을 수 없습니다."
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return f"SerpAPI 접근이 거부되었습니다. API 키를 확인하거나 플랜을 점검해주세요. (오류: {str(e)})"
        elif e.response.status_code == 401:
            return f"SerpAPI 인증에 실패했습니다. API 키가 올바른지 확인해주세요. (오류: {str(e)})"
        elif e.response.status_code == 429:
            return f"SerpAPI 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요. (오류: {str(e)})"
        else:
            return f"웹 검색 HTTP 오류가 발생했습니다: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"웹 검색 중 네트워크 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"SERPER API 검색 중 예상치 못한 오류가 발생했습니다: {str(e)}"

@tool("OpenAIResearchTool")
def openai_research_crewai_tool(query: str) -> str:
    """OpenAI GPT-4를 사용하여 상세하고 정확한 정보를 조사하는 도구입니다.
    
    사용 시기:
    - 복잡한 주제에 대한 상세한 분석이 필요할 때
    - 최신 트렌드나 기술 동향을 파악해야 할 때  
    - 비즈니스 전략이나 시장 분석이 필요할 때
    - 전문적인 지식이나 개념 설명이 필요할 때
    
    입력: 조사하고 싶은 주제나 질문 (문자열)
    출력: GPT-4가 제공하는 상세하고 전문적인 분석 결과
    
    예시: "2024년 AI 시장 동향", "디지털 마케팅 전략", "클라우드 컴퓨팅 보안", "UX 디자인 원칙"
    
    장점: 웹 검색보다 더 정확하고 체계적인 정보 제공
    """
    return openai_research_tool(query)

@tool("WebSearchTool")
def web_search_tool(query: str) -> str:
    """
    웹 검색을 통해 최신 정보를 수집하는 도구입니다.
    
    사용 시기:
    - 최신 정보나 최근 데이터가 필요할 때
    - 시장 동향이나 트렌드를 파악해야 할 때
    - 구체적인 사례나 통계가 필요할 때
    - 경쟁사 정보나 업계 동향을 파악해야 할 때
    
    입력: 검색하고 싶은 키워드나 질문
    출력: 검색 결과 요약 (제목, 내용, 링크 포함)
    
    예시: "2024년 AI 기술 동향", "ChatGPT 최신 업데이트", "머신러닝 시장 규모", "UI/UX 디자인 트렌드"
    
    중요: 질문에 답하기 전에 최신 정보가 필요하다면 반드시 이 도구를 먼저 사용하세요.
    """
    # 1. OpenAI 조사 도구를 먼저 시도 (가장 정확하고 상세한 정보)
    print(f"🤖 OpenAI로 정보 조사 시도: {query}")
    openai_result = openai_research_tool(query)
    
    # OpenAI에서 유효한 결과를 얻었으면 반환
    if openai_result and not ("API 키가 설정되지 않았습니다" in openai_result or "오류:" in openai_result):
        print(f"✅ OpenAI 조사 성공")
        return openai_result
    
    # 2. SERPER API 시도 (실제 웹 검색 결과)
    serper_api_key = os.getenv("SERPER_API_KEY")
    if serper_api_key:
        print(f"🔍 SERPER API로 검색 시도: {query}")
        serper_result = serper_search(query, serper_api_key)
        if serper_result and not ("오류가 발생했습니다" in serper_result):
            print(f"✅ SERPER API 검색 성공") 
            return serper_result
    
    # 3. DuckDuckGo 백업 시도
    print(f"🦆 DuckDuckGo로 검색 시도: {query}")
    ddg_result = duckduckgo_search(query)
    if ddg_result and not ("즉시 답변을 찾을 수 없습니다" in ddg_result or "오류가 발생했습니다" in ddg_result):
        print(f"✅ DuckDuckGo 검색 성공")
        return ddg_result
    
    # 4. 모든 방법 실패시 안내 메시지
    print(f"⚠️ 모든 검색 방법 실패")
    return f"검색어 '{query}'에 대한 상세한 정보를 찾기 어렵습니다.\\n\\n💡 더 나은 검색을 위해:\\n• OPENAI_API_KEY 설정 (가장 정확한 정보)\\n• SERPER_API_KEY 설정 (실시간 웹 검색)\\n\\n기본 지식을 바탕으로 답변을 제공하겠습니다."

class ChatMessage:
    def __init__(self, sender: str, content: str, timestamp: datetime.datetime = None, message_type: str = "message"):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now()
        self.message_type = message_type  # "message", "system", "question", "response"

class ChatRoundtable:
    def __init__(self):
        self.chat_history: List[ChatMessage] = []
        self.current_topic = ""
        self.context = {}
        self.active_agents = []
        self.discussion_state = "ready"  # ready, discussing, paused, ended
        self.current_speaker = None  # 현재 발언자
        self.auto_discussion_enabled = False  # 자동 토론 진행 여부
        self.next_speaker_queue = []  # 다음 발언자 대기열
        self.user_intervention_pending = False  # 사용자 개입 대기 상태
        self.discussion_rounds = 0  # 토론 라운드 수
        self.used_responses = {}  # 각 에이전트가 이미 사용한 응답 추적
        self.setup_agents()
    
    def setup_agents(self, custom_personas=None):
        """에이전트 설정"""
        # 기본 페르소나 정의 (저장된 커스텀 페르소나가 있으면 로드)
        try:
            from personas_storage import persona_storage
            default_personas = persona_storage.load_personas()
        except ImportError:
            # personas_storage를 import할 수 없는 경우 기본 페르소나 사용
            default_personas = get_default_personas()
        
        # 커스텀 페르소나가 제공된 경우 기본값과 병합
        if custom_personas:
            for agent_name, persona in custom_personas.items():
                if agent_name in default_personas:
                    default_personas[agent_name].update(persona)
        
        # LLM 설정
        llm = LLM(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY
        )
        
        # 토론 진행자
        moderator_persona = default_personas["진행자"]
        self.moderator = Agent(
            role=moderator_persona["role"],
            goal=moderator_persona["goal"],
            backstory=moderator_persona["backstory"],
            verbose=True,
            tools=[openai_research_crewai_tool, web_search_tool],
            llm=llm
        )
        
        # 디자인팀 에이전트
        design_persona = default_personas["디자인팀"]
        self.design_agent = Agent(
            role=design_persona["role"],
            goal=design_persona["goal"],
            backstory=design_persona["backstory"],
            verbose=True,
            tools=[openai_research_crewai_tool, web_search_tool],
            llm=llm
        )

        # 영업팀 에이전트  
        sales_persona = default_personas["영업팀"]
        self.sales_agent = Agent(
            role=sales_persona["role"],
            goal=sales_persona["goal"],
            backstory=sales_persona["backstory"],
            verbose=True,
            tools=[openai_research_crewai_tool, web_search_tool],
            llm=llm
        )

        # 생산팀 에이전트
        production_persona = default_personas["생산팀"]
        self.production_agent = Agent(
            role=production_persona["role"],
            goal=production_persona["goal"],
            backstory=production_persona["backstory"],
            verbose=True,
            tools=[openai_research_crewai_tool, web_search_tool],
            llm=llm
        )

        # 마케팅팀 에이전트
        marketing_persona = default_personas["마케팅팀"]
        self.marketing_agent = Agent(
            role=marketing_persona["role"],
            goal=marketing_persona["goal"],
            backstory=marketing_persona["backstory"],
            verbose=True,
            tools=[openai_research_crewai_tool, web_search_tool],
            llm=llm
        )

        # IT팀 에이전트
        it_persona = default_personas["IT팀"]
        self.it_agent = Agent(
            role=it_persona["role"],
            goal=it_persona["goal"],
            backstory=it_persona["backstory"],
            verbose=True,
            tools=[openai_research_crewai_tool, web_search_tool],
            llm=llm
        )

    def get_agent_by_name(self, name: str):
        """이름으로 에이전트 찾기"""
        agent_map = {
            "진행자": self.moderator,
            "토론진행자": self.moderator,
            "김창의": self.design_agent,
            "디자인팀": self.design_agent,
            "박매출": self.sales_agent,
            "영업팀": self.sales_agent,
            "이현실": self.production_agent,
            "생산팀": self.production_agent,
            "최홍보": self.marketing_agent,
            "마케팅팀": self.marketing_agent,
            "박테크": self.it_agent,
            "IT팀": self.it_agent
        }
        return agent_map.get(name.replace(" ", ""))

    def start_discussion(self, topic: str, context: Dict, participants: List[str] = None):
        """토론 시작"""
        try:
            print(f"start_discussion 호출됨: topic={topic}, participants={participants}")
            print(f"context 타입: {type(context)}, 내용: {context}")
            
            self.current_topic = topic
            
            # context가 dict가 아닌 경우 처리
            if not isinstance(context, dict):
                print(f"경고: context가 dict가 아닙니다. 타입: {type(context)}")
                self.context = {}
            else:
                self.context = context
            
            self.discussion_state = "discussing"
            
            # 새 토론 시작시 사용된 응답 초기화
            self.used_responses = {}
            
            # 참여 에이전트 설정
            if participants:
                print(f"참가자 목록: {participants}")
                self.active_agents = []
                for participant in participants:
                    print(f"참가자 매칭 시도: '{participant}'")
                    # 이름 기반 매칭
                    if participant == "김창의" or "창의" in participant or "디자인" in participant or "Design" in participant:
                        self.active_agents.append(self.design_agent)
                        print(f"디자인 에이전트 추가: {self.design_agent.role}")
                    elif participant == "박매출" or "매출" in participant or "영업" in participant or "Sales" in participant:
                        self.active_agents.append(self.sales_agent)
                        print(f"영업 에이전트 추가: {self.sales_agent.role}")
                    elif participant == "이현실" or "현실" in participant or "생산" in participant or "Production" in participant:
                        self.active_agents.append(self.production_agent)
                        print(f"생산 에이전트 추가: {self.production_agent.role}")
                    elif participant == "최홍보" or "홍보" in participant or "마케팅" in participant or "Marketing" in participant:
                        self.active_agents.append(self.marketing_agent)
                        print(f"마케팅 에이전트 추가: {self.marketing_agent.role}")
                    elif participant == "정기술" or "기술" in participant or "IT" in participant:
                        self.active_agents.append(self.it_agent)
                        print(f"IT 에이전트 추가: {self.it_agent.role}")
                    else:
                        print(f"⚠️ 매칭되지 않은 참가자: '{participant}'")
            else:
                print("기본 에이전트 사용")
                self.active_agents = [self.design_agent, self.sales_agent, self.production_agent, self.marketing_agent, self.it_agent]
            
            print(f"최종 활성 에이전트 수: {len(self.active_agents)}")
            print("최종 활성 에이전트 목록:")
            for i, agent in enumerate(self.active_agents):
                print(f"  [{i}]: {agent.role}")
            
            # 시작 메시지
            start_msg = ChatMessage(
                sender="시스템",
                content=f"🚀 토론이 시작되었습니다!\n주제: {topic}\n참석자: {len(self.active_agents)}명",
                message_type="system"
            )
            self.chat_history.append(start_msg)
            
            return start_msg
            
        except Exception as e:
            print(f"start_discussion 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e

    def get_initial_opinions(self):
        """각 팀의 초기 입장 수집"""
        try:
            # context가 제대로 설정되었는지 확인
            if not hasattr(self, 'context') or not self.context:
                print("경고: context가 설정되지 않았습니다. 기본값을 사용합니다.")
                self.context = {}
            
            # context가 dict가 아닌 경우 처리
            if not isinstance(self.context, dict):
                print(f"경고: context가 dict가 아닙니다. 타입: {type(self.context)}")
                self.context = {}
            
            context_info = f"""
            **회사 상황:**
            - 회사 규모: {self.context.get('company_size', '정보 없음')}
            - 사업 분야: {self.context.get('industry', '정보 없음')}
            - 연 매출: {self.context.get('revenue', '정보 없음')}
            - 해결 과제: {self.context.get('current_challenge', '정보 없음')}
            """
            
            print(f"컨텍스트 정보: {context_info}")
            print(f"활성 에이전트 수: {len(self.active_agents)}")
            
            initial_opinions = []
            
            for i, agent in enumerate(self.active_agents):
                try:
                    print(f"에이전트 {i+1} 초기 의견 생성 중: {agent.role}")
                    
                    task = Task(
                        description=f"""
                        토론 주제: {self.current_topic}
                        
                        {context_info}
                        
                        귀하의 전문 분야 관점에서 이 주제에 대한 초기 입장을 간결하게 제시해주세요.
                        채팅 형식으로 2-3문장 정도의 핵심 의견만 말씀해주세요.
                        """,
                        expected_output="전문가 관점의 간결한 초기 입장 (한국어)",
                        agent=agent
                    )
                    
                    crew = Crew(
                        agents=[agent],
                        tasks=[task],
                        process=Process.sequential,
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    
                    msg = ChatMessage(
                        sender=agent.role,
                        content=str(result)
                    )
                    self.chat_history.append(msg)
                    initial_opinions.append(msg)
                    
                    print(f"에이전트 {i+1} 초기 의견 생성 완료: {agent.role}")
                    
                except Exception as e:
                    print(f"에이전트 {i+1} 초기 의견 생성 실패: {agent.role} - {str(e)}")
                    # 기본 메시지 생성
                    default_msg = ChatMessage(
                        sender=agent.role,
                        content=f"{agent.role}의 초기 의견을 생성하는 중 오류가 발생했습니다."
                    )
                    self.chat_history.append(default_msg)
                    initial_opinions.append(default_msg)
            
            return initial_opinions
            
        except Exception as e:
            print(f"get_initial_opinions 전체 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            # 빈 리스트 반환
            return []

    def ask_specific_person(self, person: str, question: str, context: str = ""):
        """특정 전문가에게 질문"""
        agent = self.get_agent_by_name(person)
        if not agent:
            return ChatMessage(
                sender="시스템",
                content=f"❌ '{person}'을(를) 찾을 수 없습니다. 사용 가능한 전문가: 김창의(디자인), 박매출(영업), 이현실(생산), 최홍보(마케팅), 박테크(IT)",
                message_type="system"
            )
        
        # 최근 대화 컨텍스트 포함
        recent_context = ""
        if len(self.chat_history) > 0:
            recent_messages = self.chat_history[-5:]  # 최근 5개 메시지
            recent_context = "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_messages])
        
        task = Task(
            description=f"""
            토론 주제: {self.current_topic}
            
            최근 대화 내용:
            {recent_context}
            
            추가 컨텍스트:
            {context}
            
            질문: {question}
            
            위 질문에 대해 귀하의 전문 분야 관점에서 답변해주세요.
            채팅 형식으로 자연스럽게 답변해주세요.
            """,
            expected_output="전문가 관점의 구체적 답변 (한국어)",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        response_msg = ChatMessage(
            sender=agent.role,
            content=str(result)
        )
        self.chat_history.append(response_msg)
        
        return response_msg

    def continue_discussion(self, user_input: str):
        """토론 계속 진행"""
        # 사용자 메시지 추가
        user_msg = ChatMessage(
            sender="사용자",
            content=user_input
        )
        self.chat_history.append(user_msg)
        
        # 진행자가 응답
        recent_context = ""
        if len(self.chat_history) > 0:
            recent_messages = self.chat_history[-10:]  # 최근 10개 메시지
            recent_context = "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_messages])
        
        task = Task(
            description=f"""
            토론 주제: {self.current_topic}
            
            최근 대화 내용:
            {recent_context}
            
            사용자가 "{user_input}"라고 말했습니다.
            
            토론 진행자로서 이에 적절히 응답하고, 필요하다면 다른 전문가들의 추가 의견을 요청하거나
            토론을 더 발전시킬 수 있는 방향을 제시해주세요.
            """,
            expected_output="토론 진행자의 적절한 응답 (한국어)",
            agent=self.moderator
        )
        
        crew = Crew(
            agents=[self.moderator],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        moderator_msg = ChatMessage(
            sender="토론 진행자",
            content=str(result)
        )
        self.chat_history.append(moderator_msg)
        
        return moderator_msg

    def deep_dive_question(self, question: str, focus_area: str = "전체"):
        """결과에 대한 심화 질문 처리"""
        # 사용자 질문 추가
        user_msg = ChatMessage(
            sender="사용자",
            content=f"[심화질문-{focus_area}] {question}",
            message_type="question"
        )
        self.chat_history.append(user_msg)
        
        # 전체 토론 컨텍스트
        full_context = "\n".join([f"{msg.sender}: {msg.content}" for msg in self.chat_history])
        
        if focus_area == "전체" or focus_area == "종합":
            # 진행자가 종합적으로 답변
            task = Task(
                description=f"""
                토론 주제: {self.current_topic}
                
                전체 토론 내용:
                {full_context}
                
                사용자가 "{question}"에 대해 심화 질문을 했습니다.
                
                지금까지의 모든 토론 내용을 바탕으로 이 질문에 대해 종합적이고 구체적으로 답변해주세요.
                다음 사항을 포함해주세요:
                1. 질문에 대한 직접적 답변
                2. 관련 데이터나 근거
                3. 실행 방안
                4. 예상되는 결과
                5. 추가 고려사항
                """,
                expected_output="심화 질문에 대한 종합적 답변 (한국어)",
                agent=self.moderator
            )
            
            crew = Crew(
                agents=[self.moderator],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff()
            
            response_msg = ChatMessage(
                sender="토론 진행자",
                content=str(result),
                message_type="response"
            )
            
        else:
            # 특정 분야 전문가가 답변
            agent = self.get_agent_by_name(focus_area)
            if not agent:
                return ChatMessage(
                    sender="시스템",
                    content=f"❌ '{focus_area}' 전문가를 찾을 수 없습니다.",
                    message_type="system"
                )
            
            task = Task(
                description=f"""
                토론 주제: {self.current_topic}
                
                전체 토론 내용:
                {full_context}
                
                사용자가 "{question}"에 대해 귀하의 전문 분야와 관련된 심화 질문을 했습니다.
                
                귀하의 전문성을 바탕으로 이 질문에 대해 구체적이고 실용적으로 답변해주세요.
                다음 사항을 포함해주세요:
                1. 전문 분야 관점에서의 답변
                2. 구체적인 데이터나 사례
                3. 실행 시 고려사항
                4. 성공 요인과 리스크
                """,
                expected_output="전문가 관점의 심화 답변 (한국어)",
                agent=agent
            )
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff()
            
            response_msg = ChatMessage(
                sender=agent.role,
                content=str(result),
                message_type="response"
            )
        
        self.chat_history.append(response_msg)
        return response_msg

    def brainstorm_solutions(self, problem: str):
        """특정 문제에 대한 브레인스토밍"""
        user_msg = ChatMessage(
            sender="사용자",
            content=f"[브레인스토밍] {problem}",
            message_type="question"
        )
        self.chat_history.append(user_msg)
        
        # 모든 활성 에이전트가 아이디어 제시
        brainstorm_responses = []
        
        for agent in self.active_agents:
            task = Task(
                description=f"""
                토론 주제: {self.current_topic}
                브레인스토밍 문제: {problem}
                
                귀하의 전문 분야 관점에서 이 문제에 대한 창의적이고 실용적인 해결 아이디어를 제시해주세요.
                
                다음 형식으로 답변해주세요:
                1. 핵심 아이디어 (1줄 요약)
                2. 구체적 실행 방법
                3. 예상 효과
                4. 필요 자원
                
                짧고 명확하게 작성해주세요.
                """,
                expected_output="창의적 해결 아이디어 (한국어)",
                agent=agent
            )
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff()
            
            response_msg = ChatMessage(
                sender=agent.role,
                content=str(result)
            )
            brainstorm_responses.append(response_msg)
            self.chat_history.append(response_msg)
        
        # 진행자가 아이디어들을 종합
        all_ideas = "\n\n".join([f"{msg.sender}: {msg.content}" for msg in brainstorm_responses])
        
        synthesis_task = Task(
            description=f"""
            브레인스토밍 문제: {problem}
            
            각 전문가의 아이디어:
            {all_ideas}
            
            위의 모든 아이디어를 분석하고 다음을 제시해주세요:
            1. 가장 유망한 아이디어 TOP 3
            2. 아이디어들의 시너지 방안
            3. 통합 실행 계획
            4. 우선순위와 타임라인
            """,
            expected_output="브레인스토밍 종합 결과 (한국어)",
            agent=self.moderator
        )
        
        synthesis_crew = Crew(
            agents=[self.moderator],
            tasks=[synthesis_task],
            process=Process.sequential,
            verbose=False
        )
        
        synthesis_result = synthesis_crew.kickoff()
        
        synthesis_msg = ChatMessage(
            sender="토론 진행자",
            content=f"🧠 브레인스토밍 종합 결과:\n\n{synthesis_result}",
            message_type="conclusion"
        )
        self.chat_history.append(synthesis_msg)
        
        return brainstorm_responses + [synthesis_msg]

    def get_implementation_plan(self, solution: str):
        """특정 솔루션에 대한 구체적 실행 계획 요청"""
        user_msg = ChatMessage(
            sender="사용자",
            content=f"[실행계획] {solution}",
            message_type="question"
        )
        self.chat_history.append(user_msg)
        
        # 전체 컨텍스트 포함
        full_context = "\n".join([f"{msg.sender}: {msg.content}" for msg in self.chat_history[-20:]])
        
        task = Task(
            description=f"""
            토론 주제: {self.current_topic}
            요청된 솔루션: {solution}
            
            최근 토론 내용:
            {full_context}
            
            "{solution}"에 대한 구체적이고 실행 가능한 계획을 수립해주세요.
            
            다음 항목을 포함해주세요:
            1. 실행 단계별 세부 계획 (1단계, 2단계, 3단계...)
            2. 각 단계별 소요 기간
            3. 필요 자원 (인력, 예산, 기술 등)
            4. 담당 부서별 역할 분담
            5. 성과 측정 지표 (KPI)
            6. 리스크 요소와 대응책
            7. 마일스톤과 체크포인트
            """,
            expected_output="구체적 실행 계획 (한국어)",
            agent=self.moderator
        )
        
        crew = Crew(
            agents=[self.moderator],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        plan_msg = ChatMessage(
            sender="토론 진행자",
            content=f"📋 실행 계획:\n\n{result}",
            message_type="response"
        )
        self.chat_history.append(plan_msg)
        
        return plan_msg

    def get_conclusion(self):
        """현재까지의 토론 내용을 바탕으로 중간 결론 도출"""
        discussion_content = "\n".join([f"{msg.sender}: {msg.content}" for msg in self.chat_history])
        
        task = Task(
            description=f"""
            토론 주제: {self.current_topic}
            
            지금까지의 토론 내용:
            {discussion_content}
            
            현재까지의 토론 내용을 바탕으로 중간 결론을 정리해주세요:
            1. 주요 합의 사항
            2. 여전히 논의가 필요한 부분
            3. 현재까지 제시된 실행 방안
            4. 다음 논의 방향
            """,
            expected_output="체계적으로 정리된 중간 결론 (한국어)",
            agent=self.moderator
        )
        
        crew = Crew(
            agents=[self.moderator],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        conclusion_msg = ChatMessage(
            sender="토론 진행자",
            content=str(result),
            message_type="conclusion"
        )
        self.chat_history.append(conclusion_msg)
        
        return conclusion_msg

    def start_auto_discussion(self):
        """자동 토론 시작"""
        self.auto_discussion_enabled = True
        self.discussion_state = "auto_discussing"
        self._initialize_speaker_queue()
        
        return ChatMessage(
            sender="시스템",
            content="🚀 자동 토론이 시작되었습니다! 전문가들이 자유롭게 토론을 진행합니다.",
            message_type="system"
        )
    
    def pause_auto_discussion(self):
        """자동 토론 일시정지"""
        self.auto_discussion_enabled = False
        self.discussion_state = "paused"
        
        return ChatMessage(
            sender="시스템",
            content="⏸️ 자동 토론이 일시정지되었습니다.",
            message_type="system"
        )
    
    def resume_auto_discussion(self):
        """자동 토론 재개"""
        self.auto_discussion_enabled = True
        self.discussion_state = "auto_discussing"
        
        return ChatMessage(
            sender="시스템",
            content="▶️ 자동 토론이 재개되었습니다.",
            message_type="system"
        )
    
    def request_user_intervention(self):
        """사용자 개입 요청"""
        self.user_intervention_pending = True
        self.auto_discussion_enabled = False
        self.discussion_state = "user_intervention"
        
        return ChatMessage(
            sender="시스템",
            content="✋ 사용자 개입이 요청되었습니다. 발언해주세요!",
            message_type="system"
        )
    
    def continue_after_user_intervention(self):
        """사용자 개입 후 토론 재개"""
        self.user_intervention_pending = False
        self.auto_discussion_enabled = True
        self.discussion_state = "auto_discussing"
        
        return ChatMessage(
            sender="시스템",
            content="🔄 사용자 발언 후 토론을 재개합니다.",
            message_type="system"
        )
    
    def _initialize_speaker_queue(self):
        """발언자 대기열 초기화"""
        import random
        self.next_speaker_queue = self.active_agents.copy()
        random.shuffle(self.next_speaker_queue)
        self.current_speaker = None
    
    def get_next_speaker(self):
        """다음 발언자 선정"""
        if not self.next_speaker_queue:
            self._initialize_speaker_queue()
        
        # active_agents가 비어있는 경우 처리
        if not self.next_speaker_queue:
            print("경고: active_agents가 비어있습니다. 기본 에이전트를 설정합니다.")
            self.active_agents = [self.design_agent, self.sales_agent, self.production_agent]
            self._initialize_speaker_queue()
        
        # 여전히 비어있는 경우 오류 방지
        if not self.next_speaker_queue:
            print("오류: 발언자 대기열을 초기화할 수 없습니다.")
            return None
        
        self.current_speaker = self.next_speaker_queue.pop(0)
        return self.current_speaker
    
    def get_current_speaker_info(self):
        """현재 발언자 정보 반환"""
        if self.current_speaker:
            return {
                "name": self.current_speaker.role,
                "is_speaking": True,
                "status": "발언 중"
            }
        elif self.user_intervention_pending:
            return {
                "name": "사용자",
                "is_speaking": False,
                "status": "발언 대기"
            }
        else:
            return {
                "name": "준비 중",
                "is_speaking": False,
                "status": "대기"
            }
    
    async def generate_auto_response_async(self, callback=None):
        """비동기적으로 자동 응답 생성 - 실시간 스트리밍 지원"""
        if not self.auto_discussion_enabled:
            print("❌ 자동 토론이 비활성화됨")
            return None
        
        next_speaker = self.get_next_speaker()
        
        # next_speaker가 None인 경우 처리
        if not next_speaker:
            print("❌ 다음 발언자를 찾을 수 없습니다.")
            return None
        
        print(f"🎤 다음 발언자: {next_speaker.role}")
        
        # 즉시 타이핑 시작 알림
        if callback:
            await callback("typing_start", {"speaker": next_speaker.role})
        
        try:
            # CrewAI 에이전트를 사용한 실제 AI 응답 생성
            response_content = self._generate_crewai_response(next_speaker)
            
            response_msg = ChatMessage(
                sender=next_speaker.role,
                content=response_content
            )
            
            self.chat_history.append(response_msg)
            self.discussion_rounds += 1
            
            print(f"✅ 응답 생성 완료: {next_speaker.role}")
            
            if callback:
                await callback("typing_stop", {})
                await callback("message", response_msg)
            
            return response_msg
                
        except Exception as e:
            print(f"자동 응답 생성 오류: {e}")
            if callback:
                await callback("typing_stop", {})
            return None
    
    def _get_quick_responses(self, speaker):
        """발언자별 빠른 응답 템플릿"""
        responses = {
            "디자인팀 팀장 김창의": [
                "사용자 경험 관점에서 보면, 이 부분은 더 직관적으로 개선할 수 있을 것 같습니다.",
                "디자인적으로 접근하면 브랜드 정체성을 강화하는 방향으로 진행해보면 어떨까요?",
                "시각적 일관성을 위해 디자인 시스템을 먼저 정립하는 것이 중요해 보입니다."
            ],
            "영업팀 팀장 박매출": [
                "고객 피드백을 보면, 이런 방향으로 가는 것이 매출 증대에 도움이 될 것 같습니다.",
                "시장 반응을 고려할 때, 더 공격적인 마케팅 전략이 필요할 것 같아요.",
                "경쟁사 대비 우리의 강점을 어떻게 부각시킬지 고민해봐야겠습니다."
            ],
            "생산팀 팀장 이현실": [
                "현실적으로 생산 일정을 고려하면, 단계적 접근이 더 안전할 것 같습니다.",
                "품질 관리 측면에서 이 부분은 좀 더 신중하게 검토해야 할 것 같아요.",
                "리소스 배분을 효율적으로 하려면 우선순위를 명확히 해야겠습니다."
            ],
            "마케팅팀 팀장 최홍보": [
                "타겟 고객층을 고려할 때, 이런 메시지로 어필하면 좋을 것 같습니다.",
                "브랜딩 관점에서 일관된 스토리텔링이 중요할 것 같아요.",
                "소셜미디어 반응을 보면, 이런 콘텐츠가 더 효과적일 것 같습니다."
            ],
            "IT팀 팀장 박테크": [
                "기술적 구현 가능성을 검토해보면, 이 방향이 더 현실적일 것 같습니다.",
                "시스템 안정성을 고려할 때, 보안 측면도 함께 검토해야겠습니다.",
                "개발 리소스를 고려하면 MVP부터 시작하는 것이 좋을 것 같아요."
            ]
        }
        return responses.get(speaker.role, [
            "흥미로운 관점이네요. 제 분야에서 보면 다른 접근도 가능할 것 같습니다.",
            "좋은 의견입니다. 추가로 고려해볼 점이 있다면...",
            "그 부분에 대해서는 좀 더 자세히 논의해봐야 할 것 같습니다."
        ])

    def save_chat_log(self):
        """채팅 로그를 마크다운 파일로 저장"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"채팅토론결과_{timestamp}.md"
        
        markdown_content = f"""# 🏢 채팅형 원탁토론 결과

## 📋 토론 정보
- **주제**: {self.current_topic}
- **일시**: {datetime.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")}
- **참석자**: {len(self.active_agents)}명
- **총 메시지**: {len(self.chat_history)}개
- **토론 라운드**: {self.discussion_rounds}라운드

---

## 💬 채팅 로그

"""
        
        for msg in self.chat_history:
            time_str = msg.timestamp.strftime("%H:%M:%S")
            if msg.message_type == "system":
                markdown_content += f"**[{time_str}] 📢 {msg.sender}**: {msg.content}\n\n"
            elif msg.message_type == "conclusion":
                markdown_content += f"**[{time_str}] 🎯 {msg.sender}**: {msg.content}\n\n"
            else:
                markdown_content += f"**[{time_str}] {msg.sender}**: {msg.content}\n\n"
        
        markdown_content += f"""
---

*이 문서는 채팅형 원탁토론 시스템에 의해 자동 생성되었습니다.*  
*생성 시간: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filename
    
    def _generate_role_specific_response(self, agent):
        """에이전트 역할에 맞는 특화된 응답 생성 (중복 방지)"""
        import random
        
        # 현재 토론 주제와 컨텍스트 정보 활용
        topic = getattr(self, 'current_topic', '새로운 프로젝트')
        round_num = self.discussion_rounds
        
        # 에이전트별 사용된 응답 추적 초기화
        if agent.role not in self.used_responses:
            self.used_responses[agent.role] = set()
        
        # 에이전트별 특화된 응답 템플릿
        responses = {
            "디자인 전문가": [
                f"디자인 관점에서 보면, {topic}의 사용자 인터페이스는 직관적이고 접근성이 좋아야 합니다. 특히 시각적 일관성과 브랜드 아이덴티티를 고려해야 해요.",
                f"UX/UI 설계 시 고려해야 할 점은 사용자 여정(User Journey)입니다. {topic}에서 사용자가 어떤 단계를 거쳐 목표를 달성하는지 분석이 필요합니다.",
                f"디자인 시스템 구축이 중요합니다. {topic}의 일관된 브랜드 경험을 위해 컬러, 타이포그래피, 컴포넌트 가이드라인을 정립해야 합니다.",
                f"사용자 중심 디자인(Human-Centered Design)이 핵심입니다. {topic} 사용자들의 니즈와 페인포인트를 정확히 파악한 후 솔루션을 제시해야 해요.",
            ],
            "영업 전문가": [
                f"시장에서 {topic}의 경쟁력을 확보하려면 차별화된 가치 제안이 필요합니다. 고객이 왜 우리 제품을 선택해야 하는지 명확한 메시지가 있어야 해요.",
                f"고객 세분화(Customer Segmentation) 전략이 중요합니다. {topic}의 타겟 고객층을 정확히 정의하고 각각에 맞는 영업 접근법을 준비해야 합니다.",
                f"매출 목표 달성을 위한 단계별 전략이 필요해요. {topic}의 시장 진입부터 확장까지, 각 단계별 KPI와 실행 계획을 세워야 합니다.",
                f"고객 관계 관리(CRM) 시스템을 통해 {topic} 잠재고객의 구매 여정을 체계적으로 관리해야 합니다. 리드 생성부터 계약 체결까지 전 과정을 추적해야 해요.",
            ],
            "생산 전문가": [
                f"생산 효율성 측면에서 {topic}의 제조 공정을 최적화해야 합니다. 품질 관리와 원가 절감의 균형을 찾는 것이 핵심이에요.",
                f"공급망 관리(SCM)가 중요합니다. {topic}에 필요한 원자재와 부품의 안정적 조달과 재고 최적화 방안을 구축해야 합니다.",
                f"품질 보증(QA) 시스템을 구축해야 해요. {topic}의 품질 기준을 설정하고, 생산 전 과정에서 품질 검증 체계를 운영해야 합니다.",
                f"생산 스케줄링과 용량 계획이 필요합니다. {topic}의 수요 예측을 바탕으로 효율적인 생산 계획을 수립해야 합니다.",
            ],
            "마케팅 전문가": [
                f"브랜드 포지셔닝 전략이 핵심입니다. {topic}이 시장에서 어떤 이미지와 가치로 인식되기를 원하는지 명확히 정의해야 해요.",
                f"통합 마케팅 커뮤니케이션(IMC) 접근이 필요합니다. {topic}의 메시지를 다양한 채널을 통해 일관되게 전달해야 합니다.",
                f"디지털 마케팅 전략을 강화해야 해요. {topic}의 온라인 가시성을 높이고, SEO, 소셜미디어, 콘텐츠 마케팅을 통합적으로 운영해야 합니다.",
                f"고객 데이터 분석을 통한 개인화 마케팅이 중요합니다. {topic} 사용자들의 행동 패턴을 분석하여 맞춤형 캠페인을 설계해야 해요.",
            ],
            "IT 전문가": [
                f"기술 아키텍처 설계가 중요합니다. {topic}의 확장성과 안정성을 고려한 시스템 구조를 설계해야 합니다.",
                f"보안 체계 구축이 필수입니다. {topic}의 데이터 보호와 사이버 보안 위협에 대응할 수 있는 다층 보안 시스템이 필요해요.",
                f"클라우드 인프라 전략을 수립해야 합니다. {topic}의 비용 효율성과 성능을 동시에 확보할 수 있는 클라우드 솔루션을 선택해야 해요.",
                f"데이터 관리 및 분석 시스템이 핵심입니다. {topic}에서 생성되는 데이터를 효과적으로 수집, 저장, 분석할 수 있는 인프라를 구축해야 합니다.",
            ]
        }
        
        # 해당 역할의 응답이 없으면 일반적인 응답 사용
        role_responses = responses.get(agent.role, [
            f"{agent.role} 관점에서 {topic}에 대해 전문적인 의견을 제시하겠습니다.",
            f"우리 분야의 경험을 바탕으로 {topic}의 실행 가능성을 검토해보겠습니다.",
            f"{topic}와 관련된 중요한 고려사항들을 말씀드리겠습니다.",
        ])
        
        # 아직 사용하지 않은 응답들만 필터링
        available_responses = [r for r in role_responses if r not in self.used_responses[agent.role]]
        
        # 모든 응답을 사용했다면 리셋 (새로운 라운드 시작)
        if not available_responses:
            self.used_responses[agent.role].clear()
            available_responses = role_responses
        
        # 응답 선택 (한 번만)
        selected_response = random.choice(available_responses)
        
        # 선택된 응답을 사용된 응답에 추가
        self.used_responses[agent.role].add(selected_response)
        
        # 토론 진행 단계에 따른 응답 스타일 조정 (선택적)
        if round_num <= 2:
            # 초기 단계: 그대로 사용
            base_response = selected_response
        elif round_num <= 5:
            # 중간 단계: 약간의 스타일 조정 (하지만 너무 획일적이지 않게)
            if "고려해야" in selected_response and round_num % 2 == 0:
                base_response = selected_response.replace("고려해야", "구체적으로 실행해야")
            else:
                base_response = selected_response
        else:
            # 후반 단계: 결론 지향적 스타일로 약간 조정
            if "필요합니다" in selected_response and round_num % 3 == 0:
                base_response = selected_response.replace("필요합니다", "핵심 포인트로 정리됩니다")
            else:
                base_response = selected_response
        
        
        return base_response
    
    def _generate_crewai_response(self, agent):
        """CrewAI 에이전트를 사용하여 실제 AI 응답 생성"""
        from crewai import Task, Crew
        
        # 현재 토론 상황 컨텍스트 구성
        topic = getattr(self, 'current_topic', '새로운 프로젝트')
        
        # 최근 대화 내용 가져오기 (마지막 3개 메시지)
        recent_messages = []
        if len(self.chat_history) > 0:
            recent_messages = self.chat_history[-3:]
            context_messages = "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_messages])
        else:
            context_messages = "토론이 시작되었습니다."
        
        # 회사 정보 컨텍스트
        company_context = ""
        if hasattr(self, 'context') and self.context:
            company_context = f"""
회사 정보:
- 규모: {self.context.get('company_size', '정보 없음')}
- 업종: {self.context.get('industry', '정보 없음')}  
- 매출: {self.context.get('revenue', '정보 없음')}
- 현재 과제: {self.context.get('current_challenge', '정보 없음')}
"""
        
        # 간단하고 명확한 프롬프트로 수정
        task_description = f"""
{agent.role}의 전문성을 바탕으로 다음 주제에 대한 의견을 2-3문장으로 간단히 제시하세요:

주제: {topic}
{company_context}

최근 논의: {context_messages}

{agent.role}의 관점에서 구체적이고 실무적인 의견을 제시해주세요.
"""

        try:
            # Task 생성
            task = Task(
                description=task_description,
                agent=agent,
                expected_output="전문가 관점의 간결한 의견 (2-3문장)"
            )
            
            # Crew를 통해 실행
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False
            )
            
            result = crew.kickoff()
            
            # 결과 처리
            if hasattr(result, 'raw'):
                response = result.raw
            elif isinstance(result, str):
                response = result
            else:
                response = str(result)
            
            # "Final Answer:" 부분 제거
            if "Final Answer:" in response:
                response = response.split("Final Answer:")[-1].strip()
            
            # 너무 긴 응답은 자르기
            if len(response) > 300:
                sentences = response.split('.')
                response = '. '.join(sentences[:3]) + '.'
            
            response = response.strip()
            if not response:
                raise ValueError("빈 응답")
                
            return response
                
        except Exception as e:
            print(f"⚠️ CrewAI 응답 생성 실패 ({agent.role}): {e}")
            # 폴백으로 기존 템플릿 응답 사용
            return self._generate_role_specific_response(agent)