import regex
from data.database import *

def get_existing_link():
    session = SessionLocal()
    try:
        result = session.query(RawArticle.link).all()
        links = [row[0] for row in result]
        return set(links)
    finally:
        session.close()
        

def get_unlabeled_articles(limit):
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
            .filter(limit)
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