"""LeadBot Pro - Main Application"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
import os
import re

# Fix: Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now use local imports (NO 'app.' prefix)
from database import init_db, get_db
from models import Lead
from ollama_agent import agent

# Create FastAPI app - THIS IS THE 'app' VARIABLE!
app = FastAPI(title="LeadBot Pro", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Initialize database
print("🚀 Starting LeadBot Pro...")
init_db()
print("✅ Database ready")

def extract_name(message):
    """Better name extraction with more patterns"""
    message_lower = message.lower().strip()
    
    # Common name patterns
    patterns = [
        r'my name is ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'my name is ([a-z]+)',
        r"i'?m ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"i'?m ([a-z]+)",
        r'i am ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'i am ([a-z]+)',
        r'this is ([A-Z][a-z]+)',
        r'name is ([A-Z][a-z]+)',
        r'call me ([A-Z][a-z]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Filter out common words that aren't names
            if name.lower() not in ['is', 'the', 'a', 'an', 'and', 'of', 'to', 'for', 'my', 'name', 'i', 'me']:
                return name.title()
    
    return None

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    result = agent.process_message(request.message)
    
    # Improved lead extraction
    name = extract_name(request.message)
    
    if name:
        # Check if lead already exists
        existing_lead = db.query(Lead).filter(Lead.name == name).first()
        if not existing_lead:
            new_lead = Lead(name=name)
            db.add(new_lead)
            db.commit()
            print(f"✅ Lead saved: {name}")
        else:
            print(f"✅ Lead already exists: {name}")
    
    return ChatResponse(response=result["response"])

# Get all leads
@app.get("/leads")
async def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return [{"id": l.id, "name": l.name, "created": str(l.created_at)} for l in leads]

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "model": agent.model}

# Web interface
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>LeadBot Pro</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .chat-container {
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            height: 80vh;
            display: flex;
            flex-direction: column;
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 20px;
        }
        #messages {
            flex: 1;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user {
            text-align: right;
        }
        .user .content {
            background: #667eea;
            color: white;
            display: inline-block;
            padding: 10px 18px;
            border-radius: 20px;
            max-width: 70%;
            text-align: left;
        }
        .bot {
            text-align: left;
        }
        .bot .content {
            background: white;
            color: #333;
            display: inline-block;
            padding: 10px 18px;
            border-radius: 20px;
            max-width: 70%;
            border: 1px solid #e0e0e0;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        input:focus {
            border-color: #667eea;
        }
        button {
            padding: 12px 28px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #5a67d8;
        }
        .status {
            text-align: center;
            margin-top: 10px;
            font-size: 12px;
            color: #28a745;
        }
        .typing {
            color: #999;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <h1>🤖 LeadBot Pro</h1>
        <div id="messages">
            <div class="message bot">
                <div class="content">
                    👋 Hello! I'm LeadBot Pro.<br>
                    Tell me about yourself! Try saying:<br>
                    • "My name is John"<br>
                    • "I work at Google"<br>
                    • "I need help with lead generation"
                </div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
        <div class="status" id="status">✅ Connected</div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            const messages = document.getElementById('messages');
            messages.innerHTML += `<div class="message user"><div class="content">${escapeHtml(message)}</div></div>`;
            input.value = '';
            
            const typingId = Date.now();
            messages.innerHTML += `<div class="message bot" id="typing-${typingId}"><div class="content typing">🤖 Typing...</div></div>`;
            messages.scrollTop = messages.scrollHeight;
            
            document.getElementById('status').innerHTML = '🤔 AI is thinking...';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                
                document.getElementById(`typing-${typingId}`).remove();
                messages.innerHTML += `<div class="message bot"><div class="content">${escapeHtml(data.response)}</div></div>`;
                messages.scrollTop = messages.scrollHeight;
                document.getElementById('status').innerHTML = '✅ Ready';
            } catch (error) {
                document.getElementById(`typing-${typingId}`).remove();
                messages.innerHTML += `<div class="message bot"><div class="content">❌ Error: ${error.message}</div></div>`;
                document.getElementById('status').innerHTML = '❌ Connection error';
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv
    load_dotenv()
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 LeadBot Pro starting on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)