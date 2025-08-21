import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { theme } from '../styles/theme';

const MessageContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
`;

const UserMessageContainer = styled(MessageContainer)`
  align-items: flex-end;
`;

const AssistantMessageContainer = styled(MessageContainer)`
  align-items: flex-start;
`;

const SystemMessageContainer = styled(MessageContainer)`
  align-items: center;
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 1rem 1.25rem;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
  line-height: 1.4;
`;

const UserBubble = styled(MessageBubble)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 6px;
  margin-left: 20%;
`;

const AssistantBubble = styled(MessageBubble)`
  background: white;
  border: 1px solid #e1e5e9;
  border-bottom-left-radius: 6px;
  margin-right: 20%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
`;

const SystemBubble = styled(MessageBubble)`
  background: linear-gradient(135deg, #42a5f5 0%, #1e88e5 100%);
  color: white;
  border-radius: 12px;
  max-width: 90%;
  text-align: center;
  font-weight: 500;
`;

const ConclusionBubble = styled(MessageBubble)`
  background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
  color: white;
  border-radius: 12px;
  margin-right: 20%;
  box-shadow: 0 2px 8px rgba(67, 160, 71, 0.3);
`;

const ResponseBubble = styled(MessageBubble)`
  background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
  color: white;
  border-radius: 12px;
  margin-right: 20%;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
`;

const SenderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
`;

const SenderName = styled.span`
  font-weight: bold;
  color: ${props => props.color || '#343a40'};
`;

const SenderAvatar = styled.span`
  font-size: 1.2rem;
`;

const Timestamp = styled.div`
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.25rem;
  opacity: 0.7;
`;

const MessageContent = styled.div`
  white-space: pre-wrap;
`;

const getAvatarAndColor = (sender) => {
  const avatarMap = {
    "사용자": { avatar: "👤", color: "#667eea" },
    "시스템": { avatar: "🔔", color: "#42a5f5" },
    "토론 진행자": { avatar: "🎭", color: "#ff9800" },
    "디자인팀 팀장 김창의": { avatar: "🎨", color: "#e91e63" },
    "영업팀 팀장 박매출": { avatar: "💼", color: "#9c27b0" },
    "생산팀 팀장 이현실": { avatar: "⚙️", color: "#795548" },
    "마케팅팀 팀장 최홍보": { avatar: "📢", color: "#ff5722" },
    "IT팀 팀장 박테크": { avatar: "💻", color: "#00bcd4" }
  };
  
  return avatarMap[sender] || { avatar: "🤖", color: "#6c757d" };
};

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('ko-KR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

function ChatMessage({ message }) {
  if (!message) {
    return <div style={{color: 'red'}}>Message is undefined</div>;
  }
  
  const { sender, content, timestamp, message_type } = message;
  const { avatar, color } = getAvatarAndColor(sender);

  const messageVariants = {
    initial: { opacity: 0, y: 20, scale: 0.95 },
    animate: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        duration: parseInt(theme.animation.duration.normal) / 1000,
        ease: theme.animation.framerEasing.out
      }
    }
  };

  if (message_type === "system") {
    return (
      <SystemMessageContainer
        variants={messageVariants}
        initial="initial"
        animate="animate"
      >
        <SystemBubble>
          <SenderInfo style={{ justifyContent: 'center', marginBottom: '0.25rem' }}>
            <SenderAvatar>{avatar}</SenderAvatar>
            <SenderName>{sender}</SenderName>
          </SenderInfo>
          <MessageContent>{content}</MessageContent>
          <Timestamp style={{ textAlign: 'center', color: 'rgba(255,255,255,0.8)' }}>
            {formatTime(timestamp)}
          </Timestamp>
        </SystemBubble>
      </SystemMessageContainer>
    );
  }

  if (sender === "사용자") {
    return (
      <UserMessageContainer
        variants={messageVariants}
        initial="initial"
        animate="animate"
      >
        <UserBubble>
          <MessageContent>{content}</MessageContent>
          <Timestamp style={{ textAlign: 'right', color: 'rgba(255,255,255,0.8)' }}>
            {formatTime(timestamp)}
          </Timestamp>
        </UserBubble>
      </UserMessageContainer>
    );
  }

  // 전문가 메시지
  let BubbleComponent = AssistantBubble;
  
  if (message_type === "conclusion") {
    BubbleComponent = ConclusionBubble;
  } else if (message_type === "response") {
    BubbleComponent = ResponseBubble;
  }

  return (
    <AssistantMessageContainer
      variants={messageVariants}
      initial="initial"
      animate="animate"
    >
      <SenderInfo>
        <SenderAvatar>{avatar}</SenderAvatar>
        <SenderName color={color}>{sender}</SenderName>
      </SenderInfo>
      <BubbleComponent>
        <MessageContent>{content}</MessageContent>
        <Timestamp style={{ 
          color: message_type === "conclusion" || message_type === "response" 
            ? 'rgba(255,255,255,0.8)' 
            : '#6c757d' 
        }}>
          {formatTime(timestamp)}
        </Timestamp>
      </BubbleComponent>
    </AssistantMessageContainer>
  );
}

export default ChatMessage;