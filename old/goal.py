from datetime import datetime
from flask import jsonify, request, make_response

def get_goal(collection, title):
    goal = collection.find_one({"title": title})
    return _handle_goal_response(goal)

def get_goal_by_id(collection, id):
    goal = collection.find_one({"_id": id})
    return _handle_goal_response(goal)

def get_goals_by_user_id(collection, user_id):
    goals = list(collection.find({"owner": user_id}))
    return jsonify(goals)

def create_goal(collection, data):
    goal_data = _create_goal_data(data)
    insert_result = collection.insert_one(goal_data)
    return _create_success_response(insert_result.inserted_id)

def delete_goal(collection, title):
    delete_result = collection.delete_one({"title": title})
    return _handle_delete_response(delete_result)

def _handle_goal_response(goal):
    if goal:
        return jsonify(goal)
    else:
        return _create_error_response("Goal not found")

def _create_goal_data(data):
    return {
        "title": data.get('title'),
        "name": data.get('name'),
        "due_date": datetime.strptime(data.get('due_date'), '%Y-%m-%d') if data.get('due_date') else None,
        "creation_date": datetime.now(),
        "owner": data.get('owner'),
        "progress": data.get('progress'),
        "status": data.get('status'),
        "user_id": data.get('user_id')
    }

def _create_success_response(id):
    return jsonify({"id": str(id)})

def _handle_delete_response(delete_result):
    if delete_result.deleted_count > 0:
        return jsonify({"message": "Goal deleted successfully"})
    else:
        return _create_error_response("Goal not found")

def _create_error_response(message):
    return make_response(jsonify({"error": message}), 404)

