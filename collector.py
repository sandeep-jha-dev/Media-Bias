# import newspaper
# import pandas as pd
# import re
# from unidecode import unidecode
# import ftfy

# def clean_text(text):

#     if not text:
#         return ""

#     text = ftfy.fix_text(text)
#     text = re.sub(r'[^\x00-\x7F]+', ' ', text)   
#     text = text.replace('\n', ' ').replace('\r', ' ')
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# source_url = 'https://indianexpress.com/section/political-pulse/'

# news_source = newspaper.build(source_url, memoize_articles=False)

# print(f"Found {len(news_source.articles)} articles. Starting download...")

# final_data = []

# for article in news_source.articles[:20]:
#     try:
#         article.download()
#         article.parse()

#         cleaned_text = clean_text(article.text)

#         if len(cleaned_text) < 300:
#             continue
#         final_data.append({
#             'title': article.title.strip(),
#             'text': cleaned_text,
#             'url': article.url,
#         })
#         print(f"Successfully scraped: {article.title[:50]}...")
#     except Exception as e:
#         print(f"Failed to scrape an article: {e}")

# df = pd.DataFrame(final_data)

# if not df.empty:
#     initial_count = len(df)
#     df = df.drop_duplicates(subset=['title'], keep='first')
#     df = df.drop_duplicates(subset=['text'], keep='first')
#     print(f"\nRemoved {initial_count - len(df)} duplicate articles.")
#     df.to_csv('political_news_final.csv', index = False, encoding = 'utf-8-sig')
#     print(f"Final dataset saved with {len(df)} clean, unique articles.")
# else:
#     print("No articles were collected. Check your internet or sourdce URL.")


# import newspaper
# import pandas as pd
# import re
# import ftfy
# import time
# import random

# def is_english(text):
#     """Returns True if the string is mostly English/ASCII."""
#     try:
#         text.encode('ascii')
#         return True
#     except UnicodeEncodeError:
#         return False

# def clean_text(text):
#     if not text:
#         return ""
#     # 1. Fix encoding errors (Mojibake)
#     text = ftfy.fix_text(text)
#     # 2. Remove non-ASCII characters (This will strip Tamil/Hindi fonts)
#     text = re.sub(r'[^\x00-\x7F]+', ' ', text)   
#     # 3. Standardize whitespace
#     text = text.replace('\n', ' ').replace('\r', ' ')
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# source_url = 'https://indianexpress.com/section/political-pulse/'

# # memoize_articles=False ensures it doesn't 'remember' old runs
# news_source = newspaper.build(source_url, memoize_articles=False)

# print(f"Found {len(news_source.articles)} potential articles. Filtering and Downloading...")

# final_data = []

# # We'll use a set to track URLs to avoid double-processing
# seen_urls = set()

# for article in news_source.articles:
#     # Stop once we have a good sample for testing (e.g., 50 articles)
#     if len(final_data) >= 50:
#         break
        
#     try:
#         # SAFETY CHECK 1: Ensure the URL actually belongs to Political Pulse
#         if 'political-pulse' not in article.url:
#             continue
            
#         if article.url in seen_urls:
#             continue

#         article.download()
#         article.parse()

#         # SAFETY CHECK 2: Language Filter for Title
#         # This solves your "Tamil Title" issue
#         if not is_english(article.title):
#             print(f"Skipping non-English article: {article.title[:30]}...")
#             continue

#         cleaned_text = clean_text(article.text)

#         # SAFETY CHECK 3: Length Filter
#         if len(cleaned_text) < 500: # Increased slightly to ensure high-quality snippets
#             continue

#         final_data.append({
#             'title': article.title.strip(),
#             'text': cleaned_text,
#             'url': article.url,
#         })
        
#         seen_urls.add(article.url)
#         print(f"Successfully scraped ({len(final_data)}): {article.title[:50]}...")
        
#         # RATE LIMITING: Don't get banned!
#         time.sleep(random.uniform(1, 2))

#     except Exception as e:
#         print(f"Error processing {article.url}: {e}")

# # Save the data
# df = pd.DataFrame(final_data)

# if not df.empty:
#     initial_count = len(df)
#     # Drop duplicates by title and text to be safe
#     df = df.drop_duplicates(subset=['title'], keep='first')
#     df = df.drop_duplicates(subset=['text'], keep='first')
    
#     print(f"\nFinal count after duplicate removal: {len(df)}")
#     df.to_csv('political_news_final.csv', index=False, encoding='utf-8-sig')
#     print("Dataset saved to political_news_final.csv")
# else:
#     print("No articles collected.")

import cloudscraper
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import time
import random
import re
import ftfy

def clean_text(text):
    if not text: return ""
    text = ftfy.fix_text(text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)   
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 1. Get the links (The part that finally worked for you!)
def get_links():
    scraper = cloudscraper.create_scraper()
    url = "https://indianexpress.com/section/political-pulse/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    
    try:
        r = scraper.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/article/political-pulse/' in href and href.count('/') > 5:
                links.append(href)
        return list(set(links))
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    links = get_links()
    
    if links:
        print(f"Found {len(links)} links. Starting the actual scraping...")
        scraped_articles = []

        for i, url in enumerate(links):
            try:
                # 2. Download and Parse each article
                article = Article(url)
                article.download()
                article.parse()
                
                body = clean_text(article.text)
                
                # Only keep articles with actual content
                if len(body) > 400:
                    scraped_articles.append({
                        'title': article.title.strip(),
                        'text': body,
                        'url': url
                    })
                    print(f"[{i+1}/{len(links)}] Scraped: {article.title[:40]}...")
                
                # Wait 2 seconds between articles so the server doesn't block you again
                time.sleep(2)
                
            except Exception as e:
                print(f"Skipping {url} due to error.")

        # 3. CRITICAL: Save everything to a CSV file
        df = pd.DataFrame(scraped_articles)
        df.to_csv('political_news_scraped.csv', index=False, encoding='utf-8-sig')
        print(f"\nDONE! Created 'political_news_scraped.csv' with {len(df)} articles.")
    else:
        print("No links found to scrape.")