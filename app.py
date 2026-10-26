import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from chatbot import FAQBot

PORT = 5000
bot = FAQBot("faqs.json")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }

        .chat-box {
            width: 100%;
            max-width: 520px;
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            height: 600px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        }

        .header {
            background: #2b5c8f;
            color: #ffffff;
            padding: 14px 18px;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
        }

        .header h2 {
            margin: 0;
            font-size: 18px;
        }

        .header p {
            margin: 4px 0 0;
            font-size: 12px;
            opacity: 0.9;
        }

        .quick-questions {
            display: flex;
            gap: 6px;
            padding: 8px 12px;
            background: #f9f9f9;
            border-bottom: 1px solid #eee;
            overflow-x: auto;
        }

        .quick-questions button {
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 11px;
            cursor: pointer;
            white-space: nowrap;
        }

        .quick-questions button:hover {
            background: #eef2f7;
        }

        .messages-area {
            flex: 1;
            padding: 14px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .msg {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 14px;
            line-height: 1.4;
        }

        .bot-msg {
            background: #f1f3f5;
            color: #222;
            align-self: flex-start;
        }

        .user-msg {
            background: #2b5c8f;
            color: #fff;
            align-self: flex-end;
        }

        .match-info {
            font-size: 11px;
            color: #777;
            margin-top: 4px;
        }

        .input-row {
            display: flex;
            padding: 12px;
            border-top: 1px solid #eee;
            background: #fff;
        }

        .input-row input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            outline: none;
        }

        .input-row button {
            margin-left: 8px;
            padding: 10px 18px;
            background: #2b5c8f;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }

        .input-row button:hover {
            background: #20456c;
        }
    </style>
</head>
<body>

<div class="chat-box">
    <div class="header">
        <h2>FAQ Assistant</h2>
        <p>Ask questions regarding orders, returns, and support</p>
    </div>

    <div class="quick-questions">
        <button onclick="setQuery('What is your return policy?')">Return Policy</button>
        <button onclick="setQuery('How do I track my order?')">Track Order</button>
        <button onclick="setQuery('How long does shipping take?')">Shipping Time</button>
        <button onclick="setQuery('What payment methods do you accept?')">Payments</button>
    </div>

    <div class="messages-area" id="messagesArea">
        <div class="msg bot-msg">
            Hi, how can I help you today? Feel free to ask any question.
        </div>
    </div>

    <form class="input-row" onsubmit="sendMessage(event)">
        <input type="text" id="userInput" placeholder="Type your question..." autocomplete="off">
        <button type="submit">Send</button>
    </form>
</div>

<script>
    const messagesArea = document.getElementById('messagesArea');
    const userInput = document.getElementById('userInput');

    function appendMessage(text, isUser, matchText = "") {
        const div = document.createElement('div');
        div.className = 'msg ' + (isUser ? 'user-msg' : 'bot-msg');
        div.innerText = text;

        if (matchText) {
            const info = document.createElement('div');
            info.className = 'match-info';
            info.innerText = matchText;
            div.appendChild(info);
        }

        messagesArea.appendChild(div);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    function setQuery(text) {
        userInput.value = text;
        sendMessage(new Event('submit'));
    }

    async function sendMessage(e) {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        appendMessage(text, true);
        userInput.value = '';

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });
            const data = await res.json();
            
            let info = '';
            if (data.matched_question) {
                info = `Matched: "${data.matched_question}" (Confidence: ${Math.round(data.score * 100)}%)`;
            }
            appendMessage(data.answer, false, info);
        } catch (err) {
            appendMessage('Error reaching server. Please check your connection.', false);
        }
    }
</script>

</body>
</html>
"""

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            query = data.get("question", "")
            result = bot.get_answer(query)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Keep terminal output clean
        pass


def run():
    server = HTTPServer(("127.0.0.1", PORT), ChatHandler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Chatbot server running at: {url}")
    print("Press Ctrl+C to stop.")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()


if __name__ == "__main__":
    run()
