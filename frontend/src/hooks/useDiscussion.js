import { useState, useCallback } from 'react';

export const useDiscussion = () => {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState({
    autoDiscussionEnabled: false,
    userInterventionPending: false,
    discussionState: 'ready',
    discussionRounds: 0,
    currentSpeaker: { name: '', isTyping: false },
    totalMessages: 0,
    activeParticipants: []
  });

  const addMessage = useCallback((message) => {
    console.log('addMessage 호출됨:', message);
    setMessages(prev => {
      console.log('현재 메시지 목록:', prev);
      // 중복 메시지 방지
      const isDuplicate = prev.some(msg => 
        msg.id === message.id || 
        (msg.sender === message.sender && 
         msg.content === message.content && 
         Math.abs(new Date(msg.timestamp) - new Date(message.timestamp)) < 1000)
      );
      
      if (isDuplicate) {
        console.log('중복 메시지 발견, 추가하지 않음:', message);
        return prev;
      }
      
      const newMessages = [...prev, message];
      console.log('메시지 추가 후 목록:', newMessages);
      return newMessages;
    });
    setStatus(prev => ({
      ...prev,
      totalMessages: prev.totalMessages + 1
    }));
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const updateStatus = useCallback((newStatus) => {
    if (typeof newStatus === 'function') {
      setStatus(newStatus);
    } else {
      setStatus(prev => ({ ...prev, ...newStatus }));
    }
  }, []);

  return {
    messages,
    addMessage,
    clearMessages,
    status,
    updateStatus
  };
};