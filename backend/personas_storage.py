import json
import os
from typing import Dict, Any
from chat_roundtable import get_default_personas

class PersonaStorage:
    """페르소나 저장 및 관리 클래스"""
    
    def __init__(self, storage_file: str = "custom_personas.json"):
        self.storage_file = storage_file
        self.storage_path = os.path.join(os.path.dirname(__file__), storage_file)
        
    def load_personas(self) -> Dict[str, Any]:
        """저장된 페르소나 로드, 없으면 기본 페르소나 반환"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    custom_personas = json.load(f)
                
                # 기본 페르소나와 커스텀 페르소나 병합
                default_personas = get_default_personas()
                
                # 커스텀 페르소나가 있는 경우 기본값 업데이트
                for agent_name, persona in custom_personas.items():
                    if agent_name in default_personas:
                        default_personas[agent_name].update(persona)
                
                return default_personas
            else:
                # 저장된 파일이 없으면 기본 페르소나 반환
                return get_default_personas()
                
        except Exception as e:
            print(f"페르소나 로드 실패: {e}")
            return get_default_personas()
    
    def save_personas(self, personas: Dict[str, Any]) -> bool:
        """페르소나 저장"""
        try:
            # 기본 페르소나와 다른 부분만 저장 (차분 저장)
            default_personas = get_default_personas()
            custom_personas = {}
            
            for agent_name, persona in personas.items():
                if agent_name in default_personas:
                    # 기본값과 다른 필드만 저장
                    custom_persona = {}
                    default_persona = default_personas[agent_name]
                    
                    for field in ['role', 'goal', 'backstory']:
                        if persona.get(field) != default_persona.get(field):
                            custom_persona[field] = persona[field]
                    
                    if custom_persona:  # 변경된 내용이 있을 때만 저장
                        custom_personas[agent_name] = custom_persona
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # JSON 파일로 저장
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(custom_personas, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"페르소나 저장 실패: {e}")
            return False
    
    def reset_personas(self) -> bool:
        """커스텀 페르소나 삭제 (기본값으로 리셋)"""
        try:
            if os.path.exists(self.storage_path):
                os.remove(self.storage_path)
            return True
        except Exception as e:
            print(f"페르소나 리셋 실패: {e}")
            return False
    
    def get_custom_personas(self) -> Dict[str, Any]:
        """커스텀 페르소나만 반환"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"커스텀 페르소나 로드 실패: {e}")
            return {}

# 전역 인스턴스
persona_storage = PersonaStorage()