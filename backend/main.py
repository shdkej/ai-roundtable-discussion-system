from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime
import json
import asyncio
import os
from chat_roundtable import ChatRoundtable, ChatMessage
# from memory_system import FAISSMemorySystem  # 임시 비활성화

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 연결된 웹소켓 클라이언트들
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket 클라이언트 연결됨. 총 연결 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket 클라이언트 연결 해제됨. 총 연결 수: {len(self.active_connections)}")

    def has_connected_clients(self) -> bool:
        """연결된 클라이언트가 있는지 확인"""
        # 실제로 연결이 살아있는지 확인
        active_connections = []
        for connection in self.active_connections:
            try:
                # WebSocket 상태 확인
                if hasattr(connection, 'client_state') and connection.client_state.name != 'DISCONNECTED':
                    active_connections.append(connection)
            except:
                # 연결이 끊어진 경우 제거 대상
                pass
        
        # 실제 활성 연결 목록 업데이트
        self.active_connections = active_connections
        return len(self.active_connections) > 0

    def get_connection_count(self) -> int:
        """현재 연결된 클라이언트 수 반환"""
        self.has_connected_clients()  # 연결 상태 갱신
        return len(self.active_connections)

    async def broadcast(self, message: dict):
        if not self.has_connected_clients():
            print("연결된 클라이언트가 없어 브로드캐스트를 건너뜁니다.")
            return False
        
        disconnected = []
        successful_sends = 0
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
                successful_sends += 1
            except Exception as e:
                print(f"브로드캐스트 오류: {e}")
                disconnected.append(connection)
        
        # 연결이 끊어진 클라이언트 제거
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
        
        print(f"브로드캐스트 완료: {successful_sends}명에게 전송, {len(disconnected)}개 연결 제거")
        return successful_sends > 0

manager = ConnectionManager()

# 토론 시스템 및 메모리 시스템 인스턴스
chat_system: Optional[ChatRoundtable] = None
auto_discussion_task: Optional[asyncio.Task] = None
# memory_system = FAISSMemorySystem()  # 임시 비활성화
memory_system = None
current_room_id: Optional[str] = None

# 요청/응답 모델
class StartDiscussionRequest(BaseModel):
    topic: str
    participants: List[str]
    company_info: Dict[str, str]

class UserMessageRequest(BaseModel):
    content: str

class ExpertQuestionRequest(BaseModel):
    expert: str
    question: str

class DeepDiveRequest(BaseModel):
    question: str
    focus_area: str = "전체"

class CreateChatroomRequest(BaseModel):
    room_name: str

class AddContextRequest(BaseModel):
    context: str
    agent_name: Optional[str] = None  # None이면 공통 맥락
    metadata: Optional[Dict] = None

class SearchContextRequest(BaseModel):
    query: str
    agent_name: Optional[str] = None  # None이면 공통 맥락 검색
    room_id: Optional[str] = None  # 채팅방 검색
    top_k: int = 5

class SwitchChatroomRequest(BaseModel):
    room_id: str

class PersonaRequest(BaseModel):
    agent_name: str
    role: str
    goal: str
    backstory: str

class UpdatePersonaRequest(BaseModel):
    agent_name: str
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None

# 연결 상태 확인 헬퍼 함수
def check_websocket_connection():
    """WebSocket 연결 상태를 확인하고 연결이 없으면 에러 반환"""
    print(f"=== WebSocket 연결 상태 확인 ===")
    has_clients = manager.has_connected_clients()
    connection_count = manager.get_connection_count()
    print(f"연결된 클라이언트 있음: {has_clients}")
    print(f"연결 수: {connection_count}")
    print(f"활성 연결 목록 길이: {len(manager.active_connections)}")
    
    if not has_clients:
        print("WebSocket 연결 실패: 클라이언트가 연결되지 않음")
        return {
            "success": False, 
            "error": "WebSocket 클라이언트가 연결되지 않았습니다. 프론트엔드를 새로고침하거나 다시 연결해주세요.",
            "connection_count": 0
        }
    
    print("WebSocket 연결 성공")
    return {
        "success": True,
        "connection_count": connection_count
    }

