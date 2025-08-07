from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import time
import os

app = Flask(__name__)
CORS(app)

# ✅ Your Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# 🛡 Simple in-memory rate limit store
rate_limit_store = {}


@app.route('/ask', methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    user_id = data.get("userId", "default")

    print("🟢 Received question:", question)

    # ✅ Prompt prefix
    prompt = "Answer like you're a helpful assistant. " + question

    # 🧠 Rate limit: Max 5 questions per session
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = {"count": 0, "start_time": time.time()}

    if rate_limit_store[user_id]["count"] >= 5:
        return jsonify({"response": "❌ Rate limit exceeded (max 5 questions per session)."}), 429

    rate_limit_store[user_id]["count"] += 1

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            model="llama3-8b-8192"
        )

        reply = chat_completion.choices[0].message.content
        print("🤖 Groq replied:", reply)
        return jsonify({"response": reply})

    except Exception as e:
        print("❌ Error calling Groq API:", str(e))
        return jsonify({"response": "Something went wrong with the AI model."}), 500


if(__name__=="__main__"):
    app.run(host="0.0.0.0", port=5000)