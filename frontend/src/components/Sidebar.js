import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Hand, 
  BarChart3, 
  Save, 
  Settings,
  Users,
  MessageSquare,
  Clock,
  Database,
  Brain,
  Hash,
  ChevronRight,
  Square,
  UserCog
} from 'lucide-react';
import toast from 'react-hot-toast';
import { theme } from '../styles/theme';

const SidebarContainer = styled.div`
  width: 320px;
  background: ${theme.colors.surface.primary};
  border-radius: ${theme.borderRadius.lg} 0 0 ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.xl};
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: ${theme.spacing[6]} 0 ${theme.spacing[6]} ${theme.spacing[6]};
  border: 1px solid ${theme.colors.border.light};
  backdrop-filter: blur(20px);
`;

const SidebarHeader = styled.div`
  background: ${theme.colors.surface.primary};
  color: ${theme.colors.text.primary};
  padding: ${theme.spacing[6]};
  text-align: center;
  border-bottom: 1px solid ${theme.colors.border.light};
`;

const SidebarTitle = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  margin-bottom: ${theme.spacing[3]};
  font-family: ${theme.typography.fontFamily.primary};
  letter-spacing: -0.01em;
`;

const StatusBadge = styled.div`
  background: ${theme.colors.system.blue};
  color: ${theme.colors.text.inverse};
  padding: ${theme.spacing[2]} ${theme.spacing[4]};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  display: inline-block;
  box-shadow: ${theme.shadows.sm};
`;

const SidebarContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${theme.spacing[4]};
`;

const Section = styled.div`
  margin-bottom: ${theme.spacing[8]};
`;

const NavigationSection = styled.div`
  margin-bottom: ${theme.spacing[6]};
  border-bottom: 1px solid ${theme.colors.border.light};
  padding-bottom: ${theme.spacing[4]};
`;

const NavButton = styled(motion.button)`
  width: 100%;
  background: ${props => props.$active ? theme.colors.system.blue : 'transparent'};
  color: ${props => props.$active ? theme.colors.text.inverse : theme.colors.text.primary};
  border: 1px solid ${props => props.$active ? theme.colors.system.blue : theme.colors.border.light};
  padding: ${theme.spacing[3]};
  margin-bottom: ${theme.spacing[2]};
  border-radius: ${theme.borderRadius.md};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${theme.spacing[2]};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:hover {
    background: ${props => props.$active ? theme.colors.primary[600] : theme.colors.surface.secondary};
    border-color: ${theme.colors.system.blue};
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h3`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text.primary};
  margin-bottom: ${theme.spacing[4]};
  display: flex;
  align-items: center;
  gap: ${theme.spacing[2]};
  font-family: ${theme.typography.fontFamily.primary};
`;

const ControlButton = styled(motion.button)`
  width: 100%;
  background: ${props => props.primary ? theme.colors.system.blue : theme.colors.surface.secondary};
  color: ${props => props.primary ? theme.colors.text.inverse : theme.colors.text.primary};
  border: 1px solid ${props => props.primary ? 'transparent' : theme.colors.border.light};
  padding: ${theme.spacing[3]} ${theme.spacing[4]};
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.medium};
  font-family: ${theme.typography.fontFamily.primary};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  margin-bottom: ${theme.spacing[2]};
  display: flex;
  align-items: center;
  gap: ${theme.spacing[2]};
  justify-content: center;
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  box-shadow: ${theme.shadows.sm};
  
  &:hover {
    background: ${props => props.primary ? theme.colors.primary[600] : theme.colors.gray[100]};
    border-color: ${props => props.primary ? 'transparent' : theme.colors.border.medium};
    box-shadow: ${theme.shadows.md};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing[2]};
  margin-bottom: ${theme.spacing[2]};
`;

const StatsCard = styled.div`
  background: ${theme.colors.surface.secondary};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing[4]};
  margin-bottom: ${theme.spacing[2]};
  border: 1px solid ${theme.colors.border.light};
  box-shadow: ${theme.shadows.sm};
`;

const StatRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing[2]};
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const StatLabel = styled.span`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.typography.fontSize.sm};
  font-family: ${theme.typography.fontFamily.primary};
`;

const StatValue = styled.span`
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text.primary};
  font-family: ${theme.typography.fontFamily.primary};
`;

const ExpertList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing[2]};
`;