# 메시지를 dict로 변환하는 헬퍼 함수
def message_to_dict(msg: ChatMessage) -> dict:
    import hashlib
    # 메시지 내용으로 고유 ID 생성
    content_hash = hashlib.md5(f"{msg.sender}_{msg.content}_{msg.timestamp.isoformat()}".encode()).hexdigest()[:8]
    return {
        "id": f"{msg.timestamp.isoformat()}_{msg.sender}_{content_hash}",
        "sender": msg.sender,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat(),
        "message_type": msg.message_type
    }

# API 엔드포인트
@app.post("/api/start_discussion")
async def start_discussion(request: StartDiscussionRequest):
    global chat_system, auto_discussion_task, current_room_id
    
    print(f"=== start_discussion API 호출 시작 ===")
    print(f"요청 데이터: topic={request.topic}, participants={request.participants}")
    print(f"회사 정보: {request.company_info}")
    
    # WebSocket 연결 상태 확인
    connection_check = check_websocket_connection()
    print(f"WebSocket 연결 상태: {connection_check}")
    if not connection_check["success"]:
        print(f"WebSocket 연결 실패: {connection_check}")
        return connection_check
    
    try:
        print("1. 기존 자동 토론 중지 시도...")
        # 기존 자동 토론 중지
        if auto_discussion_task and not auto_discussion_task.done():
            auto_discussion_task.cancel()
            print("기존 자동 토론 태스크 취소됨")
        
        print("2. 새 채팅방 생성...")
        # 새 채팅방 생성
        room_name = f"토론: {request.topic[:50]}{'...' if len(request.topic) > 50 else ''}"
        if memory_system:
            current_room_id = memory_system.create_chatroom(room_name, request.topic)
        else:
            import uuid
            current_room_id = str(uuid.uuid4())
        print(f"채팅방 생성됨: room_id={current_room_id}, room_name={room_name}, topic={request.topic}")
        
        print("3. 새 토론 시스템 초기화...")
        # 새 토론 시스템 초기화
        try:
            chat_system = ChatRoundtable()
            print("ChatRoundtable 인스턴스 생성됨")
        except Exception as e:
            import traceback
            print(f"ChatRoundtable 인스턴스 생성 실패: {str(e)}")
            print("상세 오류 정보:")
            traceback.print_exc()
            raise e
        
        print("4. 토론 시작...")
        try:
            start_msg = chat_system.start_discussion(
                request.topic, 
                request.company_info, 
                request.participants
            )
            print(f"토론 시작 메시지 생성됨: sender={start_msg.sender}, content_length={len(start_msg.content)}")
            
            # active_agents 상태 확인
            print(f"활성 에이전트 수: {len(chat_system.active_agents)}")
            for i, agent in enumerate(chat_system.active_agents):
                print(f"  에이전트 {i+1}: {agent.role}")
                
        except Exception as e:
            import traceback
            print(f"토론 시작 실패: {str(e)}")
            print("상세 오류 정보:")
            traceback.print_exc()
            raise e
        
        print("5. 시작 메시지를 메모리에 저장...")
        # 시작 메시지를 메모리에 저장
        memory_system.add_message_to_chatroom(
            current_room_id, 
            start_msg.sender, 
            start_msg.content, 
            start_msg.timestamp.isoformat()
        )
        print("시작 메시지 메모리 저장 완료")
        
        print("6. 초기 의견 수집...")
        # 초기 의견 수집
        initial_opinions = chat_system.get_initial_opinions()
        print(f"초기 의견 {len(initial_opinions)}개 수집됨")
        
        print("7. 초기 의견들을 메모리에 저장...")
        # 초기 의견들도 메모리에 저장
        for i, opinion in enumerate(initial_opinions):
            memory_system.add_message_to_chatroom(
                current_room_id,
                opinion.sender,
                opinion.content,
                opinion.timestamp.isoformat()
            )
            print(f"  의견 {i+1} 저장: {opinion.sender}")
        print("초기 의견들 메모리 저장 완료")
        
        print("8. 토론 주제를 공통 맥락에 저장...")
        # 토론 주제를 공통 맥락에 저장
        memory_system.add_common_context(
            f"토론 주제: {request.topic}",
            {"type": "discussion_topic", "room_id": current_room_id}
        )
        print("토론 주제 공통 맥락 저장 완료")
        
        print("9. 회사 정보를 공통 맥락에 저장...")
        # 회사 정보를 공통 맥락에 저장
        company_context = f"회사 정보 - 규모: {request.company_info.get('company_size', '')}, " \
                         f"산업: {request.company_info.get('industry', '')}, " \
                         f"매출: {request.company_info.get('revenue', '')}, " \
                         f"과제: {request.company_info.get('current_challenge', '')}"
        memory_system.add_common_context(
            company_context,
            {"type": "company_info", "room_id": current_room_id}
        )
        print("회사 정보 공통 맥락 저장 완료")
        
        print("10. 응답 데이터 준비...")
        # 모든 메시지 준비
        messages = [start_msg] + initial_opinions
        response_data = {
            "success": True,
            "messages": [message_to_dict(msg) for msg in messages],
            "room_id": current_room_id
        }
        print(f"응답 데이터 준비 완료: 메시지 {len(messages)}개")
        
        print("11. 웹소켓으로 브로드캐스트...")
        # 웹소켓으로 브로드캐스트
        broadcast_result = await manager.broadcast({
            "type": "discussion_started",
            "data": response_data
        })
        print(f"웹소켓 브로드캐스트 결과: {broadcast_result}")
        
        print("=== start_discussion API 성공 완료 ===")
        return response_data
        
    except Exception as e:
        import traceback
        print(f"=== start_discussion API 오류 발생 ===")
        print(f"오류 메시지: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        print("상세 오류 정보:")
        traceback.print_exc()
        print("=== 오류 정보 끝 ===")
        return {"success": False, "error": str(e)}

@app.post("/api/start_auto_discussion")
async def start_auto_discussion():
    global auto_discussion_task
    
    # WebSocket 연결 상태 확인
    connection_check = check_websocket_connection()
    if not connection_check["success"]:
        return connection_check
    
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    # 자동 토론 시작
    start_msg = chat_system.start_auto_discussion()
    
    # 자동 토론 태스크 시작
    auto_discussion_task = asyncio.create_task(auto_discussion_loop())
    
    await manager.broadcast({
        "type": "message",
        "data": message_to_dict(start_msg)
    })
    
    return {"success": True, "message": message_to_dict(start_msg)}

@app.post("/api/pause_auto_discussion")
async def pause_auto_discussion():
    global auto_discussion_task
    
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    print("=== 자동 토론 일시정지 요청 ===")
    
    # 즉시 상태 변경 (다른 프로세스에서 확인할 수 있도록)
    chat_system.auto_discussion_enabled = False
    chat_system.discussion_state = "paused"
    print(f"상태 변경 완료: enabled={chat_system.auto_discussion_enabled}, state={chat_system.discussion_state}")
    
    # 자동 토론 태스크 강제 취소
    if auto_discussion_task and not auto_discussion_task.done():
        print("자동 토론 태스크 취소 중...")
        auto_discussion_task.cancel()
        try:
            await asyncio.wait_for(auto_discussion_task, timeout=2.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("자동 토론 태스크 취소됨")
        except Exception as e:
            print(f"태스크 취소 중 오류: {e}")
    
    # 태스크 참조 초기화
    auto_discussion_task = None
    print("자동 토론 일시정지 완료")
    
    pause_msg = chat_system.pause_auto_discussion()
    
    await manager.broadcast({
        "type": "message",
        "data": message_to_dict(pause_msg)
    })
    
    return {"success": True, "message": message_to_dict(pause_msg)}

@app.post("/api/resume_auto_discussion")
async def resume_auto_discussion():
    global auto_discussion_task
    
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    print("=== 자동 토론 재개 요청 ===")
    
    # 기존 태스크가 있다면 정리
    if auto_discussion_task and not auto_discussion_task.done():
        print("기존 태스크 정리 중...")
        auto_discussion_task.cancel()
        try:
            await asyncio.wait_for(auto_discussion_task, timeout=1.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    
    # 자동 토론 재개
    resume_msg = chat_system.resume_auto_discussion()
    print(f"상태 변경 완료: enabled={chat_system.auto_discussion_enabled}, state={chat_system.discussion_state}")
    
    # 새로운 자동 토론 태스크 시작
    auto_discussion_task = asyncio.create_task(auto_discussion_loop())
    print("새로운 자동 토론 태스크 시작")
    
    await manager.broadcast({
        "type": "message",
        "data": message_to_dict(resume_msg)
    })
    
    return {"success": True, "message": message_to_dict(resume_msg)}

@app.post("/api/stop_auto_discussion")
async def stop_auto_discussion():
    global auto_discussion_task
    
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    print("=== 자동 토론 중지 요청 ===")
    
    # 즉시 상태 변경 (다른 프로세스에서 확인할 수 있도록)
    chat_system.auto_discussion_enabled = False
    chat_system.discussion_state = "ready"
    chat_system.user_intervention_pending = False
    print(f"상태 변경 완료: enabled={chat_system.auto_discussion_enabled}")
    
    # 자동 토론 태스크 강제 취소
    if auto_discussion_task and not auto_discussion_task.done():
        print("자동 토론 태스크 취소 중...")
        auto_discussion_task.cancel()
        try:
            await asyncio.wait_for(auto_discussion_task, timeout=2.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("자동 토론 태스크 취소됨")
        except Exception as e:
            print(f"태스크 취소 중 오류: {e}")
    
    # 태스크 참조 초기화
    auto_discussion_task = None
    print("자동 토론 완전 중지 완료")
    
    stop_msg = ChatMessage(
        sender="시스템",
        content="⏹️ 자동 토론이 중지되었습니다.",
        message_type="system"
    )
    chat_system.chat_history.append(stop_msg)
    
    await manager.broadcast({
        "type": "message",
        "data": message_to_dict(stop_msg)
    })
    
    return {"success": True, "message": message_to_dict(stop_msg)}

@app.post("/api/request_intervention")
async def request_intervention():
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    # 사용자 개입 요청
    intervention_msg = chat_system.request_user_intervention()
    
    await manager.broadcast({
        "type": "message",
        "data": message_to_dict(intervention_msg)
    })
    
    await manager.broadcast({
        "type": "user_intervention_requested",
        "data": {}
    })
    
    return {"success": True, "message": message_to_dict(intervention_msg)}

@app.post("/api/send_message")
async def send_message(request: UserMessageRequest):
    global current_room_id
    
    print(f"=== send_message API 호출 시작 ===")
    print(f"요청 내용: {request.content}")
    print(f"현재 room_id: {current_room_id}")
    
    # WebSocket 연결 상태 확인
    connection_check = check_websocket_connection()
    print(f"WebSocket 연결 상태: {connection_check}")
    if not connection_check["success"]:
        print(f"WebSocket 연결 실패: {connection_check}")
        return connection_check
    
    if not chat_system:
        print("토론 시스템이 초기화되지 않음")
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        # 사용자 메시지 처리
        if chat_system.user_intervention_pending:
            print("사용자 개입 후 토론 재개 모드")
            # 사용자 개입 후 토론 재개
            user_msg = ChatMessage("사용자", request.content)
            chat_system.chat_history.append(user_msg)
            print(f"사용자 메시지 생성: {user_msg.sender} - {user_msg.content}")
            
            # 사용자 메시지를 메모리에 저장
            if current_room_id:
                memory_system.add_message_to_chatroom(
                    current_room_id,
                    user_msg.sender,
                    user_msg.content,
                    user_msg.timestamp.isoformat()
                )
                print("사용자 메시지 메모리 저장 완료")
            
            continue_msg = chat_system.continue_after_user_intervention()
            print(f"토론 재개 메시지 생성: {continue_msg.sender} - {continue_msg.content}")
            
            # 응답 메시지도 메모리에 저장
            if current_room_id:
                memory_system.add_message_to_chatroom(
                    current_room_id,
                    continue_msg.sender,
                    continue_msg.content,
                    continue_msg.timestamp.isoformat()
                )
                print("토론 재개 메시지 메모리 저장 완료")
            
            # 메시지들 브로드캐스트
            print("사용자 메시지 브로드캐스트 시작...")
            user_broadcast_result = await manager.broadcast({
                "type": "message",
                "data": message_to_dict(user_msg)
            })
            print(f"사용자 메시지 브로드캐스트 결과: {user_broadcast_result}")
            
            print("토론 재개 메시지 브로드캐스트 시작...")
            continue_broadcast_result = await manager.broadcast({
                "type": "message", 
                "data": message_to_dict(continue_msg)
            })
            print(f"토론 재개 메시지 브로드캐스트 결과: {continue_broadcast_result}")
            
            # 자동 토론 재개
            global auto_discussion_task
            auto_discussion_task = asyncio.create_task(auto_discussion_loop())
            print("자동 토론 태스크 재시작")
            
            return {"success": True, "messages": [message_to_dict(user_msg), message_to_dict(continue_msg)]}
        else:
            print("일반 토론 진행 모드")
            # 일반 토론 진행
            response = chat_system.continue_discussion(request.content)
            print(f"토론 응답 생성: {response.sender} - {response.content}")
            
            # 응답을 메모리에 저장
            if current_room_id:
                memory_system.add_message_to_chatroom(
                    current_room_id,
                    response.sender,
                    response.content,
                    response.timestamp.isoformat()
                )
                print("토론 응답 메모리 저장 완료")
            
            print("토론 응답 브로드캐스트 시작...")
            broadcast_result = await manager.broadcast({
                "type": "message",
                "data": message_to_dict(response)
            })
            print(f"토론 응답 브로드캐스트 결과: {broadcast_result}")
            
            return {"success": True, "message": message_to_dict(response)}
            
    except Exception as e:
        import traceback
        print(f"=== send_message API 오류 발생 ===")
        print(f"오류 메시지: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        print("상세 오류 정보:")
        traceback.print_exc()
        print("=== 오류 정보 끝 ===")
        return {"success": False, "error": str(e)}

@app.post("/api/ask_expert")
async def ask_expert(request: ExpertQuestionRequest):
    print(f"=== ask_expert API 호출 시작 ===")
    print(f"전문가: {request.expert}")
    print(f"질문: {request.question}")
    
    # WebSocket 연결 상태 확인
    connection_check = check_websocket_connection()
    print(f"WebSocket 연결 상태: {connection_check}")
    if not connection_check["success"]:
        print(f"WebSocket 연결 실패: {connection_check}")
        return connection_check
    
    if not chat_system:
        print("토론 시스템이 초기화되지 않음")
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        response = chat_system.ask_specific_person(request.expert, request.question)
        print(f"전문가 응답 생성: {response.sender} - {response.content}")
        
        print("전문가 응답 브로드캐스트 시작...")
        broadcast_result = await manager.broadcast({
            "type": "message",
            "data": message_to_dict(response)
        })
        print(f"전문가 응답 브로드캐스트 결과: {broadcast_result}")
        
        return {"success": True, "message": message_to_dict(response)}
        
    except Exception as e:
        import traceback
        print(f"=== ask_expert API 오류 발생 ===")
        print(f"오류 메시지: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        print("상세 오류 정보:")
        traceback.print_exc()
        print("=== 오류 정보 끝 ===")
        return {"success": False, "error": str(e)}

@app.post("/api/deep_dive")
async def deep_dive(request: DeepDiveRequest):
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        response = chat_system.deep_dive_question(request.question, request.focus_area)
        
        await manager.broadcast({
            "type": "message",
            "data": message_to_dict(response)
        })
        
        return {"success": True, "message": message_to_dict(response)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/get_conclusion")
async def get_conclusion():
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        conclusion = chat_system.get_conclusion()
        
        await manager.broadcast({
            "type": "message",
            "data": message_to_dict(conclusion)
        })
        
        return {"success": True, "message": message_to_dict(conclusion)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/status")
async def get_status():
    # 연결 상태 정보 포함
    connection_count = manager.get_connection_count()
    has_connections = manager.has_connected_clients()
    
    if not chat_system:
        return {
            "discussion_started": False,
            "current_room_id": current_room_id,
            "websocket_connected": has_connections,
            "connection_count": connection_count
        }
    
    speaker_info = chat_system.get_current_speaker_info()
    
    return {
        "discussion_started": True,
        "auto_discussion_enabled": chat_system.auto_discussion_enabled,
        "user_intervention_pending": chat_system.user_intervention_pending,
        "discussion_state": chat_system.discussion_state,
        "discussion_rounds": chat_system.discussion_rounds,
        "current_speaker": speaker_info,
        "total_messages": len(chat_system.chat_history),
        "current_room_id": current_room_id,
        "websocket_connected": has_connections,
        "connection_count": connection_count
    }

# 메모리 시스템 API 엔드포인트들
@app.post("/api/memory/create_chatroom")
async def create_chatroom(request: CreateChatroomRequest):
    try:
        room_id = memory_system.create_chatroom(request.room_name)
        return {"success": True, "room_id": room_id}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/memory/chatrooms")
async def get_chatrooms():
    try:
        chatrooms = memory_system.get_chatroom_list()
        return {"success": True, "chatrooms": chatrooms}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/memory/add_context")
async def add_context(request: AddContextRequest):
    try:
        if request.agent_name:
            memory_system.add_agent_context(request.agent_name, request.context, request.metadata)
        else:
            memory_system.add_common_context(request.context, request.metadata)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/memory/search")
async def search_context(request: SearchContextRequest):
    try:
        if request.room_id:
            # 채팅방 검색
            results = memory_system.search_chatroom_context(request.room_id, request.query, request.top_k)
        elif request.agent_name:
            # 에이전트별 맥락 검색
            results = memory_system.search_agent_context(request.agent_name, request.query, request.top_k)
        else:
            # 공통 맥락 검색
            results = memory_system.search_common_context(request.query, request.top_k)
        
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/memory/stats")
async def get_memory_stats():
    try:
        stats = {
            "common_memory": memory_system.get_common_memory().get_stats(),
            "agent_memories": {
                name: memory.get_stats() 
                for name, memory in memory_system.agent_memories.items()
            },
            "chatroom_memories": {
                room_id: memory.get_stats() 
                for room_id, memory in memory_system.chatroom_memories.items()
            },
            "total_chatrooms": len(memory_system.get_chatroom_list())
        }
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/memory/chatroom/{room_id}/conversation")
async def get_chatroom_conversation(room_id: str):
    try:
        # MD 파일 읽기
        md_path = f"{memory_system.memory_dir}/chatrooms/{room_id}_conversation.md"
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        else:
            return {"success": False, "error": "대화 기록을 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/switch_chatroom")
async def switch_chatroom(request: SwitchChatroomRequest):
    global current_room_id, chat_system, auto_discussion_task
    
    try:
        # 채팅방 존재 확인
        chatrooms = memory_system.get_chatroom_list()
        room_exists = any(room['id'] == request.room_id for room in chatrooms)
        
        if not room_exists:
            return {"success": False, "error": "채팅방을 찾을 수 없습니다."}
        
        # 기존 자동 토론 중지
        if auto_discussion_task and not auto_discussion_task.done():
            auto_discussion_task.cancel()
        
        # 채팅방 전환
        old_room_id = current_room_id
        current_room_id = request.room_id
        
        # 기존 토론 시스템 정리
        if chat_system:
            chat_system.auto_discussion_enabled = False
            chat_system.discussion_state = "ready"
            chat_system.user_intervention_pending = False
        
        # 채팅방 정보 가져오기
        room_info = next(room for room in chatrooms if room['id'] == request.room_id)
        
        # 채팅방 대화 기록 로드
        conversation_content = ""
        md_path = f"{memory_system.memory_dir}/chatrooms/{request.room_id}_conversation.md"
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                conversation_content = f.read()
        
        await manager.broadcast({
            "type": "chatroom_switched",
            "data": {
                "room_id": current_room_id,
                "room_info": room_info,
                "conversation_content": conversation_content,
                "previous_room_id": old_room_id
            }
        })
        
        return {
            "success": True, 
            "room_id": current_room_id,
            "room_info": room_info,
            "conversation_content": conversation_content
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# 페르소나 관리 API 엔드포인트들
@app.get("/api/personas")
async def get_personas():
    """현재 에이전트들의 페르소나 정보 반환"""
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        personas = {}
        agent_map = {
            "디자인팀": chat_system.design_agent,
            "영업팀": chat_system.sales_agent,
            "생산팀": chat_system.production_agent,
            "마케팅팀": chat_system.marketing_agent,
            "IT팀": chat_system.it_agent,
            "진행자": chat_system.moderator
        }
        
        for agent_name, agent in agent_map.items():
            personas[agent_name] = {
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory
            }
        
        return {"success": True, "personas": personas}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/personas/update")
async def update_persona(request: UpdatePersonaRequest):
    """특정 에이전트의 페르소나 업데이트"""
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        agent_map = {
            "디자인팀": chat_system.design_agent,
            "영업팀": chat_system.sales_agent,
            "생산팀": chat_system.production_agent,
            "마케팅팀": chat_system.marketing_agent,
            "IT팀": chat_system.it_agent,
            "진행자": chat_system.moderator
        }
        
        if request.agent_name not in agent_map:
            return {"success": False, "error": f"존재하지 않는 에이전트: {request.agent_name}"}
        
        agent = agent_map[request.agent_name]
        
        # 업데이트할 필드만 변경
        if request.role is not None:
            agent.role = request.role
        if request.goal is not None:
            agent.goal = request.goal
        if request.backstory is not None:
            agent.backstory = request.backstory
        
        # 업데이트된 페르소나 정보 브로드캐스트
        await manager.broadcast({
            "type": "persona_updated",
            "data": {
                "agent_name": request.agent_name,
                "persona": {
                    "role": agent.role,
                    "goal": agent.goal,
                    "backstory": agent.backstory
                }
            }
        })
        
        return {"success": True, "message": f"{request.agent_name} 페르소나가 업데이트되었습니다."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/personas/reset")
async def reset_personas():
    """모든 에이전트 페르소나를 기본값으로 리셋"""
    if not chat_system:
        return {"success": False, "error": "토론이 시작되지 않았습니다."}
    
    try:
        # 새로운 에이전트들을 다시 설정
        chat_system.setup_agents()
        
        # 활성 에이전트 목록 갱신 (기존 참여자 기준으로)
        if hasattr(chat_system, 'active_agents') and chat_system.active_agents:
            # 기존 활성 에이전트들의 역할 저장
            active_roles = [agent.role for agent in chat_system.active_agents]
            
            # 새로 설정된 에이전트들로 활성 목록 갱신
            new_active_agents = []
            for role in active_roles:
                if "디자인" in role:
                    new_active_agents.append(chat_system.design_agent)
                elif "영업" in role:
                    new_active_agents.append(chat_system.sales_agent)
                elif "생산" in role:
                    new_active_agents.append(chat_system.production_agent)
                elif "마케팅" in role:
                    new_active_agents.append(chat_system.marketing_agent)
                elif "IT" in role:
                    new_active_agents.append(chat_system.it_agent)
            
            chat_system.active_agents = new_active_agents
        
        # 리셋 완료 브로드캐스트
        await manager.broadcast({
            "type": "personas_reset",
            "data": {"message": "모든 페르소나가 기본값으로 리셋되었습니다."}
        })
        
        return {"success": True, "message": "모든 페르소나가 기본값으로 리셋되었습니다."}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 자동 토론 루프
async def auto_discussion_loop():
    try:
        while chat_system and chat_system.auto_discussion_enabled:
            # 더 빠른 체크를 위해 0.5초 간격으로 상태 확인
            for _ in range(6):  # 3초 총 대기를 위해 0.5초씩 6번
                await asyncio.sleep(0.5)
                if not chat_system or not chat_system.auto_discussion_enabled:
                    print("자동 토론 중지 신호 감지됨")
                    return
            
            if not chat_system.auto_discussion_enabled:
                break
            
            # WebSocket 연결 상태 확인
            if not manager.has_connected_clients():
                print("자동 토론 중단: WebSocket 클라이언트가 연결되지 않음")
                # 자동 토론 일시정지
                if chat_system:
                    chat_system.auto_discussion_enabled = False
                break
            
            # 콜백 함수 정의
            async def broadcast_callback(event_type, data):
                # 브로드캐스트 전에 연결 상태 확인
                if not manager.has_connected_clients():
                    print(f"브로드캐스트 건너뜀 ({event_type}): 연결된 클라이언트 없음")
                    return
                
                if event_type == "typing_start":
                    success = await manager.broadcast({
                        "type": "typing_start",
                        "data": data
                    })
                    if not success:
                        print("typing_start 브로드캐스트 실패")
                elif event_type == "typing_stop":
                    success = await manager.broadcast({
                        "type": "typing_stop",
                        "data": {}
                    })
                    if not success:
                        print("typing_stop 브로드캐스트 실패")
                elif event_type == "message":
                    # 메시지를 메모리에 저장
                    if current_room_id and hasattr(data, 'sender'):
                        memory_system.add_message_to_chatroom(
                            current_room_id,
                            data.sender,
                            data.content,
                            data.timestamp.isoformat()
                        )
                    
                    success = await manager.broadcast({
                        "type": "message",
                        "data": message_to_dict(data)
                    })
                    if not success:
                        print("message 브로드캐스트 실패")
            
            # 중지 신호 재확인
            if not chat_system or not chat_system.auto_discussion_enabled:
                print("자동 토론 중지됨 - 응답 생성 전")
                break
            
            # 비동기 응답 생성 (실시간 스트리밍) - 취소 가능하게 함
            try:
                response_task = asyncio.create_task(
                    chat_system.generate_auto_response_async(broadcast_callback)
                )
                response = await asyncio.wait_for(response_task, timeout=30.0)
                
                if not chat_system.auto_discussion_enabled:
                    print("자동 토론 중지됨 - 응답 생성 후")
                    break
                    
            except asyncio.TimeoutError:
                print("자동 응답 생성 타임아웃")
                continue
            except asyncio.CancelledError:
                print("자동 응답 생성 취소됨")
                break
            except Exception as e:
                print(f"자동 응답 생성 오류: {e}")
                continue
            
            if response:
                # 사용자 개입이 요청된 경우
                if chat_system.user_intervention_pending:
                    await manager.broadcast({
                        "type": "user_intervention_requested",
                        "data": {}
                    })
                    break
                    
    except asyncio.CancelledError:
        # 태스크가 취소된 경우
        pass
    except Exception as e:
        print(f"자동 토론 루프 오류: {e}")

@app.get("/api/websocket/status")
async def get_websocket_status():
    """WebSocket 연결 상태 확인 전용 엔드포인트"""
    connection_count = manager.get_connection_count()
    has_connections = manager.has_connected_clients()
    
    return {
        "success": True,
        "websocket_connected": has_connections,
        "connection_count": connection_count,
        "active_connections": len(manager.active_connections)
    }

# WebSocket 엔드포인트
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"WebSocket 클라이언트 연결됨: {websocket.client}")
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신 (heartbeat 등)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get('type') == 'ping':
                    # ping에 대한 pong 응답
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "data": {"timestamp": datetime.datetime.now().isoformat()}
                    }))
                else:
                    print(f"클라이언트 메시지 수신: {data}")
            except json.JSONDecodeError:
                print(f"유효하지 않은 JSON 메시지: {data}")
                
    except WebSocketDisconnect:
        print(f"WebSocket 클라이언트 정상 연결 해제: {websocket.client}")
    except Exception as e:
        print(f"WebSocket 연결 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.disconnect(websocket)
        print(f"WebSocket 연결 정리 완료: {websocket.client}")

# uvicorn으로 실행할 때는 이 부분을 주석 처리
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)