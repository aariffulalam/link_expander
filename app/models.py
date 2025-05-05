from sqlalchemy import Column, String, Text, DateTime, Integer, Index
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class URLExpansionLog(Base):
    __tablename__ = "expand_url_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    url = Column(String(765), nullable=False)
    expanded_url = Column(String(765), nullable=False)
    expanded = Column(TINYINT(1), nullable=False)  # Explicitly use TINYINT(1) for MySQL
    error_message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Define indexes to match the SQL migration
    __table_args__ = (
        Index('idx_url', 'url'),
        Index('idx_expanded_url', 'expanded_url'),
        Index('idx_expanded', 'expanded'),
        Index('idx_created_at', 'created_at'),
    )