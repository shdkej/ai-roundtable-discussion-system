import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { theme } from '../styles/theme';

const SetupContainer = styled.div`
  flex: 1;
  padding: 2rem;
  display: flex;
  gap: 2rem;
  min-height: 0;
  overflow: hidden;
  
  @media (max-width: 1024px) {
    flex-direction: column;
    overflow-y: auto;
    gap: 1.5rem;
  }
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const LeftPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  
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
  
  @media (max-width: 1024px) {
    overflow: visible;
  }
`;

const RightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  
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
  
  @media (max-width: 1024px) {
    overflow: visible;
  }
`;

const Section = styled(motion.div)`
  background: ${theme.colors.surface.secondary};
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid ${theme.colors.border.light};
  height: fit-content;
`;

const SectionTitle = styled.h3`
  color: ${theme.colors.text.primary};
  margin-bottom: 1rem;
  font-size: 1.2rem;
`;

const TopicOptions = styled.div`
  display: grid;
  gap: 0.5rem;
`;

const TopicButton = styled.button`
  background: ${props => props.selected ? theme.colors.system.blue : theme.colors.surface.primary};
  color: ${props => props.selected ? theme.colors.text.inverse : theme.colors.text.primary};
  border: 2px solid ${props => props.selected ? 'transparent' : theme.colors.border.light};
  padding: 1rem;
  border-radius: 10px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: ${theme.colors.system.blue};
  }
`;

const CustomTopicInput = styled.textarea`
  width: 100%;
  padding: 1rem;
  border: 2px solid ${theme.colors.border.light};
  border-radius: 10px;
  font-size: 1rem;
  resize: vertical;
  min-height: 100px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
  }
`;

const ParticipantGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
`;

const ParticipantCard = styled.div`
  background: ${theme.colors.surface.primary};
  border: 2px solid ${props => props.selected ? theme.colors.system.blue : theme.colors.border.light};
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: ${theme.colors.system.blue};
  }
`;

const ParticipantInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
`;

const ParticipantName = styled.div`
  font-weight: bold;
  color: ${theme.colors.text.primary};
`;

const ParticipantRole = styled.div`
  color: ${theme.colors.text.secondary};
  font-size: 0.9rem;
`;

const CompanyInfoGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-weight: 500;
  color: ${theme.colors.text.primary};
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 2px solid ${theme.colors.border.light};
  border-radius: 8px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
  }
`;

const TextArea = styled.textarea`
  padding: 0.75rem;
  border: 2px solid ${theme.colors.border.light};
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  min-height: 80px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
  }
`;

const StartButtonContainer = styled.div`
  margin-top: auto;
  padding-top: 1rem;
`;

const StartButton = styled(motion.button)`
  background: ${theme.colors.system.blue};
  color: ${theme.colors.text.inverse};
  border: none;
  padding: 1rem 2rem;
  border-radius: 15px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  width: 100%;
  box-shadow: ${theme.shadows.md};
  
  &:hover {
    background: ${theme.colors.primary[600]};
  }
`;

const defaultTopics = [
  "새로운 프리미엄 제품 라인 출시 전략",
  "고객 불만 대응을 위한 품질 개선 방안",
  "비용 절감을 위한 생산 프로세스 혁신",
  "ESG 경영을 위한 친환경 제품 개발",
  "디지털 전환을 통한 업무 효율성 향상"
];

const experts = [
  { id: "디자인팀 김창의", name: "김창의", dept: "디자인팀", emoji: "🎨", description: "UI/UX 전문가" },
  { id: "영업팀 박매출", name: "박매출", dept: "영업팀", emoji: "💼", description: "영업 전문가" },
  { id: "생산팀 이현실", name: "이현실", dept: "생산팀", emoji: "⚙️", description: "생산 전문가" },
  { id: "마케팅팀 최홍보", name: "최홍보", dept: "마케팅팀", emoji: "📢", description: "마케팅 전문가" },
  { id: "IT팀 박테크", name: "박테크", dept: "IT팀", emoji: "💻", description: "IT 전문가" }
];