const ExpertCard = styled.div`
  background: ${theme.colors.surface.secondary};
  border-radius: ${theme.borderRadius.base};
  padding: ${theme.spacing[3]};
  border: 1px solid ${theme.colors.border.light};
  font-size: ${theme.typography.fontSize.sm};
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:hover {
    background: ${theme.colors.gray[100]};
    box-shadow: ${theme.shadows.sm};
  }
`;

const ExpertName = styled.div`
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text.primary};
  margin-bottom: ${theme.spacing[1]};
  font-family: ${theme.typography.fontFamily.primary};
`;

const ExpertRole = styled.div`
  color: ${theme.colors.text.secondary};
  font-family: ${theme.typography.fontFamily.primary};
`;

const ChatroomList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing[1]};
  max-height: 200px;
  overflow-y: auto;
`;

const ChatroomItem = styled(motion.button)`
  width: 100%;
  background: ${props => props.$active ? theme.colors.system.blue : theme.colors.surface.secondary};
  color: ${props => props.$active ? theme.colors.text.inverse : theme.colors.text.primary};
  border: 1px solid ${props => props.$active ? theme.colors.system.blue : theme.colors.border.light};
  padding: ${theme.spacing[3]};
  border-radius: ${theme.borderRadius.base};
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: ${theme.spacing[2]};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  text-align: left;
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  min-height: 60px;
  
  &:hover {
    background: ${props => props.$active ? theme.colors.primary[600] : theme.colors.gray[100]};
    border-color: ${theme.colors.system.blue};
  }
`;

const ChatroomName = styled.div`
  flex: 1;
  font-weight: ${theme.typography.fontWeight.semibold};
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
  line-height: 1.3;
  max-height: 2.6em;
`;

const ChatroomInfo = styled.div`
  font-size: ${theme.typography.fontSize.xs};
  color: ${props => props.$active ? theme.colors.text.inverse : theme.colors.text.secondary};
  opacity: 0.8;
`;

const EmptyState = styled.div`
  text-align: center;
  color: ${theme.colors.text.secondary};
  font-size: ${theme.typography.fontSize.sm};
  padding: ${theme.spacing[4]};
  font-style: italic;
