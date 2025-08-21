import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const PersonaEditor = ({ isOpen, onClose, onUpdate }) => {
  const [personas, setPersonas] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [formData, setFormData] = useState({
    role: '',
    goal: '',
    backstory: ''
  });

  useEffect(() => {
    if (isOpen) {
      fetchPersonas();
    }
  }, [isOpen]);

  const fetchPersonas = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/personas');
      const data = await response.json();
      if (data.success) {
        setPersonas(data.personas);
        // 첫 번째 에이전트를 기본 선택
        const firstAgent = Object.keys(data.personas)[0];
        if (firstAgent) {
          setSelectedAgent(firstAgent);
          setFormData(data.personas[firstAgent]);
        }
      }
    } catch (error) {
      console.error('페르소나 정보 가져오기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentSelect = (agentName) => {
    setSelectedAgent(agentName);
    setFormData(personas[agentName] || { role: '', goal: '', backstory: '' });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleUpdate = async () => {
    if (!selectedAgent) return;

    setLoading(true);
    try {
      const response = await fetch('/api/personas/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_name: selectedAgent,
          ...formData
        }),
      });

      const data = await response.json();
      if (data.success) {
        // 로컬 상태 업데이트
        setPersonas(prev => ({
          ...prev,
          [selectedAgent]: formData
        }));
        
        if (onUpdate) {
          onUpdate(selectedAgent, formData);
        }
        
        alert('페르소나가 성공적으로 업데이트되었습니다!');
      } else {
        alert(`업데이트 실패: ${data.error}`);
      }
    } catch (error) {
      console.error('페르소나 업데이트 실패:', error);
      alert('페르소나 업데이트 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('모든 페르소나를 기본값으로 리셋하시겠습니까?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/personas/reset', {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        // 페르소나 정보 다시 가져오기
        await fetchPersonas();
        alert('모든 페르소나가 기본값으로 리셋되었습니다!');
      } else {
        alert(`리셋 실패: ${data.error}`);
      }
    } catch (error) {
      console.error('페르소나 리셋 실패:', error);
      alert('페르소나 리셋 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Overlay>
      <Modal>
        <Header>
          <Title>전문가 페르소나 편집</Title>
          <CloseButton onClick={onClose}>×</CloseButton>
        </Header>
        
        <Content>
          {loading ? (
            <LoadingMessage>로딩 중...</LoadingMessage>
          ) : (
            <>
              <AgentSelector>
                <SelectorLabel>전문가 선택:</SelectorLabel>
                <AgentTabs>
                  {Object.keys(personas).map(agentName => (
                    <AgentTab
                      key={agentName}
                      active={selectedAgent === agentName}
                      onClick={() => handleAgentSelect(agentName)}
                    >
                      {agentName}
                    </AgentTab>
                  ))}
                </AgentTabs>
              </AgentSelector>

              {selectedAgent && (
                <FormContainer>
                  <FormGroup>
                    <Label>역할 (Role):</Label>
                    <Input
                      type="text"
                      value={formData.role}
                      onChange={(e) => handleInputChange('role', e.target.value)}
                      placeholder="전문가의 역할을 입력하세요"
                    />
                  </FormGroup>

                  <FormGroup>
                    <Label>목표 (Goal):</Label>
                    <TextArea
                      value={formData.goal}
                      onChange={(e) => handleInputChange('goal', e.target.value)}
                      placeholder="전문가의 목표를 입력하세요"
                      rows={3}
                    />
                  </FormGroup>

                  <FormGroup>
                    <Label>배경 스토리 (Backstory):</Label>
                    <TextArea
                      value={formData.backstory}
                      onChange={(e) => handleInputChange('backstory', e.target.value)}
                      placeholder="전문가의 배경 스토리를 입력하세요"
                      rows={6}
                    />
                  </FormGroup>
                </FormContainer>
              )}
            </>
          )}
        </Content>

        <Footer>
          <ResetButton onClick={handleReset} disabled={loading}>
            전체 리셋
          </ResetButton>
          <ButtonGroup>
            <CancelButton onClick={onClose} disabled={loading}>
              취소
            </CancelButton>
            <UpdateButton 
              onClick={handleUpdate} 
              disabled={loading || !selectedAgent}
            >
              {loading ? '업데이트 중...' : '업데이트'}
            </UpdateButton>
          </ButtonGroup>
        </Footer>
      </Modal>
    </Overlay>
  );
};

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
`;

const Modal = styled.div`
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #333;
  background: #0f0f0f;
`;

const Title = styled.h2`
  margin: 0;
  color: #fff;
  font-size: 1.4rem;
  font-weight: 600;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #999;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;

  &:hover {
    background: #333;
    color: #fff;
  }
`;

const Content = styled.div`
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #999;
  padding: 40px;
  font-size: 1.1rem;
`;

const AgentSelector = styled.div`
  margin-bottom: 24px;
`;

const SelectorLabel = styled.div`
  color: #fff;
  font-weight: 500;
  margin-bottom: 12px;
`;

const AgentTabs = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const AgentTab = styled.button`
  background: ${props => props.active ? '#007acc' : '#333'};
  color: ${props => props.active ? '#fff' : '#ccc'};
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.active ? '#0066aa' : '#444'};
    color: #fff;
  }
`;

const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  color: #fff;
  font-weight: 500;
  font-size: 0.95rem;
`;

const Input = styled.input`
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 12px;
  color: #fff;
  font-size: 0.95rem;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #007acc;
  }

  &::placeholder {
    color: #666;
  }
`;

const TextArea = styled.textarea`
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 12px;
  color: #fff;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #007acc;
  }

  &::placeholder {
    color: #666;
  }
`;

const Footer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid #333;
  background: #0f0f0f;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const UpdateButton = styled(Button)`
  background: #007acc;
  color: #fff;

  &:hover:not(:disabled) {
    background: #0066aa;
  }
`;

const CancelButton = styled(Button)`
  background: #666;
  color: #fff;

  &:hover:not(:disabled) {
    background: #777;
  }
`;

const ResetButton = styled(Button)`
  background: #dc3545;
  color: #fff;

  &:hover:not(:disabled) {
    background: #c82333;
  }
`;

export default PersonaEditor;