function DiscussionSetup({ onStartDiscussion }) {
  const [selectedTopic, setSelectedTopic] = useState(defaultTopics[0]);
  const [customTopic, setCustomTopic] = useState('');
  const [useCustomTopic, setUseCustomTopic] = useState(false);
  const [selectedParticipants, setSelectedParticipants] = useState([
    "디자인팀 김창의", "영업팀 박매출", "생산팀 이현실"
  ]);
  const [companyInfo, setCompanyInfo] = useState({
    company_size: "중견 제조업체",
    industry: "아웃도어 의류",
    revenue: "800억원",
    current_challenge: ""
  });

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
    setUseCustomTopic(false);
  };

  const handleCustomTopicToggle = () => {
    setUseCustomTopic(true);
    setSelectedTopic('');
  };

  const handleParticipantToggle = (participantId) => {
    setSelectedParticipants(prev => 
      prev.includes(participantId)
        ? prev.filter(id => id !== participantId)
        : [...prev, participantId]
    );
  };

  const handleCompanyInfoChange = (field, value) => {
    setCompanyInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleStartDiscussion = () => {
    const topic = useCustomTopic ? customTopic : selectedTopic;
    
    if (!topic.trim()) {
      toast.error('토론 주제를 선택하거나 입력해주세요.');
      return;
    }
    
    if (selectedParticipants.length < 2) {
      toast.error('최소 2명 이상의 전문가를 선택해주세요.');
      return;
    }
    
    // 참석자 ID를 이름으로 변환
    const participantNames = selectedParticipants.map(participantId => {
      const expert = experts.find(e => e.id === participantId);
      return expert ? expert.name : participantId;
    });
    
    onStartDiscussion({
      topic: topic.trim(),
      participants: participantNames,
      company_info: companyInfo
    });
  };

  return (
    <SetupContainer>
      <LeftPanel>
        <Section
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <SectionTitle>📋 토론 주제</SectionTitle>
          <TopicOptions>
            {defaultTopics.map((topic, index) => (
              <TopicButton
                key={index}
                selected={selectedTopic === topic && !useCustomTopic}
                onClick={() => handleTopicSelect(topic)}
              >
                {topic}
              </TopicButton>
            ))}
            <TopicButton
              selected={useCustomTopic}
              onClick={handleCustomTopicToggle}
            >
              📝 직접 입력
            </TopicButton>
            {useCustomTopic && (
              <CustomTopicInput
                placeholder="토론하고 싶은 주제를 입력하세요..."
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
              />
            )}
          </TopicOptions>
        </Section>

        <Section
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <SectionTitle>👥 참석자 선택</SectionTitle>
          <ParticipantGrid>
            {experts.map((expert) => (
              <ParticipantCard
                key={expert.id}
                selected={selectedParticipants.includes(expert.id)}
                onClick={() => handleParticipantToggle(expert.id)}
              >
                <ParticipantInfo>
                  <span>{expert.emoji}</span>
                  <ParticipantName>{expert.name}</ParticipantName>
                </ParticipantInfo>
                <ParticipantRole>{expert.description}</ParticipantRole>
              </ParticipantCard>
            ))}
          </ParticipantGrid>
        </Section>
      </LeftPanel>

      <RightPanel>
        <Section
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <SectionTitle>🏢 회사 정보</SectionTitle>
          <CompanyInfoGrid>
            <InputGroup>
              <Label>회사 규모</Label>
              <Input
                value={companyInfo.company_size}
                onChange={(e) => handleCompanyInfoChange('company_size', e.target.value)}
              />
            </InputGroup>
            <InputGroup>
              <Label>사업 분야</Label>
              <Input
                value={companyInfo.industry}
                onChange={(e) => handleCompanyInfoChange('industry', e.target.value)}
              />
            </InputGroup>
            <InputGroup>
              <Label>연 매출</Label>
              <Input
                value={companyInfo.revenue}
                onChange={(e) => handleCompanyInfoChange('revenue', e.target.value)}
              />
            </InputGroup>
            <InputGroup style={{ gridColumn: '1 / -1' }}>
              <Label>주요 과제</Label>
              <TextArea
                placeholder="해결하고 싶은 문제를 간단히 설명해주세요..."
                value={companyInfo.current_challenge}
                onChange={(e) => handleCompanyInfoChange('current_challenge', e.target.value)}
              />
            </InputGroup>
          </CompanyInfoGrid>
        </Section>

        <StartButtonContainer>
          <StartButton
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleStartDiscussion}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            🚀 채팅 토론 시작
          </StartButton>
        </StartButtonContainer>
      </RightPanel>
    </SetupContainer>
  );
}

export default DiscussionSetup;