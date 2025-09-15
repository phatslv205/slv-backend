from extensions import db
from datetime import datetime

class NoiTuGameHistory(db.Model):
    __tablename__ = "noi_tu_game_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.user_id"))
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

    total_turns = db.Column(db.Integer, default=0)
    result = db.Column(db.String(10))  # 'win' | 'lose' | 'draw'
    reward_used = db.Column(db.String(100))
    
    user_final_word = db.Column(db.String(100))
    ai_final_word = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_turns": self.total_turns,
            "result": self.result,
            "reward_used": self.reward_used,
            "user_final_word": self.user_final_word,
            "ai_final_word": self.ai_final_word
        }
