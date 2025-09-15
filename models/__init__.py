from extensions import db  

# Import tất cả model sau khi tạo db
from .user import User
from .message import Message
from .chat_history import ChatHistory
from .transaction import Transaction
from .friend import Friend
from .friend_request import FriendRequest
from .blocked_user_log import BlockedUserLog
from .daily_usage_stats import DailyUsageStats
from .image_history import ImageHistory
from .feedback import Feedback 
from .dev_chat_history import DevChatHistory
from .user_memory import UserMemoryItem
from .smartdoc import SmartDoc 