import requests

# Dynamic functions using bot_token and channel_id from DB

def get_followers(bot_token, channel_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMemberCount?chat_id={channel_id}"
    r = requests.get(url)
    data = r.json()
    if data.get("ok"):
        return data["result"]
    return None

def get_admins(bot_token, channel_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatAdministrators?chat_id={channel_id}"
    r = requests.get(url)
    data = r.json()
    if data.get("ok"):
        admins = []
        for a in data["result"]:
            admins.append({
                "user_id": a["user"]["id"],
                "username": a["user"].get("username"),
                "status": a["status"]
            })
        return admins
    return []

def get_user_id(bot_token, channel_id, username):
    # Get user_id from username
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={channel_id}&user_id=@{username}"
    r = requests.get(url)
    data = r.json()
    if data.get("ok"):
        return data["result"]["user"]["id"]
    return None

def promote_user(bot_token, channel_id, username):
    user_id = get_user_id(bot_token, channel_id, username)
    if not user_id:
        return {"error": "User not found or bot not admin"}
    
    url = f"https://api.telegram.org/bot{bot_token}/promoteChatMember"
    payload = {
        "chat_id": channel_id,
        "user_id": user_id,
        "can_change_info": True,
        "can_post_messages": True,
        "can_delete_messages": True,
        "can_invite_users": True,
        "can_pin_messages": True,
        "can_promote_members": False
    }
    r = requests.post(url, data=payload)
    return r.json()

def revoke_admin(bot_token, channel_id, username):
    user_id = get_user_id(bot_token, channel_id, username)
    if not user_id:
        return {"error": "User not found or bot not admin"}
    
    url = f"https://api.telegram.org/bot{bot_token}/promoteChatMember"
    payload = {
        "chat_id": channel_id,
        "user_id": user_id,
        "can_change_info": False,
        "can_post_messages": False,
        "can_delete_messages": False,
        "can_invite_users": False,
        "can_pin_messages": False,
        "can_promote_members": False
    }
    r = requests.post(url, data=payload)
    return r.json()
