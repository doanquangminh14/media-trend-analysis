from data.database import SessionLocal, RawArticle, ProcessedArticle
from sqlalchemy.dialects.postgresql import insert

VALID_SENTIMENT = {"Positive", "Negative", "Neutral"}
VALID_INTENT = {"Informational", "Warning", "Promotional"}

def get_existing_link():
    session = SessionLocal()
    try:
        result = session.query(RawArticle.link).all()
        links = [row[0] for row in result]
        return set(links)
    finally:
        session.close()

def insert_data(df3):
    data_to_insert = df3.to_dict(orient= 'records')
    session = SessionLocal()
    try:
        for row in data_to_insert:
            stmt = insert(RawArticle).values(
                title       = row['title'],
                link        = row['link'],
                category    = row['category'],
                content     = row.get('content', None),
                public_date = row.get('public_date', None)
            )  
            stmt = stmt.on_conflict_do_nothing(index_elements = ['link'])
            session.execute(stmt)
        session.commit()
        print(f"Đã chạy xong lệnh lưu dữ liệu. Các bài trùng link sẽ tự động bị bỏ qua.")
    except Exception as e:
        session.rollback()
        print(f"Lỗi khi lưu DB: {e}")
    finally:
        session.close()
        
def save_labels(labeled_data: list):
    session = SessionLocal()
    try:
        if not labeled_data:
            print("Không có dữ liệu để lưu.")
            return
        success = 0
        fail = 0
        
        for row in labeled_data:
            try:
                article_id = row.get("article_id")
                sentiment = row.get("sentiment", "Neutral")
                intent = row.get("intent", "Informational")
                if not article_id:
                    raise ValueError("Missing article_id")
                if sentiment not in VALID_SENTIMENT:
                    sentiment = "Neutral"
                if intent not in VALID_INTENT:
                    intent = "Informational"
                stmt = insert(ProcessedArticle).values(
                    article_id =  article_id,
                    sentiment   =  sentiment,
                    intent     =  intent
                ).on_conflict_do_nothing(index_elements=['article_id'])
                
                session.execute(stmt)
                success += 1
            except Exception as row_error:
                print(f"Lỗi row {row}: {row_error}")
                fail += 1
        session.commit()
        print(f"Đã lưu {success} labels | Lỗi: {fail}")
    except Exception as e:
        session.rollback()
        print(f"Lỗi khi lưu labels: {e}")
    
    finally:
        session.close()