from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
class NoiTuLeaderboard(db.Model):
    __tablename__ = 'noi_tu_leaderboard'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False, unique=True)

    wins = db.Column(db.Integer, default=0)
    total_games = db.Column(db.Integer, default=0)
    last_win_time = db.Column(db.DateTime, default=datetime.utcnow)
def update_leaderboard(user_id, won=False):
    stmt = insert(NoiTuLeaderboard).values(
        user_id=user_id,
        total_games=1,
        wins=1 if won else 0,
        last_win_time=datetime.utcnow()
    ).on_conflict_do_update(
        index_elements=['user_id'],
        set_={
            "total_games": NoiTuLeaderboard.total_games + 1,
            "wins": NoiTuLeaderboard.wins + (1 if won else 0),
            "last_win_time": datetime.utcnow()
        }
    )
    db.session.execute(stmt)
    db.session.commit()