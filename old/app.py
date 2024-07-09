import pymongo
from flask import Flask, jsonify
from goal import get_goal, create_goal, delete_goal
from openai import chat_with_gpt

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["goals_database"]
goals_collection = db["goals_collection"]
users_collection = db["users"]

app = Flask(__name__)

# Specify the Prompt here
PROMPT = "Hello, how can I help you?"

@app.route('/goal', methods=['GET'])
def goal_get():
    try:
        goal = get_goal(goals_collection)
        if goal:
            return jsonify(goal)
        else:
            return jsonify({"error": "Goal not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/goal', methods=['POST'])
def goal_create():
    try:
        return create_goal(goals_collection)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/goal/<title>', methods=['DELETE'])
def goal_delete(title):
    try:
        return delete_goal(goals_collection, title)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example usage of chat_with_gpt
@app.route('/chat_with_gpt/<user_id>/<prompt>', methods=['GET'])
def chat(user_id):
    try:
        response = chat_with_gpt(users_collection, user_id, PROMPT, audio=False)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
