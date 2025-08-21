import { useState, useEffect, useRef } from 'react';

export const useWebSocket = (url, options = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [shouldReconnect, setShouldReconnect] = useState(true);
  const websocket = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatTimeoutRef = useRef(null);
  const maxReconnectAttempts = 3; // 재연결 시도 횟수를 3으로 줄임
  const heartbeatInterval = 30000; // 30초마다 heartbeat
  // 콜백 함수들을 ref로 저장하여 재렌더링에 영향받지 않도록 함
  const optionsRef = useRef(options);
  optionsRef.current = options;

  useEffect(() => {
    const connect = () => {
      try {
        // 기존 연결이 있으면 정리
        if (websocket.current) {
          websocket.current.close();
        }
        
        console.log('WebSocket 연결 시도:', url);
        websocket.current = new WebSocket(url);

        websocket.current.onopen = () => {
          console.log('WebSocket 연결 성공');
          setIsConnected(true);
          setError(null);
          setReconnectAttempts(0);
          
          // heartbeat 시작
          heartbeatTimeoutRef.current = setInterval(() => {
            if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
              websocket.current.send(JSON.stringify({ type: 'ping' }));
            }
          }, heartbeatInterval);
          
          if (optionsRef.current.onConnect) optionsRef.current.onConnect();
        };

        websocket.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            // ping/pong은 로그에서 제외
            if (data.type !== 'pong') {
              console.log('WebSocket 메시지 수신:', data);
            }
            if (optionsRef.current.onMessage) optionsRef.current.onMessage(data);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err, event.data);
          }
        };

        websocket.current.onclose = (event) => {
          console.log('WebSocket 연결 종료:', event.code, event.reason);
          setIsConnected(false);
          
          // heartbeat 정리
          if (heartbeatTimeoutRef.current) {
            clearInterval(heartbeatTimeoutRef.current);
            heartbeatTimeoutRef.current = null;
          }
          
          if (optionsRef.current.onDisconnect) optionsRef.current.onDisconnect();
          
          // 재연결 시도 (shouldReconnect가 true이고 최대 횟수 미만일 때만)
          if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
            const timeout = Math.min(3000 * Math.pow(2, reconnectAttempts), 30000);
            console.log(`${timeout}ms 후 재연결 시도 (${reconnectAttempts + 1}/${maxReconnectAttempts})`);
            
            setReconnectAttempts(prev => prev + 1);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
                connect();
              }
            }, timeout);
          } else if (reconnectAttempts >= maxReconnectAttempts) {
            console.error('최대 재연결 시도 횟수 초과 - 재연결 중지');
            setShouldReconnect(false);
            setError(new Error(`서버에 연결할 수 없습니다 (${maxReconnectAttempts}회 시도 실패). 수동으로 재연결을 시도하거나 백엔드 서버 상태를 확인해주세요.`));
          }
        };

        websocket.current.onerror = (err) => {
          console.error('WebSocket 오류:', err);
          setError(err);
          if (optionsRef.current.onError) optionsRef.current.onError(err);
        };
      } catch (err) {
        console.error('WebSocket 연결 시도 실패:', err);
        setError(err);
        if (optionsRef.current.onError) optionsRef.current.onError(err);
      }
    };

    connect();

    return () => {
      // 모든 타이머와 연결 정리
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (heartbeatTimeoutRef.current) {
        clearInterval(heartbeatTimeoutRef.current);
        heartbeatTimeoutRef.current = null;
      }
      if (websocket.current) {
        websocket.current.onopen = null;
        websocket.current.onmessage = null;
        websocket.current.onclose = null;
        websocket.current.onerror = null;
        websocket.current.close();
        websocket.current = null;
      }
      // 재연결 중지
      setShouldReconnect(false);
    };
  }, [url]);

  const sendMessage = (message) => {
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(JSON.stringify(message));
      return true;
    } else {
      console.warn('WebSocket이 연결되지 않음. 메시지 전송 실패:', message);
      return false;
    }
  };

  const manualReconnect = () => {
    console.log('수동 재연결 시도');
    setReconnectAttempts(0);
    setError(null);
    setShouldReconnect(true);
    
    // 모든 타이머 정리
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
    
    // 기존 WebSocket 연결 정리 후 새로 연결
    if (websocket.current) {
      websocket.current.onopen = null;
      websocket.current.onmessage = null;
      websocket.current.onclose = null;
      websocket.current.onerror = null;
      websocket.current.close();
    }
    
    // 강제로 useEffect 재실행 (URL을 동일하게 유지하면서)
    setTimeout(() => {
      try {
        websocket.current = new WebSocket(url);
        
        websocket.current.onopen = () => {
          console.log('수동 재연결 성공');
          setIsConnected(true);
          setError(null);
          setReconnectAttempts(0);
          
          // heartbeat 시작
          heartbeatTimeoutRef.current = setInterval(() => {
            if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
              websocket.current.send(JSON.stringify({ type: 'ping' }));
            }
          }, heartbeatInterval);
          
          if (optionsRef.current.onConnect) optionsRef.current.onConnect();
        };

        // 기존 이벤트 핸들러들 다시 등록
        websocket.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type !== 'pong') {
              console.log('WebSocket 메시지 수신:', data);
            }
            if (optionsRef.current.onMessage) optionsRef.current.onMessage(data);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err, event.data);
          }
        };

        websocket.current.onclose = (event) => {
          console.log('WebSocket 연결 종료:', event.code, event.reason);
          setIsConnected(false);
          if (heartbeatTimeoutRef.current) {
            clearInterval(heartbeatTimeoutRef.current);
            heartbeatTimeoutRef.current = null;
          }
          if (optionsRef.current.onDisconnect) optionsRef.current.onDisconnect();
        };

        websocket.current.onerror = (err) => {
          console.error('WebSocket 오류:', err);
          setError(err);
          if (optionsRef.current.onError) optionsRef.current.onError(err);
        };
      } catch (err) {
        console.error('수동 재연결 실패:', err);
        setError(err);
      }
    }, 100);
  };

  const stopReconnecting = () => {
    console.log('재연결 시도 중지');
    setShouldReconnect(false);
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  };

  return {
    isConnected,
    error,
    reconnectAttempts,
    shouldReconnect,
    sendMessage,
    manualReconnect,
    stopReconnecting
  };
};