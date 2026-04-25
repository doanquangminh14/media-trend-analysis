Create Table raw_articles (
    id           Serial Primary Key,
    title        Text Not Null,
    content      Text,
    category     Text Not Null,
    link         Text Unique Not Null,
    public_date  Text,
    created_at   Timestamptz Default Now()    
);


Create Table processed_articles (
    id           Serial Primary Key,
    article_id   Int,
    sentiment    Text Check (sentiment In ('Positive', 'Negative', 'Neutral')),
    intent       Text Check (intent In ('Informational', 'Warning', 'Promotional')),
    processed_at Timestamptz Default Now(),
    Constraint fk_raw_article Foreign Key(article_id) References raw_articles(id) 
);



Create Unique Index idx_processed_article_id On processed_articles(article_id);

Create View vw_articles_full As 
Select r.id, r.category, r.title, r.public_date, p.sentiment, p.intent
From raw_articles r
Left Join processed_articles p On r.id = p.article_id