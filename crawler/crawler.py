import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.etl import *


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options = chrome_options)
url_categories = {'Thể thao':'https://vnexpress.net/the-thao',
                  #'Kinh doanh':'https://vnexpress.net/kinh-doanh',
                  #'Sức khỏe':'https://vnexpress.net/suc-khoe',
                  #'Thế giới':'https://vnexpress.net/the-gioi'
                  }

def crawler(url_categories):
    all_article_content = []
    for name_category , base_url in url_categories.items():
        max_page = 1
        for page in range(1, max_page +1):
            if page == 1:
                target_url = base_url
            else:
                target_url = f"{base_url}-p{page}"
            driver.get(target_url)
            time.sleep(3)
            data_html = driver.page_source
            html_content = BeautifulSoup(data_html,"html.parser")
            article_content = html_content.find_all('h3',{'class':'title-news'})
            for i in article_content:
                a_tag = i.find('a')
                if a_tag:
                    title = a_tag.get('title')
                    link = a_tag.get('href')
                    category = name_category
                    if title and link :
                        all_article_content.append({
                            'title':title,
                            'link':link,
                            'category':category
                        })
    df1 = pd.DataFrame(all_article_content)
    df1 = df1.drop_duplicates(subset=['link'], keep='first')
    return df1 

def get_content_link(df1):
    links = df1['link'].tolist()
    all_normal_content = []
    for url in links:
        try:
            driver.get(url)
            time.sleep(3)
            data_html = driver.page_source
        except Exception as e:
            print(f"Lỗi truy cập {url} : {e}")
            continue
        try:
            html_content = BeautifulSoup(data_html,"html.parser")
            paragraphs = html_content.find_all('p',{'class':'Normal'})
            contents_text = ' '.join([p.text for p in paragraphs])
            date_tag = html_content.find('span',{'class':'date'})
            public_date = date_tag.text.strip() if date_tag else None
            all_normal_content.append({
                'link':url,
                'content':contents_text,
                'public_date':public_date
            })
        except AttributeError as e:
            print(f"Bỏ qua (lỗi html) {url}: {e}")
            continue
    df2 = pd.DataFrame(all_normal_content)
    return df2

def merge_df(df1,df2):
    df3 = pd.merge(df1,df2, on = 'link', how = 'left')
    return df3


def run():
    df1 = crawler(url_categories)
    existing_links = get_existing_link()
    df1_filtered = df1[~df1['link'].isin(existing_links)]
    print(f"Tổng bài crawl được: {len(df1)}")
    print(f"Bài đã có trong DB: {len(df1) - len(df1_filtered)}")
    print(f"Bài mới sẽ crawl conent: {len(df1_filtered)}")
    if df1_filtered.empty:
        print("Không có bài mới!!")
        return
    df2 = get_content_link(df1_filtered)
    df3 = merge_df(df1_filtered,df2)
    driver.quit()
    return df3
