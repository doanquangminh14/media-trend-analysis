import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit = False,  autoflush = False, bind = engine)
Base = declarative_base()

class RawArticle(Base):
    __tablename__ = "raw_articles"
    id           = Column(Integer, primary_key = True, index = True)
    title        = Column(Text, nullable = False)
    content      = Column(Text, nullable = False)
    category     = Column(Text, nullable = False)
    link         = Column(Text, unique = True, nullable = False)
    public_date  = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default = func.now())
    
    processed_data = relationship("ProcessedArticle", back_populates="raw_articles")
    
class ProcessedArticle(Base):
    __tablename__ = "processed_articles"
    id           = Column(Integer, primary_key = True, index = True)
    article_id   = Column(Integer, ForeignKey('raw_articles.id'), unique = True)
    sentiment    = Column(Text)
    intent       = Column(Text)
    processed_at   = Column(DateTime(timezone=True), server_default = func.now())
    
    __table_args__ = (
        CheckConstraint(sentiment.in_(['Positive', 'Negative', 'Neutral'])),
        CheckConstraint(intent.in_(['Informational', 'Warning', 'Promotional']))
    )
    
    raw_article = relationship('RawArticle', back_populates= "processed_data")
    
def init_db():
    Base.metadata.create_all(bind = engine)
    
