import spacy
import pandas as pd

nlp = spacy.load("en_core_web_trf")

df = pd.read_csv('political_news_scraped.csv')

all_entities = []

print("Starting Entity Extraction...")

for index, row in df.iterrows():
    doc = nlp(row['text'])

    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            all_entities.append({'entity':ent.text, 'type':ent.label_,'article_title':row['title']})
entity_df = pd.DataFrame(all_entities)
top_entities = entity_df['entity'].value_counts().head(10)

print("\n Top 10 Entities : ")
print(top_entities)

entity_df.to_csv('extracted_entities.csv', index = False)