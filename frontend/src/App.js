import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Toaster } from 'react-hot-toast';
import DiscussionSetup from './components/DiscussionSetup';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import MemoryDashboard from './components/MemoryDashboard';
import PersonaEditor from './components/PersonaEditor';
import { useWebSocket } from './hooks/useWebSocket';
import { useDiscussion } from './hooks/useDiscussion';
import { theme } from './styles/theme';

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background: ${theme.colors.gray[50]};
  font-family: ${theme.typography.fontFamily.primary};
  box-sizing: border-box;
  gap: 0;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: ${theme.colors.surface.primary};
  border-radius: ${props => props.$hasSidebar ? `0 ${theme.borderRadius.lg} ${theme.borderRadius.lg} 0` : theme.borderRadius.lg};
  box-shadow: ${theme.shadows.lg};
  overflow: hidden;
  min-height: 0;
  margin: ${theme.spacing[6]};
  border: 1px solid ${theme.colors.border.light};
`;

const Header = styled.div`
  background: ${theme.colors.surface.primary};
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing[8]} ${theme.spacing[6]};
  text-align: center;
  border-bottom: 1px solid ${theme.colors.border.light};
  backdrop-filter: blur(20px);
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['4xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  margin-bottom: ${theme.spacing[2]};
  color: ${theme.colors.text.primary};
  line-height: ${theme.typography.lineHeight.tight};
  letter-spacing: -0.02em;
`;

const Subtitle = styled.p`
  font-size: ${theme.typography.fontSize.lg};
  color: ${theme.colors.text.secondary};
  font-weight: ${theme.typography.fontWeight.normal};
  line-height: ${theme.typography.lineHeight.relaxed};
  margin: 0;
`;

function App() {
  const [discussionStarted, setDiscussionStarted] = useState(false);
  const [currentView, setCurrentView] = useState('setup'); // setup, chat, memory
  const [currentRoomId, setCurrentRoomId] = useState(null);
  const [isPersonaEditorOpen, setIsPersonaEditorOpen] = useState(false);
  const { 
    messages, 
    addMessage, 
    clearMessages,
    status,
    updateStatus 
  } = useDiscussion();
  
  const { 
    isConnected, 
    reconnectAttempts,
    shouldReconnect,
    manualReconnect,
    stopReconnecting,
  } = useWebSocket('ws://localhost:8101/ws', {
    onMessage: (data) => {
      if (data.type === 'message') {
        addMessage(data.data);
      } else if (data.type === 'discussion_started') {
        // 이미 discussionStarted가 true이므로 상태 변경 없이 메시지만 추가
        if (data.data.messages) {
          data.data.messages.forEach(msg => addMessage(msg));
        }
      } else if (data.type === 'typing_start') {
        updateStatus(prev => ({
          ...prev,
          currentSpeaker: {
            name: data.data.speaker,
            isTyping: true
          }
        }));
      } else if (data.type === 'typing_stop') {
        updateStatus(prev => ({
          ...prev,
          currentSpeaker: {
            ...prev.currentSpeaker,
            isTyping: false
          }
        }));
      } else if (data.type === 'user_intervention_requested') {
        updateStatus(prev => ({
          ...prev,
          userInterventionPending: true
        }));
      } else if (data.type === 'chatroom_switched') {
        // 채팅방 전환 시 handleChatroomSwitch 호출
        console.log('WebSocket chatroom_switched 이벤트:', data.data);
        handleChatroomSwitch(data.data);
      } else if (data.type === 'persona_updated') {
        // 페르소나 업데이트 알림
        console.log('페르소나 업데이트됨:', data.data);
      } else if (data.type === 'personas_reset') {
        // 페르소나 리셋 알림
        console.log('페르소나 리셋됨:', data.data);
      }
    }
  });

  // 상태 폴링 - 자동토론 상태를 주기적으로 확인
  useEffect(() => {
    if (!discussionStarted) return;
    
    const pollStatus = async () => {
      try {
        const response = await fetch('/api/status');
        if (response.ok) {
          const statusData = await response.json();
          updateStatus(prev => ({
            ...prev,
            autoDiscussionEnabled: statusData.auto_discussion_enabled,
            userInterventionPending: statusData.user_intervention_pending,
            discussionState: statusData.discussion_state,
            discussionRounds: statusData.discussion_rounds,
            currentSpeaker: statusData.current_speaker || prev.currentSpeaker,
            totalMessages: statusData.total_messages
          }));
        }
      } catch (error) {
        console.error('상태 폴링 오류:', error);
      }
    };

    // 즉시 한 번 실행
    pollStatus();
    
    // 3초마다 상태 폴링
    const interval = setInterval(pollStatus, 3000);
    
    return () => clearInterval(interval);
  }, [discussionStarted, updateStatus]);

  const handleStartDiscussion = async (config) => {
    try {
      // 즉시 채팅 화면으로 전환하고 자동토론 상태로 설정
      setDiscussionStarted(true);
      setCurrentView('chat');
      
      // 즉시 자동토론 상태로 UI 업데이트
      updateStatus(prev => ({
        ...prev,
        autoDiscussionEnabled: true,
        discussionState: 'auto_discussing'
      }));
      
      const response = await fetch('/api/start_discussion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('API response:', data);
        
        // WebSocket을 통해 메시지가 올 때까지 기다리지 않고 바로 처리
        if (data.success && data.messages) {
          data.messages.forEach(msg => addMessage(msg));
          // 새 토론 시작시 room_id 설정
          if (data.room_id) {
            setCurrentRoomId(data.room_id);
          }
        }
        
        // 자동 토론 시작 API 호출
        try {
          const autoResponse = await fetch('/api/start_auto_discussion', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          
          if (autoResponse.ok) {
            console.log('자동 토론이 시작되었습니다.');
            // 이미 위에서 상태가 업데이트되었으므로 추가 상태 확인만 수행
            setTimeout(async () => {
              try {
                const statusResponse = await fetch('/api/status');
                if (statusResponse.ok) {
                  const statusData = await statusResponse.json();
                  updateStatus(prev => ({
                    ...prev,
                    autoDiscussionEnabled: statusData.auto_discussion_enabled,
                    userInterventionPending: statusData.user_intervention_pending,
                    discussionState: statusData.discussion_state,
                    discussionRounds: statusData.discussion_rounds,
                    currentSpeaker: statusData.current_speaker || prev.currentSpeaker,
                    totalMessages: statusData.total_messages
                  }));
                }
              } catch (error) {
                console.error('상태 업데이트 오류:', error);
              }
            }, 500); // 0.5초 후 상태 재확인
          }
        } catch (autoError) {
          console.error('자동 토론 시작 실패:', autoError);
        }
      } else {
        // API 실패 시에도 테스트 메시지로 진행
        const testMessage = {
          id: `test_${Date.now()}`,
          sender: "시스템",
          content: "🚀 토론이 시작되었습니다!\n주제: " + config.topic + "\n참석자: " + config.participants.length + "명",
          timestamp: new Date().toISOString(),
          message_type: "system"
        };
        addMessage(testMessage);
      }
    } catch (error) {
      console.error('Failed to start discussion:', error);
      
      // 오류 시에도 채팅 화면 유지하고 테스트 메시지 추가
      const testMessage = {
        id: `test_${Date.now()}`,
        sender: "시스템",
        content: "🚀 토론이 시작되었습니다!\n주제: " + config.topic + "\n참석자: " + config.participants.length + "명",
        timestamp: new Date().toISOString(),
        message_type: "system"
      };
      addMessage(testMessage);
    }
  };

  const handleChatroomSwitch = (data) => {
    console.log('Switching to chatroom:', data);
    
    // 메시지 초기화
    clearMessages();
    
    // 현재 채팅방 ID 설정
    setCurrentRoomId(data.room_id);
    
    // 대화 기록이 있다면 파싱해서 메시지로 추가
    if (data.conversation_content) {
      console.log('대화 기록 파싱 중...');
      try {
        // 마크다운 형식에서 메시지 추출
        const lines = data.conversation_content.split('\n');
        const messages = [];
        
        for (const line of lines) {
          // **[시간] 발신자**: 내용 형태의 라인 매칭
          const messageMatch = line.match(/^\*\*\[(\d{2}:\d{2}:\d{2})\]\s*(.+?)\*\*:\s*(.+)$/);
          if (messageMatch) {
            const [, timeStr, sender, content] = messageMatch;
            
            // 시스템 메시지 처리 (📢, 🎯 등 제거)
            const cleanSender = sender.replace(/^[📢🎯]\s*/, '').trim();
            
            // 오늘 날짜로 타임스탬프 생성
            const today = new Date();
            const [hours, minutes, seconds] = timeStr.split(':');
            const timestamp = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 
                                       parseInt(hours), parseInt(minutes), parseInt(seconds));
            
            const messageType = cleanSender === '시스템' ? 'system' : 'message';
            
            const message = {
              id: `loaded_${messages.length}_${Date.now()}`,
              sender: cleanSender,
              content: content.trim(),
              timestamp: timestamp.toISOString(),
              message_type: messageType
            };
            
            messages.push(message);
          }
        }
        
        // 파싱된 메시지들을 순서대로 추가
        console.log(`${messages.length}개 메시지 로드됨`);
        messages.forEach(message => addMessage(message));
        
      } catch (error) {
        console.error('대화 기록 파싱 오류:', error);
      }
    }
    
    // 상태 초기화 (새 채팅방으로 전환시)
    updateStatus(prev => ({
      ...prev,
      autoDiscussionEnabled: false,
      userInterventionPending: false,
      discussionState: 'ready',
      currentSpeaker: { name: '', isTyping: false }
    }));
  };

  const handleResetDiscussion = () => {
    setDiscussionStarted(false);
    setCurrentView('setup');
    setCurrentRoomId(null);
    clearMessages();
    updateStatus({
      autoDiscussionEnabled: false,
      userInterventionPending: false,
      discussionState: 'ready',
      discussionRounds: 0,
      currentSpeaker: { name: '', isTyping: false },
      totalMessages: 0
    });
  };

  const handlePersonaUpdate = (agentName, persona) => {
    console.log(`페르소나 업데이트됨: ${agentName}`, persona);
    // 필요시 추가 로직 구현
  };

  return (
    <AppContainer>
      <Toaster position="top-right" />
      
      {discussionStarted && (
        <Sidebar 
          status={status}
          onResetDiscussion={handleResetDiscussion}
          currentView={currentView}
          onViewChange={setCurrentView}
          currentRoomId={currentRoomId}
          onChatroomSwitch={handleChatroomSwitch}
          updateStatus={updateStatus}
          onOpenPersonaEditor={() => setIsPersonaEditorOpen(true)}
        />
      )}
      
      <MainContent $hasSidebar={discussionStarted}>
        <Header>
          <Title>💬 KS 채팅형 원탁토론</Title>
          <Subtitle>실시간 채팅으로 전문가들과 토론하세요</Subtitle>
        </Header>
        
        {!discussionStarted ? (
          <DiscussionSetup onStartDiscussion={handleStartDiscussion} />
        ) : currentView === 'chat' ? (
          <ChatInterface 
            messages={messages}
            status={status}
            isConnected={isConnected}
            reconnectAttempts={reconnectAttempts}
            shouldReconnect={shouldReconnect}
            onReconnect={manualReconnect}
            onStopReconnecting={stopReconnecting}
            addMessage={addMessage}
          />
        ) : currentView === 'memory' ? (
          <MemoryDashboard />
        ) : null}
      </MainContent>

      <PersonaEditor
        isOpen={isPersonaEditorOpen}
        onClose={() => setIsPersonaEditorOpen(false)}
        onUpdate={handlePersonaUpdate}
      />
    </AppContainer>
  );
}

export default App;