`;

// 기본 전문가 목록 (토론이 시작되지 않았을 때 사용)
const defaultExperts = [
  { emoji: "🎨", name: "김창의", role: "디자인 전문가" },
  { emoji: "💼", name: "박매출", role: "영업 전문가" },
  { emoji: "⚙️", name: "이현실", role: "생산 전문가" },
  { emoji: "📢", name: "최홍보", role: "마케팅 전문가" },
  { emoji: "💻", name: "박테크", role: "IT 전문가" }
];

function Sidebar({ status, onResetDiscussion, currentView, onViewChange, currentRoomId, onChatroomSwitch, updateStatus, onOpenPersonaEditor }) {
  const [isLoading, setIsLoading] = useState(false);
  const [chatrooms, setChatrooms] = useState([]);
  const [chatroomsLoading, setChatroomsLoading] = useState(true);

  // 채팅방 목록 로드
  useEffect(() => {
    loadChatrooms();
  }, []);

  const loadChatrooms = async () => {
    try {
      setChatroomsLoading(true);
      const response = await fetch('/api/memory/chatrooms');
      if (response.ok) {
        const data = await response.json();
        setChatrooms(data.chatrooms || []);
      }
    } catch (error) {
      console.error('채팅방 목록 로드 실패:', error);
    } finally {
      setChatroomsLoading(false);
    }
  };

  const handleChatroomSwitch = async (roomId) => {
    if (roomId === currentRoomId) return;
    
    try {
      const response = await fetch('/api/switch_chatroom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ room_id: roomId }),
      });

      if (response.ok) {
        const data = await response.json();
        if (onChatroomSwitch) {
          onChatroomSwitch(data);
        }
        const roomName = data.room_info.topic || data.room_info.room_name || data.room_info.name;
        toast.success(`${roomName}로 전환되었습니다.`);
      } else {
        toast.error('채팅방 전환에 실패했습니다.');
      }
    } catch (error) {
      toast.error('채팅방 전환 중 오류가 발생했습니다.');
    }
  };

  const handleAutoDiscussionControl = async (action) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/${action}_auto_discussion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // 즉시 상태 업데이트 (UI 반응성 향상)
        if (updateStatus) {
          if (action === 'start') {
            updateStatus(prev => ({
              ...prev,
              autoDiscussionEnabled: true,
              discussionState: 'auto_discussing'
            }));
            toast.success('자동 토론이 시작되었습니다.');
          } else if (action === 'pause') {
            updateStatus(prev => ({
              ...prev,
              autoDiscussionEnabled: false,
              discussionState: 'paused'
            }));
            toast.success('자동 토론이 일시정지되었습니다.');
          } else if (action === 'resume') {
            updateStatus(prev => ({
              ...prev,
              autoDiscussionEnabled: true,
              discussionState: 'auto_discussing'
            }));
            toast.success('자동 토론이 재개되었습니다.');
          } else if (action === 'stop') {
            updateStatus(prev => ({
              ...prev,
              autoDiscussionEnabled: false,
              discussionState: 'ready',
              userInterventionPending: false
            }));
            toast.success('자동 토론이 중지되었습니다.');
          }
        }
        
        // 0.5초 후 최신 상태 가져오기 (정확성 보장)
        setTimeout(async () => {
          try {
            const statusResponse = await fetch('/api/status');
            if (statusResponse.ok && updateStatus) {
              const statusData = await statusResponse.json();
              updateStatus(prev => ({
                ...prev,
                autoDiscussionEnabled: statusData.auto_discussion_enabled,
                userInterventionPending: statusData.user_intervention_pending,
                discussionState: statusData.discussion_state,
                discussionRounds: statusData.discussion_rounds,
                currentSpeaker: statusData.current_speaker || prev.currentSpeaker,
                totalMessages: statusData.total_messages,
                activeParticipants: statusData.active_participants || prev.activeParticipants
              }));
              console.log('상태 업데이트 완료:', statusData);
            }
          } catch (error) {
            console.error('상태 업데이트 오류:', error);
          }
        }, 500);
      } else {
        toast.error(`${action} 실패`);
      }
    } catch (error) {
      toast.error('요청 처리 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInterventionRequest = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/request_intervention', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // 즉시 상태 업데이트
        if (updateStatus) {
          updateStatus(prev => ({
            ...prev,
            userInterventionPending: true,
            autoDiscussionEnabled: false,
            discussionState: 'user_intervention'
          }));
        }
        toast.success('사용자 개입이 요청되었습니다.');
      } else {
        toast.error('개입 요청 실패');
      }
    } catch (error) {
      toast.error('요청 처리 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetConclusion = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/get_conclusion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast.success('결론이 생성되었습니다.');
      } else {
        toast.error('결론 생성 실패');
      }
    } catch (error) {
      toast.error('요청 처리 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const getAutoDiscussionStatus = () => {
    if (status.userInterventionPending) {
      return "사용자 개입 대기";
    } else if (status.autoDiscussionEnabled) {
      return "자동 토론 중";
    } else if (status.discussionState === 'paused') {
      return "일시정지";
    } else {
      return "대기 중";
    }
  };

  return (
    <SidebarContainer>
      <SidebarHeader>
        <SidebarTitle>토론 제어판</SidebarTitle>
        <StatusBadge>
          {getAutoDiscussionStatus()}
        </StatusBadge>
      </SidebarHeader>
      
      <SidebarContent>
        <NavigationSection>
          <SectionTitle>
            <Settings size={18} />
            화면 전환
          </SectionTitle>
          <NavButton
            $active={currentView === 'chat'}
            onClick={() => onViewChange('chat')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <MessageSquare size={16} />
            채팅 토론
          </NavButton>
          <NavButton
            $active={currentView === 'memory'}
            onClick={() => onViewChange('memory')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Brain size={16} />
            메모리 대시보드
          </NavButton>
          <NavButton
            onClick={onOpenPersonaEditor}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <UserCog size={16} />
            페르소나 편집
          </NavButton>
        </NavigationSection>
        <Section>
          <SectionTitle>
            <Settings size={18} />
            자동 토론 제어
          </SectionTitle>
          
          {!status.autoDiscussionEnabled ? (
            <ControlButton
              primary="true"
              onClick={() => handleAutoDiscussionControl('start')}
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Play size={18} />
              자동 토론 시작
            </ControlButton>
          ) : (
            <>
              <ButtonGroup>
                {[
                  {
                    key: 'pause',
                    onClick: () => handleAutoDiscussionControl('pause'),
                    disabled: isLoading,
                    icon: <Pause size={16} />,
                    text: '일시정지'
                  },
                  {
                    key: 'stop',
                    onClick: () => handleAutoDiscussionControl('stop'),
                    disabled: isLoading,
                    icon: <Square size={16} />,
                    text: '중지'
                  }
                ].map((button) => (
                  <ControlButton
                    key={button.key}
                    onClick={button.onClick}
                    disabled={button.disabled}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {button.icon}
                    {button.text}
                  </ControlButton>
                ))}
              </ButtonGroup>
              
              <ControlButton
                onClick={handleInterventionRequest}
                disabled={isLoading || status.userInterventionPending}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Hand size={18} />
                사용자 개입 요청
              </ControlButton>
            </>
          )}
          
          {status.discussionState === 'paused' && (
            <ControlButton
              primary="true"
              onClick={() => handleAutoDiscussionControl('resume')}
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Play size={18} />
              토론 재개
            </ControlButton>
          )}
        </Section>

        <Section>
          <SectionTitle>
            <BarChart3 size={18} />
            빠른 기능
          </SectionTitle>
          
          <ButtonGroup>
            {[
              {
                key: 'conclusion',
                onClick: handleGetConclusion,
                disabled: isLoading,
                icon: <MessageSquare size={16} />,
                text: '결론'
              },
              {
                key: 'save',
                onClick: () => toast.success('저장 기능은 백엔드에서 자동으로 처리됩니다.'),
                disabled: isLoading,
                icon: <Save size={16} />,
                text: '저장'
              }
            ].map((button) => (
              <ControlButton
                key={button.key}
                onClick={button.onClick}
                disabled={button.disabled}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {button.icon}
                {button.text}
              </ControlButton>
            ))}
          </ButtonGroup>
        </Section>

        <Section>
          <SectionTitle>
            <BarChart3 size={18} />
            토론 현황
          </SectionTitle>
          
          <StatsCard>
            <StatRow>
              <StatLabel>총 메시지</StatLabel>
              <StatValue>{status.totalMessages}</StatValue>
            </StatRow>
            <StatRow>
              <StatLabel>토론 라운드</StatLabel>
              <StatValue>{status.discussionRounds}</StatValue>
            </StatRow>
            <StatRow>
              <StatLabel>현재 상태</StatLabel>
              <StatValue>{getAutoDiscussionStatus()}</StatValue>
            </StatRow>
          </StatsCard>
        </Section>

        <Section>
          <SectionTitle>
            <Hash size={18} />
            채팅방 목록
          </SectionTitle>
          
          {chatroomsLoading ? (
            <EmptyState>로딩 중...</EmptyState>
          ) : chatrooms.length > 0 ? (
            <ChatroomList>
              {chatrooms.map((room) => (
                <ChatroomItem
                  key={room.id}
                  $active={room.id === currentRoomId}
                  onClick={() => handleChatroomSwitch(room.id)}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <Hash size={14} style={{ marginTop: '2px', flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <ChatroomName>
                      {room.topic || room.room_name || room.name}
                    </ChatroomName>
                    <ChatroomInfo $active={room.id === currentRoomId}>
                      {new Date(room.created_at).toLocaleDateString()} • {room.message_count || 0}개 메시지
                    </ChatroomInfo>
                  </div>
                  {room.id === currentRoomId && <ChevronRight size={14} />}
                </ChatroomItem>
              ))}
            </ChatroomList>
          ) : (
            <EmptyState>채팅방이 없습니다</EmptyState>
          )}
        </Section>

        <Section>
          <SectionTitle>
            <Users size={18} />
            참석자
          </SectionTitle>
          
          <ExpertList>
            {(status.activeParticipants && status.activeParticipants.length > 0 
              ? status.activeParticipants 
              : defaultExperts
            ).map((expert, index) => (
              <ExpertCard key={`${expert.name}-${index}`}>
                <ExpertName>
                  {expert.emoji} {expert.name}
                </ExpertName>
                <ExpertRole>{expert.role}</ExpertRole>
              </ExpertCard>
            ))}
          </ExpertList>
        </Section>

        <Section>
          <ControlButton
            onClick={onResetDiscussion}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <RotateCcw size={18} />
            새 토론 시작
          </ControlButton>
        </Section>
      </SidebarContent>
    </SidebarContainer>
  );
}

export default Sidebar;