import faiss
import numpy as np
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import uuid


class FAISSMemorySystem:
    """FAISS를 활용한 메모리 시스템"""
    
    def __init__(self, memory_dir: str = "memory_storage"):
        self.memory_dir = memory_dir
        self.embedding_dim = 128  # 간단한 해시 기반 임베딩 차원
        
        # 메모리 디렉토리 생성
        os.makedirs(memory_dir, exist_ok=True)
        os.makedirs(f"{memory_dir}/agents", exist_ok=True)
        os.makedirs(f"{memory_dir}/common", exist_ok=True)
        os.makedirs(f"{memory_dir}/chatrooms", exist_ok=True)
        
        # 각 메모리 타입별 인덱스 초기화
        self.agent_memories = {}  # 에이전트별 메모리
        self.common_memory = None  # 공통 메모리
        self.chatroom_memories = {}  # 채팅방별 메모리
        
        self._initialize_memories()
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """간단한 해시 기반 임베딩 생성"""
        # 텍스트를 해시하고 고정 크기 벡터로 변환
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # 해시를 숫자로 변환하여 임베딩 벡터 생성
        embedding = np.array([
            int(text_hash[i:i+2], 16) / 255.0  # 0-1 범위로 정규화
            for i in range(0, min(len(text_hash), self.embedding_dim * 2), 2)
        ])
        
        # 부족한 차원은 0으로 채움
        if len(embedding) < self.embedding_dim:
            embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
        else:
            embedding = embedding[:self.embedding_dim]
            
        # L2 정규화
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.reshape(1, -1).astype('float32')
    
    def _initialize_memories(self):
        """메모리 인덱스들을 초기화"""
        # 공통 메모리 초기화
        self.common_memory = MemoryIndex("common", self.memory_dir, self.embedding_dim)
        
        # 기존 에이전트 메모리 로드
        agents_dir = f"{self.memory_dir}/agents"
        if os.path.exists(agents_dir):
            for agent_file in os.listdir(agents_dir):
                if agent_file.endswith("_index.faiss"):
                    agent_name = agent_file.replace("_index.faiss", "")
                    self.agent_memories[agent_name] = MemoryIndex(
                        f"agents/{agent_name}", self.memory_dir, self.embedding_dim
                    )
        
        # 기존 채팅방 메모리 로드
        chatrooms_dir = f"{self.memory_dir}/chatrooms"
        if os.path.exists(chatrooms_dir):
            for room_file in os.listdir(chatrooms_dir):
                if room_file.endswith("_index.faiss"):
                    room_id = room_file.replace("_index.faiss", "")
                    self.chatroom_memories[room_id] = MemoryIndex(
                        f"chatrooms/{room_id}", self.memory_dir, self.embedding_dim
                    )
    
    def get_agent_memory(self, agent_name: str) -> 'MemoryIndex':
        """에이전트별 메모리 인덱스 가져오기"""
        if agent_name not in self.agent_memories:
            self.agent_memories[agent_name] = MemoryIndex(
                f"agents/{agent_name}", self.memory_dir, self.embedding_dim
            )
        return self.agent_memories[agent_name]
    
    def get_common_memory(self) -> 'MemoryIndex':
        """공통 메모리 인덱스 가져오기"""
        return self.common_memory
    
    def get_chatroom_memory(self, room_id: str) -> 'MemoryIndex':
        """채팅방별 메모리 인덱스 가져오기"""
        if room_id not in self.chatroom_memories:
            self.chatroom_memories[room_id] = MemoryIndex(
                f"chatrooms/{room_id}", self.memory_dir, self.embedding_dim
            )
        return self.chatroom_memories[room_id]
    
    def create_chatroom(self, room_name: str, topic: str = None) -> str:
        """새로운 채팅방 생성"""
        room_id = str(uuid.uuid4())
        
        # 채팅방 메타데이터 먼저 저장
        metadata = {
            "room_id": room_id,
            "room_name": room_name,
            "topic": topic or room_name,
            "created_at": datetime.now().isoformat(),
            "participants": [],
            "message_count": 0
        }
        
        metadata_path = f"{self.memory_dir}/chatrooms/{room_id}_chatroom.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 그 다음에 FAISS 메모리 인덱스 생성
        chatroom_memory = self.get_chatroom_memory(room_id)
        
        return room_id
    
    def _ensure_chatroom_metadata_exists(self, room_id: str):
        """채팅방 메타데이터 파일이 존재하는지 확인하고 없으면 생성"""
        metadata_path = f"{self.memory_dir}/chatrooms/{room_id}_chatroom.json"
        
        if not os.path.exists(metadata_path):
            print(f"채팅방 메타데이터 파일이 없어서 생성합니다: {room_id}")
            # 기본 메타데이터 생성
            metadata = {
                "room_id": room_id,
                "room_name": f"채팅방 {room_id[:8]}",
                "topic": f"채팅방 {room_id[:8]}",
                "created_at": datetime.now().isoformat(),
                "participants": [],
                "message_count": 0
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def add_message_to_chatroom(self, room_id: str, sender: str, content: str, timestamp: str = None):
        """채팅방에 메시지 추가"""
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            # 채팅방 메타데이터 파일이 없으면 생성
            self._ensure_chatroom_metadata_exists(room_id)
            
            chatroom_memory = self.get_chatroom_memory(room_id)
            
            # 메시지 데이터 구성
            message_data = {
                "sender": sender,
                "content": content,
                "timestamp": timestamp,
                "room_id": room_id
            }
            
            # 메모리에 추가
            chatroom_memory.add_memory(content, message_data)
            
            # 메타데이터 업데이트
            self._update_chatroom_metadata(room_id, sender)
            
            # MD 파일로도 저장
            self._save_message_to_md(room_id, message_data)
            
        except Exception as e:
            print(f"add_message_to_chatroom 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            # 오류가 발생해도 계속 진행
            pass
    
    def _update_chatroom_metadata(self, room_id: str, participant: str):
        """채팅방 메타데이터 업데이트"""
        metadata_path = f"{self.memory_dir}/chatrooms/{room_id}_chatroom.json"
        
        
        # 기본 메타데이터 구조 정의
        default_metadata = {
            "room_id": room_id,
            "room_name": f"채팅방 {room_id[:8]}",
            "topic": f"채팅방 {room_id[:8]}",
            "created_at": datetime.now().isoformat(),
            "participants": [],
            "message_count": 0
        }
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            metadata = default_metadata.copy()
        
        
        # metadata에 필요한 키들이 있는지 확인하고 없으면 기본값으로 추가
        for key, default_value in default_metadata.items():
            if key not in metadata:
                metadata[key] = default_value
        
        
        # 참석자 추가 (안전하게)
        participants_list = metadata.get("participants", [])
        if participant not in participants_list:
            participants_list.append(participant)
            metadata["participants"] = participants_list
        
        # 메시지 카운트 증가
        metadata["message_count"] = metadata.get("message_count", 0) + 1
        metadata["last_updated"] = datetime.now().isoformat()
        
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    
    def _save_message_to_md(self, room_id: str, message_data: Dict):
        """메시지를 MD 파일로 저장"""
        md_path = f"{self.memory_dir}/chatrooms/{room_id}_conversation.md"
        
        # 새 파일인 경우 헤더 추가
        if not os.path.exists(md_path):
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# 채팅방 대화 기록\n\n")
                f.write(f"**채팅방 ID**: {room_id}\n")
                f.write(f"**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
        
        # 메시지 추가
        with open(md_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.fromisoformat(message_data["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"## {message_data['sender']} ({timestamp})\n\n")
            f.write(f"{message_data['content']}\n\n")
            f.write("---\n\n")
    
    def search_agent_context(self, agent_name: str, query: str, top_k: int = 5) -> List[Dict]:
        """에이전트별 맥락 검색"""
        agent_memory = self.get_agent_memory(agent_name)
        return agent_memory.search(query, top_k)
    
    def search_common_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """공통 맥락 검색"""
        return self.common_memory.search(query, top_k)
    
    def search_chatroom_context(self, room_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """채팅방별 대화 내용 검색"""
        chatroom_memory = self.get_chatroom_memory(room_id)
        return chatroom_memory.search(query, top_k)
    
    def add_agent_context(self, agent_name: str, context: str, metadata: Dict = None):
        """에이전트별 맥락 추가"""
        agent_memory = self.get_agent_memory(agent_name)
        if metadata is None:
            metadata = {"agent": agent_name, "timestamp": datetime.now().isoformat()}
        else:
            metadata.update({"agent": agent_name, "timestamp": datetime.now().isoformat()})
        agent_memory.add_memory(context, metadata)
    
    def add_common_context(self, context: str, metadata: Dict = None):
        """공통 맥락 추가"""
        if metadata is None:
            metadata = {"type": "common", "timestamp": datetime.now().isoformat()}
        else:
            metadata.update({"type": "common", "timestamp": datetime.now().isoformat()})
        self.common_memory.add_memory(context, metadata)
    
    def get_chatroom_list(self) -> List[Dict]:
        """채팅방 목록 가져오기"""
        chatrooms = []
        chatrooms_dir = f"{self.memory_dir}/chatrooms"
        
        if os.path.exists(chatrooms_dir):
            for file in os.listdir(chatrooms_dir):
                if file.endswith("_chatroom.json"):
                    room_id = file.replace("_chatroom.json", "")
                    try:
                        with open(f"{chatrooms_dir}/{file}", 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            # id 필드 추가 (Sidebar에서 사용)
                            metadata["id"] = metadata.get("room_id", room_id)
                            chatrooms.append(metadata)
                    except Exception as e:
                        print(f"Error loading chatroom metadata {file}: {e}")
        
        return sorted(chatrooms, key=lambda x: x.get("last_updated", x.get("created_at", "")), reverse=True)


class MemoryIndex:
    """개별 메모리 인덱스 클래스"""
    
    def __init__(self, name: str, base_dir: str, embedding_dim: int):
        self.name = name
        self.base_dir = base_dir
        self.embedding_dim = embedding_dim
        
        self.index_path = f"{base_dir}/{name}_index.faiss"
        self.metadata_path = f"{base_dir}/{name}_metadata.json"
        
        # FAISS 인덱스와 메타데이터 로드 또는 생성
        self._load_or_create_index()
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """간단한 해시 기반 임베딩 생성"""
        # 텍스트를 해시하고 고정 크기 벡터로 변환
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # 해시를 숫자로 변환하여 임베딩 벡터 생성
        embedding = np.array([
            int(text_hash[i:i+2], 16) / 255.0  # 0-1 범위로 정규화
            for i in range(0, min(len(text_hash), self.embedding_dim * 2), 2)
        ])
        
        # 부족한 차원은 0으로 채움
        if len(embedding) < self.embedding_dim:
            embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
        else:
            embedding = embedding[:self.embedding_dim]
            
        # L2 정규화
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.reshape(1, -1).astype('float32')
    
    def _load_or_create_index(self):
        """FAISS 인덱스와 메타데이터 로드 또는 생성"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # 기존 인덱스 로드
                self.index = faiss.read_index(self.index_path)
                
                # 차원 호환성 체크
                if self.index.d != self.embedding_dim:
                    print(f"⚠️ FAISS 인덱스 차원 불일치 ({self.name}): 기존={self.index.d}, 새로운={self.embedding_dim}")
                    print(f"🔄 새로운 차원으로 인덱스 재생성...")
                    raise ValueError("차원 불일치")
                
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"✅ 기존 FAISS 인덱스 로드 완료 ({self.name}): {self.index.d}차원")
            else:
                raise FileNotFoundError("인덱스 파일 없음")
                
        except (FileNotFoundError, ValueError, Exception) as e:
            # 새 인덱스 생성
            print(f"🆕 새 FAISS 인덱스 생성 ({self.name}): {self.embedding_dim}차원")
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product (코사인 유사도)
            self.metadata = {
                "texts": [],
                "data": [],
                "created_at": datetime.now().isoformat(),
                "count": 0
            }
            self._save_index()
    
    def add_memory(self, text: str, data: Dict = None):
        """메모리에 텍스트와 메타데이터 추가"""
        if data is None:
            data = {}
        
        # 텍스트 임베딩 생성
        embedding = self._create_simple_embedding(text)
        
        # FAISS 인덱스에 추가
        self.index.add(embedding.astype('float32'))
        
        # 메타데이터 추가
        self.metadata["texts"].append(text)
        self.metadata["data"].append(data)
        self.metadata["count"] += 1
        self.metadata["last_updated"] = datetime.now().isoformat()
        
        # 저장
        self._save_index()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """쿼리로 유사한 메모리 검색"""
        if self.metadata["count"] == 0:
            return []
        
        # 쿼리 임베딩 생성
        query_embedding = self._create_simple_embedding(query)
        
        # 검색 수행
        top_k = min(top_k, self.metadata["count"])
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # 결과 구성
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx >= 0:  # 유효한 인덱스인 경우
                result = {
                    "text": self.metadata["texts"][idx],
                    "metadata": self.metadata["data"][idx],
                    "similarity_score": float(score),
                    "rank": i + 1
                }
                results.append(result)
        
        return results
    
    def _save_index(self):
        """FAISS 인덱스와 메타데이터 저장"""
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # FAISS 인덱스 저장
        faiss.write_index(self.index, self.index_path)
        
        # 메타데이터 저장
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> Dict:
        """메모리 인덱스 통계 정보"""
        return {
            "name": self.name,
            "count": self.metadata["count"],
            "created_at": self.metadata.get("created_at"),
            "last_updated": self.metadata.get("last_updated"),
            "embedding_dim": self.embedding_dim
        }