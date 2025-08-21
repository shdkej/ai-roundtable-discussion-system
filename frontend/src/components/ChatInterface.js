import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, User, Bot } from 'lucide-react';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import toast from 'react-hot-toast';
import { theme } from '../styles/theme';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 중요: flex container에서 overflow 작동하게 함 */
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${theme.spacing[4]};
  background: ${theme.colors.gray[50]};
  border-bottom: 1px solid ${theme.colors.border.light};
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${theme.colors.gray[100]};
    border-radius: ${theme.borderRadius.sm};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${theme.colors.gray[300]};
    border-radius: ${theme.borderRadius.sm};
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: ${theme.colors.gray[400]};
  }
`;

const MessagesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing[4]};
  max-width: 100%;
`;

const StatusBar = styled.div`
  background: ${props => props.$isConnected ? theme.colors.surface.tertiary : theme.colors.system.red};
  color: ${props => props.$isConnected ? theme.colors.text.secondary : theme.colors.text.inverse};
  padding: ${theme.spacing[3]} ${theme.spacing[4]};
  border-bottom: 1px solid ${theme.colors.border.light};
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: ${theme.typography.fontSize.sm};
  font-family: ${theme.typography.fontFamily.primary};
  font-weight: ${theme.typography.fontWeight.medium};
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
`;

const ConnectionStatus = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing[2]};
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.$connected ? theme.colors.system.green : theme.colors.system.red};
  box-shadow: ${theme.shadows.sm};
`;

const InputContainer = styled.div`
  background: ${theme.colors.surface.primary};
  border-top: 1px solid ${theme.colors.border.light};
  padding: ${theme.spacing[4]};
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: ${theme.spacing[4]};
  border-bottom: 1px solid ${theme.colors.border.light};
`;

const Tab = styled.button`
  background: none;
  border: none;
  padding: ${theme.spacing[3]} ${theme.spacing[6]};
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: ${props => props.$active ? theme.colors.system.blue : theme.colors.text.secondary};
  font-weight: ${props => props.$active ? theme.typography.fontWeight.semibold : theme.typography.fontWeight.normal};
  font-family: ${theme.typography.fontFamily.primary};
  font-size: ${theme.typography.fontSize.sm};
  border-bottom-color: ${props => props.$active ? theme.colors.system.blue : 'transparent'};
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:hover {
    color: ${theme.colors.system.blue};
  }
`;

const InputForm = styled.form`
  display: flex;
  gap: ${theme.spacing[3]};
  align-items: flex-end;
`;

const InputField = styled.textarea`
  flex: 1;
  padding: ${theme.spacing[3]};
  border: 1px solid ${theme.colors.border.light};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  font-family: ${theme.typography.fontFamily.primary};
  resize: none;
  min-height: 50px;
  max-height: 120px;
  transition: border-color ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
    box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
  }
  
  &:disabled {
    background: ${theme.colors.surface.secondary};
    color: ${theme.colors.text.tertiary};
  }
`;

const ExpertSelect = styled.select`
  padding: ${theme.spacing[3]};
  border: 1px solid ${theme.colors.border.light};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  font-family: ${theme.typography.fontFamily.primary};
  margin-right: ${theme.spacing[2]};
  background: ${theme.colors.surface.primary};
  transition: border-color ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
    box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
  }
