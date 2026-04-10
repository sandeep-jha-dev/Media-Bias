from google import genai
import pandas as pd
import json
import time

client = genai.Client(api_key="AIzaSyD0bPq-awMD1VXcUXZFH0rOHXxl6YmETcM")
MODEL_NAME = "gemini-2.5-flash-lite" 

def get_triples(text_snippet, retries=3):
    prompt = f"Extract Knowledge Triples in JSON: (Subject, Relation, Object, Score). Text: {text_snippet}"
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except Exception as e:
            if "503" in str(e):
                time.sleep((attempt + 1) * 10)
            else:
                break
    return []

if __name__ == "__main__":
    try:
        df = pd.read_csv('political_news_scraped.csv')
        final_triples_list = []

        print("Starting grouped analysis...")
        
        # We loop with 'enumerate' to create an ID for each article
        for index, row in df.head(25).iterrows():
            article_id = f"ART_{index + 1:03d}" # Creates IDs like ART_001, ART_002
            print(f"Analyzing {article_id}: {row['title'][:40]}...")
            
            triples = get_triples(str(row['text'])[:1500])
            
            if triples:
                for t in triples:
                    # ADDING THE GROUPING COLUMNS HERE
                    t['article_id'] = article_id  # This keeps them grouped
                    t['headline'] = row['title']
                    final_triples_list.append(t)
            
            time.sleep(5)

        if final_triples_list:
            output_df = pd.DataFrame(final_triples_list)
            
            # REORDER COLUMNS: Put the ID first so it's easy to see in Excel
            cols = ['article_id', 'sub', 'rel', 'obj', 'score', 'headline']
            existing_cols = [c for c in cols if c in output_df.columns]
            extra_cols = [c for c in output_df.columns if c not in cols]
            output_df = output_df[existing_cols + extra_cols]
            
            output_df.to_csv('political_triples_grouped.csv', index=False)
            print(f"\nSUCCESS! Grouped file saved as 'political_triples_grouped.csv'")
            
    except FileNotFoundError:
        print("Error: 'political_news_scraped.csv' not found!")