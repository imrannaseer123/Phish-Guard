from flask import Blueprint, request, jsonify
import chatbot_service
import config

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/message', methods=['POST'])
def handle_message():
    """
    Handle user messages for the chatbot.
    Input: { "message": str, "context": dict }
    Output: { "response": str, "source": str }
    """
    if not config.ENABLE_CHATBOT:
        return jsonify({"error": "Chatbot feature is disabled"}), 403

    data = request.get_json()
    user_message = data.get('message', '')
    context = data.get('context', {})
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        result = chatbot_service.process_message(user_message, context)
        return jsonify(result)
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({
            "response": "I encountered an error processing your request. Please try again.",
            "source": "System Error"
        }), 500
