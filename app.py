import asyncio
from flask import Flask, render_template, request, jsonify
from database import init_db, create_conversation, save_message, get_conversations, get_conversation_messages
from pipeline import LegalPipeline
from config import FLASK_DEBUG, PORT

app = Flask(__name__)

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    conversation_id = data.get("conversation_id")
    
    if not question:
        return jsonify({"error": "السؤال مطلوب"}), 400
    
    if not conversation_id:
        conversation_id = create_conversation(title=question[:50])
    
    save_message(conversation_id, "user", question)
    
    try:
        result = asyncio.run(LegalPipeline.process(question))
        
        response_content = result["final_response"]["opinion"]
        disclaimer = result["final_response"]["disclaimer"]
        full_response = f"{response_content}\n\n---\n{disclaimer}"
        
        save_message(conversation_id, "assistant", full_response, metadata=result["stages"])
        
        return jsonify({
            "conversation_id": conversation_id,
            "response": full_response,
            "stages": result["stages"],
            "final_response": result["final_response"]
        })
    except Exception as e:
        error_msg = f"حدث خطأ أثناء المعالجة: {str(e)}"
        return jsonify({"error": error_msg}), 500

@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    conversations = get_conversations()
    return jsonify(conversations)

@app.route("/api/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    messages = get_conversation_messages(conversation_id)
    return jsonify(messages)

if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, port=PORT)
