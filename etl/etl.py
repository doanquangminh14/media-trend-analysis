import re
from data.database import *
import unicodedata

def get_existing_link():
    session = SessionLocal()
    try:
        result = session.query(RawArticle.link).all()
        links = [row[0] for row in result]
        return set(links)
    finally:
        session.close()
        

def get_unlabeled_articles(limit = 100):
    session = SessionLocal()
    try:
        query = (
            session.query(
                RawArticle.id,
                RawArticle.content,
                RawArticle.category
            )
            .outerjoin(
                ProcessedArticle,
                RawArticle.id == ProcessedArticle.article_id
            )
            .filter(ProcessedArticle.article_id == None)
            .filter(RawArticle.content != None)
            .filter(RawArticle.content != "")
            .order_by(RawArticle.id.asc())
            .limit(limit)
        )
        result = query.all()
        return [
            {
                "id": r.id,
                "content": r.content.strip(),
                "category": r.category
            }
            for r in result
        ]
    finally:
        session.close()
        

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = unicodedata.normalize("NFC",text)
    
    text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)
    
    text = re.sub(r"http\S+|www\S+", " ", text)
    
    boilerplate_patterns = [
        r"Theo dõi.*?Facebook.*?\.",
        r"Theo dõi.*?TikTok.*?\.",
        r"Mọi ý kiến.*?xin gửi.*?\.",
        r"Bản quyền.*?\.",
        r"Xem thêm.*?\.",
    ]
    
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, " ", text, flags = re.IGNORECASE)
    
    text = re.sub(r"[^\w\sÀ-ỹ]", " ", text)
    
    text = re.sub(r"\s+", " ",text)
    
    text = text.strip()
    
    return text

def prepare_data_for_labeling():
    articles = get_unlabeled_articles()
    
    cleaned = []
    
    for a in articles:
        text = clean_text(a["content"])
        
        if text and len(text) > 200:
            cleaned.append({
                "id":a["id"],
                "content":text[:1000],
                "category":a["category"]
            })
    return cleaned