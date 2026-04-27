from data.database import SessionLocal, RawArticle, ProcessedArticle
from sqlalchemy.dialects.postgresql import insert

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
        for row in labeled_data:
            stmt = insert(ProcessedArticle)