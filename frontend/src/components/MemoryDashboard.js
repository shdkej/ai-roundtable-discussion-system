import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Database, MessageSquare, Users, Brain, FileText, Eye, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import { theme } from '../styles/theme';

const DashboardContainer = styled.div`
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  overflow-y: auto;
  background: ${theme.colors.gray[50]};
`;

const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1rem;
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text.primary};
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const RefreshButton = styled(motion.button)`
  background: ${theme.colors.system.blue};
  color: ${theme.colors.text.inverse};
  border: none;
  padding: 0.5rem 1rem;
  border-radius: ${theme.borderRadius.md};
  cursor: pointer;
  font-size: ${theme.typography.fontSize.sm};
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid ${theme.colors.border.light};
  margin-bottom: 2rem;
`;

const Tab = styled.button`
  background: none;
  border: none;
  padding: 1rem 1.5rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: ${props => props.$active ? theme.colors.system.blue : theme.colors.text.secondary};
  font-weight: ${props => props.$active ? theme.typography.fontWeight.semibold : theme.typography.fontWeight.normal};
  font-size: ${theme.typography.fontSize.base};
  border-bottom-color: ${props => props.$active ? theme.colors.system.blue : 'transparent'};
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    color: ${theme.colors.system.blue};
  }
`;

const ContentArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled(motion.div)`
  background: ${theme.colors.surface.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: 1.5rem;
  border: 1px solid ${theme.colors.border.light};
  box-shadow: ${theme.shadows.sm};
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: between;
  margin-bottom: 1rem;
`;

const StatTitle = styled.h3`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text.primary};
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const StatValue = styled.div`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.system.blue};
`;

const SearchSection = styled.div`
  background: ${theme.colors.surface.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: 1.5rem;
  border: 1px solid ${theme.colors.border.light};
`;

const SearchForm = styled.form`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 1px solid ${theme.colors.border.light};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
    box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
  }
`;

const SearchTypeSelect = styled.select`
  padding: 0.75rem;
  border: 1px solid ${theme.colors.border.light};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: ${theme.colors.surface.primary};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.system.blue};
  }
`;

const SearchButton = styled(motion.button)`
  background: ${theme.colors.system.blue};
  color: ${theme.colors.text.inverse};
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: ${theme.borderRadius.md};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SearchResults = styled.div`
  max-height: 400px;
  overflow-y: auto;
`;

const ResultItem = styled(motion.div)`
  background: ${theme.colors.surface.secondary};
  border-radius: ${theme.borderRadius.md};
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-left: 4px solid ${theme.colors.system.blue};
`;

const ResultText = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text.primary};
  margin-bottom: 0.5rem;
  line-height: 1.5;
`;

const ResultMeta = styled.div`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.text.secondary};
  display: flex;
  justify-content: between;
  align-items: center;
`;

const ChatroomList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
`;

const ChatroomCard = styled(motion.div)`
  background: ${theme.colors.surface.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: 1.5rem;
  border: 1px solid ${theme.colors.border.light};
  cursor: pointer;
  transition: all ${theme.animation.duration.fast} ${theme.animation.easing.default};
  
  &:hover {
    box-shadow: ${theme.shadows.md};
    border-color: ${theme.colors.system.blue};
  }
`;

const ChatroomTitle = styled.h4`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text.primary};
  margin-bottom: 0.5rem;
`;

const ChatroomMeta = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text.secondary};
  margin-bottom: 1rem;
`;

const ChatroomActions = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ActionButton = styled(motion.button)`
  background: ${props => props.variant === 'primary' ? theme.colors.system.blue : theme.colors.surface.secondary};
  color: ${props => props.variant === 'primary' ? theme.colors.text.inverse : theme.colors.text.primary};
  border: 1px solid ${props => props.variant === 'primary' ? 'transparent' : theme.colors.border.light};
  padding: 0.5rem 1rem;
  border-radius: ${theme.borderRadius.sm};
  cursor: pointer;
  font-size: ${theme.typography.fontSize.sm};
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const Modal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled(motion.div)`
  background: ${theme.colors.surface.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: 2rem;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  margin: 2rem;
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid ${theme.colors.border.light};
  padding-bottom: 1rem;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: ${theme.colors.text.secondary};
  
  &:hover {
    color: ${theme.colors.text.primary};
  }
`;

const ConversationContent = styled.div`
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: ${theme.typography.fontSize.sm};
  line-height: 1.6;
  white-space: pre-wrap;
  color: ${theme.colors.text.primary};
`;

function MemoryDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [chatrooms, setChatrooms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('common');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedChatroom, setSelectedChatroom] = useState(null);
  const [conversationContent, setConversationContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadStats(),
        loadChatrooms()
      ]);
    } catch (error) {
      toast.error('데이터 로딩 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/memory/stats');
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Stats loading error:', error);
    }
  };

  const loadChatrooms = async () => {
    try {
      const response = await fetch('/api/memory/chatrooms');
      const data = await response.json();
      if (data.success) {
        setChatrooms(data.chatrooms);
      }
    } catch (error) {
      console.error('Chatrooms loading error:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await fetch('/api/memory/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          agent_name: searchType === 'common' ? null : searchType,
          top_k: 10
        }),
      });

      const data = await response.json();
      if (data.success) {
        setSearchResults(data.results);
      } else {
        toast.error('검색 중 오류가 발생했습니다.');
      }
    } catch (error) {
      toast.error('검색 중 오류가 발생했습니다.');
    } finally {
      setIsSearching(false);
    }
  };

  const viewConversation = async (roomId) => {
    try {
      const response = await fetch(`/api/memory/chatroom/${roomId}/conversation`);
      const data = await response.json();
      if (data.success) {
        setConversationContent(data.content);
        setSelectedChatroom(roomId);
      } else {
        toast.error('대화 내용을 불러올 수 없습니다.');
      }
    } catch (error) {
      toast.error('대화 내용 로딩 중 오류가 발생했습니다.');
    }
  };

  const downloadConversation = async (roomId) => {
    try {
      const response = await fetch(`/api/memory/chatroom/${roomId}/conversation`);
      const data = await response.json();
      if (data.success) {
        const element = document.createElement('a');
        const file = new Blob([data.content], { type: 'text/markdown' });
        element.href = URL.createObjectURL(file);
        element.download = `conversation_${roomId}.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        toast.success('파일이 다운로드되었습니다.');
      }
    } catch (error) {
      toast.error('다운로드 중 오류가 발생했습니다.');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  if (isLoading) {
    return (
      <DashboardContainer>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <Database size={48} />
          <p>메모리 데이터를 불러오는 중...</p>
        </div>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <Header>
        <Title>
          <Brain size={32} />
          메모리 시스템 대시보드
        </Title>
        <RefreshButton
          onClick={loadData}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Database size={16} />
          새로고침
        </RefreshButton>
      </Header>

      <TabContainer>
        <Tab
          $active={activeTab === 'overview'}
          onClick={() => setActiveTab('overview')}
        >
          <Database size={16} />
          통계 개요
        </Tab>
        <Tab
          $active={activeTab === 'search'}
          onClick={() => setActiveTab('search')}
        >
          <Search size={16} />
          메모리 검색
        </Tab>
        <Tab
          $active={activeTab === 'chatrooms'}
          onClick={() => setActiveTab('chatrooms')}
        >
          <MessageSquare size={16} />
          채팅방 목록
        </Tab>
      </TabContainer>

      <ContentArea>
        {activeTab === 'overview' && (
          <>
            <StatsGrid>
              <StatCard
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <StatHeader>
                  <StatTitle>
                    <Brain size={20} />
                    공통 메모리
                  </StatTitle>
                </StatHeader>
                <StatValue>{stats?.common_memory?.count || 0}</StatValue>
                <div style={{ fontSize: '0.875rem', color: theme.colors.text.secondary }}>
                  저장된 맥락 수
                </div>
              </StatCard>

              <StatCard
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <StatHeader>
                  <StatTitle>
                    <Users size={20} />
                    에이전트 메모리
                  </StatTitle>
                </StatHeader>
                <StatValue>{Object.keys(stats?.agent_memories || {}).length}</StatValue>
                <div style={{ fontSize: '0.875rem', color: theme.colors.text.secondary }}>
                  활성 에이전트 수
                </div>
              </StatCard>

              <StatCard
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <StatHeader>
                  <StatTitle>
                    <MessageSquare size={20} />
                    채팅방
                  </StatTitle>
                </StatHeader>
                <StatValue>{stats?.total_chatrooms || 0}</StatValue>
                <div style={{ fontSize: '0.875rem', color: theme.colors.text.secondary }}>
                  총 대화방 수
                </div>
              </StatCard>

              <StatCard
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
              >
                <StatHeader>
                  <StatTitle>
                    <FileText size={20} />
                    총 메시지
                  </StatTitle>
                </StatHeader>
                <StatValue>
                  {Object.values(stats?.chatroom_memories || {}).reduce((sum, room) => sum + room.count, 0)}
                </StatValue>
                <div style={{ fontSize: '0.875rem', color: theme.colors.text.secondary }}>
                  모든 대화의 메시지 수
                </div>
              </StatCard>
            </StatsGrid>

            {stats?.agent_memories && Object.keys(stats.agent_memories).length > 0 && (
              <StatCard>
                <StatTitle style={{ marginBottom: '1rem' }}>
                  <Users size={20} />
                  에이전트별 메모리 상세
                </StatTitle>
                {Object.entries(stats.agent_memories).map(([agent, data]) => (
                  <div key={agent} style={{ 
                    display: 'flex', 
                    justifyContent: 'between', 
                    padding: '0.5rem 0',
                    borderBottom: '1px solid ' + theme.colors.border.light
                  }}>
                    <span>{agent}</span>
                    <span style={{ fontWeight: 'bold', color: theme.colors.system.blue }}>
                      {data.count} 맥락
                    </span>
                  </div>
                ))}
              </StatCard>
            )}
          </>
        )}

        {activeTab === 'search' && (
          <SearchSection>
            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Search size={20} />
              메모리 검색
            </h3>
            
            <SearchForm onSubmit={handleSearch}>
              <SearchInput
                type="text"
                placeholder="검색할 내용을 입력하세요..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <SearchTypeSelect
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
              >
                <option value="common">공통 맥락</option>
                <option value="김창의">김창의 (디자인)</option>
                <option value="박매출">박매출 (영업)</option>
                <option value="이현실">이현실 (생산)</option>
                <option value="최홍보">최홍보 (마케팅)</option>
                <option value="박테크">박테크 (IT)</option>
              </SearchTypeSelect>
              <SearchButton
                type="submit"
                disabled={isSearching}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Search size={16} />
                {isSearching ? '검색 중...' : '검색'}
              </SearchButton>
            </SearchForm>

            <SearchResults>
              {searchResults.map((result, index) => (
                <ResultItem
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <ResultText>{result.text}</ResultText>
                  <ResultMeta>
                    <span>유사도: {(result.similarity_score * 100).toFixed(1)}%</span>
                    <span>순위: #{result.rank}</span>
                  </ResultMeta>
                </ResultItem>
              ))}
              {searchResults.length === 0 && searchQuery && !isSearching && (
                <div style={{ textAlign: 'center', padding: '2rem', color: theme.colors.text.secondary }}>
                  검색 결과가 없습니다.
                </div>
              )}
            </SearchResults>
          </SearchSection>
        )}

        {activeTab === 'chatrooms' && (
          <ChatroomList>
            {chatrooms.map((room) => (
              <ChatroomCard
                key={room.room_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <ChatroomTitle>{room.room_name}</ChatroomTitle>
                <ChatroomMeta>
                  <div>생성일: {formatDate(room.created_at)}</div>
                  <div>참석자: {room.participants?.join(', ') || '없음'}</div>
                  <div>메시지 수: {room.message_count || 0}</div>
                  {room.last_updated && (
                    <div>최근 업데이트: {formatDate(room.last_updated)}</div>
                  )}
                </ChatroomMeta>
                <ChatroomActions>
                  <ActionButton
                    variant="primary"
                    onClick={() => viewConversation(room.room_id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Eye size={14} />
                    대화 보기
                  </ActionButton>
                  <ActionButton
                    onClick={() => downloadConversation(room.room_id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Download size={14} />
                    다운로드
                  </ActionButton>
                </ChatroomActions>
              </ChatroomCard>
            ))}
            {chatrooms.length === 0 && (
              <div style={{ 
                gridColumn: '1 / -1', 
                textAlign: 'center', 
                padding: '2rem', 
                color: theme.colors.text.secondary 
              }}>
                아직 생성된 채팅방이 없습니다.
              </div>
            )}
          </ChatroomList>
        )}
      </ContentArea>

      <AnimatePresence>
        {selectedChatroom && (
          <Modal
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedChatroom(null)}
          >
            <ModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ModalHeader>
                <h3>대화 내용</h3>
                <CloseButton onClick={() => setSelectedChatroom(null)}>
                  ×
                </CloseButton>
              </ModalHeader>
              <ConversationContent>
                {conversationContent || '대화 내용을 불러오는 중...'}
              </ConversationContent>
            </ModalContent>
          </Modal>
        )}
      </AnimatePresence>
    </DashboardContainer>
  );
}

export default MemoryDashboard;