`;

const SendButton = styled(motion.button)`
  background: ${theme.colors.system.blue};
  color: ${theme.colors.text.inverse};
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing[3]} ${theme.spacing[4]};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${theme.spacing[2]};
  font-weight: ${theme.typography.fontWeight.medium};
  font-family: ${theme.typography.fontFamily.primary};
  font-size: ${theme.typography.fontSize.sm};
  box-shadow: ${theme.shadows.sm};
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:hover {
    background: ${theme.colors.primary[600]};
    box-shadow: ${theme.shadows.md};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const InterventionAlert = styled(motion.div)`
  background: ${theme.colors.system.orange};
  color: ${theme.colors.text.inverse};
  padding: ${theme.spacing[4]};
  text-align: center;
  font-weight: ${theme.typography.fontWeight.semibold};
  font-family: ${theme.typography.fontFamily.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing[2]};
  box-shadow: ${theme.shadows.sm};
`;

const experts = [
  { id: "김창의", name: "🎨 김창의 (디자인)" },
  { id: "박매출", name: "💼 박매출 (영업)" },
  { id: "이현실", name: "⚙️ 이현실 (생산)" },
  { id: "최홍보", name: "📢 최홍보 (마케팅)" },
  { id: "박테크", name: "💻 박테크 (IT)" }
];

function ChatInterface({ 
  messages, 
  status, 
  isConnected, 
  reconnectAttempts, 
  shouldReconnect, 
  onReconnect, 
  onStopReconnecting,
  addMessage 
}) {
  const [activeTab, setActiveTab] = useState('general');
  const [generalInput, setGeneralInput] = useState('');
  const [expertInput, setExpertInput] = useState('');
  const [selectedExpert, setSelectedExpert] = useState('김창의');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      // 더 부드러운 스크롤을 위해 requestAnimationFrame 사용
      requestAnimationFrame(() => {
        messagesEndRef.current?.scrollIntoView({ 
          behavior: "smooth", 
          block: "end",
          inline: "nearest"
        });
      });
    }
  };

  // 메시지가 추가될 때마다 자동 스크롤
  useEffect(() => {
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 100); // 약간의 지연을 두어 DOM 업데이트 완료 후 스크롤

    return () => clearTimeout(timer);
  }, [messages]);

  // 사용자 메시지를 즉시 채팅창에 추가하는 함수
  const addUserMessage = (content, messageType = 'user') => {
    const userMessage = {
      id: `user-${Date.now()}-${Math.random()}`,
      sender: '사용자',
      content: content,
      timestamp: new Date().toISOString(),
      message_type: messageType
    };
    
    if (addMessage) {
      addMessage(userMessage);
    }
    
    return userMessage;
  };

  const handleGeneralSubmit = async (e) => {
    e.preventDefault();
    if (!generalInput.trim() || isLoading) return;

    console.log('=== 일반 메시지 전송 시작 ===');
    console.log('메시지 내용:', generalInput.trim());
    
    const messageContent = generalInput.trim();
    
    // 사용자 메시지를 즉시 채팅창에 추가
    addUserMessage(messageContent);
    
    // 입력창 즉시 클리어
    setGeneralInput('');
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/send_message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: messageContent }),
      });

      console.log('API 응답 상태:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('API 응답 데이터:', data);
        // 입력창은 이미 클리어했으므로 추가 처리 없음
      } else {
        const errorData = await response.json();
        console.error('API 오류:', errorData);
        toast.error('메시지 전송에 실패했습니다.');
      }
    } catch (error) {
      console.error('메시지 전송 중 오류:', error);
      toast.error('메시지 전송 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExpertSubmit = async (e) => {
    e.preventDefault();
    if (!expertInput.trim() || isLoading) return;

    console.log('=== 전문가 질문 전송 시작 ===');
    console.log('선택된 전문가:', selectedExpert);
    console.log('질문 내용:', expertInput.trim());
    
    const questionContent = expertInput.trim();
    const expertName = experts.find(e => e.id === selectedExpert)?.name || selectedExpert;
    
    // 사용자 질문을 즉시 채팅창에 추가
    addUserMessage(`${expertName}에게 질문: ${questionContent}`, 'expert_question');
    
    // 입력창 즉시 클리어
    setExpertInput('');
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/ask_expert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          expert: selectedExpert, 
          question: questionContent 
        }),
      });

      console.log('API 응답 상태:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('API 응답 데이터:', data);
        // 입력창은 이미 클리어했으므로 추가 처리 없음
      } else {
        const errorData = await response.json();
        console.error('API 오류:', errorData);
        toast.error('질문 전송에 실패했습니다.');
      }
    } catch (error) {
      console.error('전문가 질문 전송 중 오류:', error);
      toast.error('질문 전송 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e, submitFunction) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitFunction(e);
    }
  };

  return (
    <ChatContainer>
      <StatusBar $isConnected={isConnected}>
        <ConnectionStatus>
          <StatusDot $connected={isConnected} />
          <span>
            {isConnected 
              ? '연결됨' 
              : reconnectAttempts > 0 && shouldReconnect
                ? `재연결 중... (${reconnectAttempts}/3)` 
                : reconnectAttempts > 0 && !shouldReconnect
                  ? '재연결 중단됨'
                  : '연결 끊김'
            }
          </span>
          {!isConnected && (
            <div style={{ marginLeft: '8px', display: 'flex', gap: '4px' }}>
              {onReconnect && (!shouldReconnect || reconnectAttempts === 0) && (
                <button 
                  onClick={onReconnect}
                  style={{
                    padding: '4px 8px',
                    background: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                borderRadius: '4px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              재연결
            </button>
              )}
              {onStopReconnecting && shouldReconnect && reconnectAttempts > 0 && (
                <button 
                  onClick={onStopReconnecting}
                  style={{
                    padding: '4px 8px',
                    background: 'rgba(255,255,255,0.1)',
                    border: '1px solid rgba(255,255,255,0.3)',
                    borderRadius: '4px',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  중지
                </button>
              )}
            </div>
          )}
        </ConnectionStatus>
        <div>
          총 메시지: {status.totalMessages} | 라운드: {status.discussionRounds}
        </div>
      </StatusBar>

      <AnimatePresence>
        {status.userInterventionPending && (
          <InterventionAlert
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            ✋ 사용자 발언을 기다리고 있습니다!
          </InterventionAlert>
        )}
      </AnimatePresence>

      <MessagesContainer>
        <MessagesList>
          {messages.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: '#6c757d', 
              padding: '2rem',
              fontStyle: 'italic' 
            }}>
              아직 메시지가 없습니다. 토론을 시작해보세요!
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage 
                key={`${message.id || index}`} 
                message={message} 
              />
            ))
          )}
          
          {status.currentSpeaker?.isTyping && (
            <TypingIndicator speaker={status.currentSpeaker.name} />
          )}
          
          <div ref={messagesEndRef} />
        </MessagesList>
      </MessagesContainer>

      <InputContainer>
        <TabContainer>
          <Tab 
            $active={activeTab === 'general'}
            onClick={() => setActiveTab('general')}
          >
            💬 일반 대화
          </Tab>
          <Tab 
            $active={activeTab === 'expert'}
            onClick={() => setActiveTab('expert')}
          >
            🎯 전문가 질문
          </Tab>
        </TabContainer>

        {activeTab === 'general' ? (
          <InputForm onSubmit={handleGeneralSubmit}>
            <InputField
              value={generalInput}
              onChange={(e) => setGeneralInput(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, handleGeneralSubmit)}
              placeholder={
                status.userInterventionPending 
                  ? "의견을 말씀해주세요..." 
                  : "메시지를 입력하세요..."
              }
              disabled={isLoading}
            />
            <SendButton
              type="submit"
              disabled={!generalInput.trim() || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Send size={18} />
              전송
            </SendButton>
          </InputForm>
        ) : (
          <InputForm onSubmit={handleExpertSubmit}>
            <ExpertSelect
              value={selectedExpert}
              onChange={(e) => setSelectedExpert(e.target.value)}
            >
              {experts.map(expert => (
                <option key={expert.id} value={expert.id}>
                  {expert.name}
                </option>
              ))}
            </ExpertSelect>
            <InputField
              value={expertInput}
              onChange={(e) => setExpertInput(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, handleExpertSubmit)}
              placeholder={`${experts.find(e => e.id === selectedExpert)?.name}에게 질문하세요...`}
              disabled={isLoading}
            />
            <SendButton
              type="submit"
              disabled={!expertInput.trim() || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Send size={18} />
              질문
            </SendButton>
          </InputForm>
        )}
      </InputContainer>
    </ChatContainer>
  );
}

export default ChatInterface;