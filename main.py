from data.database import init_db
from etl.etl import prepare_data_for_labeling
from labeling.labeling_service import label_batch
from data.db_write import save_labels


BATCH_SIZE = 10

def main():
    print(" START PIPELINE")
    init_db()
    articles = prepare_data_for_labeling()

    if not articles:
        print(" Không có bài nào cần label")
        return

    print(f"Lấy được {len(articles)} bài cần label")

    total = len(articles)
    processed = 0

    for i in range(0, total, BATCH_SIZE):
        batch = articles[i:i+BATCH_SIZE]

        print(f"\n Processing batch {i//BATCH_SIZE + 1}")
        labeled = label_batch(batch)
        save_labels(labeled)
        processed += len(batch)
        print(f" Progress: {processed}/{total}")
    print("\n DONE PIPELINE")


if __name__ == "__main__":
    main()