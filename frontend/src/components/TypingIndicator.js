import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import { theme } from '../styles/theme';

const bounce = keyframes`
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
`;

const TypingContainer = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
`;

const TypingBubble = styled.div`
  background: #f1f3f4;
  border: 1px solid #e1e5e9;
  border-radius: 18px;
  border-bottom-left-radius: 6px;
  padding: 1rem 1.25rem;
  max-width: 70%;
  margin-right: 20%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const SpeakerInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
`;

const SpeakerName = styled.span`
  font-weight: bold;
  color: #667eea;
`;

const SpeakerAvatar = styled.span`
  font-size: 1.2rem;
`;

const TypingText = styled.span`
  color: #6c757d;
  font-style: italic;
`;

const DotsContainer = styled.div`
  display: flex;
  gap: 3px;
`;

const Dot = styled.div`
  width: 6px;
  height: 6px;
  background: ${theme.colors.system.blue};
  border-radius: 50%;
  animation: ${bounce} 1.4s ease-in-out infinite both;
  
  &:nth-child(1) {
    animation-delay: -0.32s;
  }
  
  &:nth-child(2) {
    animation-delay: -0.16s;
  }
  
  &:nth-child(3) {
    animation-delay: 0s;
  }
`;

const getAvatarAndColor = (speaker) => {
  const avatarMap = {
    "김창의": "🎨",
    "디자인팀 팀장 김창의": "🎨",
    "박매출": "💼", 
    "영업팀 팀장 박매출": "💼",
    "이현실": "⚙️",
    "생산팀 팀장 이현실": "⚙️", 
    "최홍보": "📢",
    "마케팅팀 팀장 최홍보": "📢",
    "박테크": "💻",
    "IT팀 팀장 박테크": "💻",
    "토론 진행자": "🎭"
  };
  
  return avatarMap[speaker] || "🤖";
};

function TypingIndicator({ speaker }) {
  const avatar = getAvatarAndColor(speaker);
  
  return (
    <TypingContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div>
        <SpeakerInfo>
          <SpeakerAvatar>{avatar}</SpeakerAvatar>
          <SpeakerName>{speaker}</SpeakerName>
        </SpeakerInfo>
        <TypingBubble>
          <TypingText>답변을 준비하고 있습니다</TypingText>
          <DotsContainer>
            <Dot />
            <Dot />
            <Dot />
          </DotsContainer>
        </TypingBubble>
      </div>
    </TypingContainer>
  );
}

export default TypingIndicator;