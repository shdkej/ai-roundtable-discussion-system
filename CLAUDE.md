# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
```bash
# Start backend server
./start_backend.sh

# Manual backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend (React)
```bash
# Start frontend development server  
./start_frontend.sh

# Manual frontend setup
cd frontend
npm install
npm start
```

### Testing
```bash
# Frontend tests
cd frontend
npm test

# Build frontend
cd frontend
npm run build
```

## Architecture Overview

This is a real-time AI roundtable discussion platform with React frontend and FastAPI backend.

### Backend Architecture (`backend/`)
- **`main.py`**: FastAPI server with WebSocket support, CORS middleware, and API endpoints
- **`chat_roundtable.py`**: Core AI discussion system using CrewAI for agent orchestration
- **`memory_system.py`**: FAISS-based vector memory system for conversation storage and retrieval
- **`memory_storage/`**: Directory containing FAISS indices and metadata for persistent memory

### Frontend Architecture (`frontend/src/`)
- **`App.js`**: Main React application component
- **`components/`**: UI components (ChatInterface, DiscussionSetup, MemoryDashboard, etc.)
- **`hooks/`**: Custom React hooks (useDiscussion, useWebSocket)
- **`styles/`**: Styled-components theme configuration

### Key Technologies
- **Backend**: FastAPI, WebSockets, CrewAI, OpenAI GPT-4, FAISS for vector storage
- **Frontend**: React 18, Styled Components, Framer Motion, Axios
- **Real-time Communication**: WebSocket for bidirectional communication

### Environment Setup
- Backend requires `OPENAI_API_KEY` in `backend/.env`
- Optional: `SERPER_API_KEY` for web search functionality
- Backend runs on port 8101, frontend on port 3000
- Frontend proxies API requests to backend via `package.json` proxy setting

### Memory System
- FAISS-based vector storage for conversation history
- Separate memory contexts for chatrooms, agents, and common context
- Automatic conversation logging in markdown format
- Support for multi-room discussions with room switching

### AI Agent System
- 5 specialized AI experts: Design, Sales, Production, Marketing, IT
- Auto-discussion mode with 3-second intervals
- User intervention capabilities during auto-discussions
- Expert-specific questioning system
- Conclusion generation from discussion history

### API Endpoints
- `/api/start_discussion`: Initialize new discussion
- `/api/start_auto_discussion`: Begin automated discussion
- `/api/send_message`: Send user messages
- `/api/ask_expert`: Query specific experts
- `/api/get_conclusion`: Generate discussion summary
- `/ws`: WebSocket endpoint for real-time communication

### Development Notes
- Backend uses uvicorn with auto-reload for development
- Frontend uses React Scripts with hot reload
- WebSocket connection management includes heartbeat and automatic reconnection
- CORS configured for localhost development
- Comprehensive error handling and logging throughout