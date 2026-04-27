import time
import re
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key= os.getenv('api_key'))
MAX_RETRY = 3

def build_prompt(content: str) -> str:
    return f"""
            You are a data labeling system.

            Classify the following Vietnamese news article into:

            Sentiment:
            - Positive: good news, success, growth
            - Negative: accidents, crisis, corruption
            - Neutral: factual reporting

            Intent:
            - Informational: just reporting
            - Warning: risk, danger, alert
            - Promotional: advertising, promotion

            Return ONLY a JSON object:
            {{
            "sentiment": "...",
            "intent": "..."
            }}

            No explanation. No markdown. No extra text.

            Article:
            {content}
            """
            
def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        return None
    return None

def call_llm(content: str):
    prompt = build_prompt(content[:1000])

    for attempt in range(MAX_RETRY):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            text = response.choices[0].message.content
            parsed = extract_json(text)

            if parsed and \
            parsed.get("sentiment") in ["Positive", "Negative", "Neutral"] and \
            parsed.get("intent") in ["Informational", "Warning", "Promotional"]:
                return parsed

        except Exception as e:
            print(f"LLM error (attempt {attempt+1}): {e}")

        time.sleep(2 ** attempt)  
    return {
        "sentiment": "Neutral",
        "intent": "Informational"
    }
    
def label_batch(articles: list):
    results = []
    fallback_count = 0
    for article in articles:
        result = call_llm(article["content"])
        
        if result["sentiment"] == "Neutral" and result["intent"] == "Informational":
            fallback_count += 1
                
        results.append({
            "article_id": article["id"],
            "sentiment": result["sentiment"],
            "intent": result["intent"]
        })
        
    print(f"Tổng bài: {len(articles)}")
    print(f"Fallback: {fallback_count} ({fallback_count/len(articles)*100:.2f}%)")
    return results