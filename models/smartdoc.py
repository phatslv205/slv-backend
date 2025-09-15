from extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class SmartDoc(db.Model):
    __tablename__ = "smart_docs"

    doc_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=True)
    description = db.Column(db.Text, nullable=False)   # Mô tả yêu cầu của người dùng
    author_name = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)       # Nội dung AI trả về (dạng văn bản)
    file_type = db.Column(db.String(10), default="docx")  # Loại file ('docx', 'pdf' nếu sau này có)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ ngược về user
    user = db.relationship("User", backref=db.backref("smartdocs", lazy=True))
