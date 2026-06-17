import os
import json
import sqlite3
import urllib.parse
from datetime import datetime, timezone
import feedparser
from googlenewsdecoder import new_decoderv1
import trafilatura
from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini Client
client = genai.Client() # Uses GEMINI_API_KEY from environment

# Database setup
DB_PATH = os.path.join("cache", "content_queue.db")

def init_db():
    os.makedirs("cache", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche_id TEXT,
            original_title TEXT,
            original_url TEXT,
            status TEXT,
            editor_score_json TEXT,
            generated_markdown TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

# Define the Pydantic schema for the Editor output
class EditorScore(BaseModel):
    site_relevance: int = Field(description="Score 1-10: How directly does this tie into the services provided by the niche?")
    user_relevance: int = Field(description="Score 1-10: How much does the target audience (avatar) care about this?")
    importance: int = Field(description="Score 1-10: Is this breaking regulatory news, a major market shift, or just fluff?")
    total_score: int = Field(description="The sum of the three scores.")
    reasoning: str = Field(description="A 1-2 sentence explanation of the scoring and the potential newsjacking angle.")
    status: str = Field(description="Must be 'APPROVED' if total_score >= 21, otherwise 'REJECTED'.")

class NicheMatch(BaseModel):
    headline_title: str = Field(description="The exact headline title of the article.")
    original_url: str = Field(description="The original Google News link.")
    niche_id: str = Field(description="The niche ID this story matches (e.g. gaclosinglawyers, georgiagreasetrap, hvaccommercialhub, waterwelldrillers).")
    angle: str = Field(description="A 1-2 sentence explanation of the newsjacking angle for this specific niche.")
    source: str = Field(description="The publisher/source of the article.")

class TriageResult(BaseModel):
    matches: list[NicheMatch] = Field(description="List of all approved matches between articles and niches.")

TOPIC_FEEDS = {
    "NATION": "https://news.google.com/rss/sections/CAAqIggKIhRDQkFTRVFvSUwyMHZNRFZzTVdpeExuUnZkR2x2ZXdJUFArR0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "BUSINESS": "https://news.google.com/rss/sections/CAAqIggKIhRDQkFTRVFvSUwyMHZNRGx6TVd4ekxuUnZkR2x2ZXdJUFArR0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "TECHNOLOGY": "https://news.google.com/rss/sections/CAAqIggKIhRDQkFTRVFvSUwyMHZNRGRqTVdZeExuUnZkR2x2ZXdJUFArR0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "SCIENCE": "https://news.google.com/rss/sections/CAAqIggKIhRDQkFTRVFvSUwyMHZNRFp0TVRZeExuUnZkR2x2ZXdJUFArR0FQAQ?hl=en-US&gl=US&ceid=US:en"
}

def fetch_general_headlines() -> list:
    """Fetches the top entries from general topics feeds and de-duplicates them."""
    seen_links = set()
    articles = []
    
    for topic, url in TOPIC_FEEDS.items():
        print(f"Fetching RSS feed for topic: {topic}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                if entry.link not in seen_links:
                    seen_links.add(entry.link)
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "source": getattr(entry, 'source', {}).get('title', 'Google News')
                    })
        except Exception as e:
            print(f"[ERROR] Failed to fetch general topic {topic}: {e}")
            
    print(f"Fetched {len(articles)} unique macro headlines.")
    return articles

def run_triage_prompt(headlines: list, profiles: dict) -> TriageResult:
    """Passes the top macro headlines and all active profiles to Gemini to find matches."""
    headlines_str = ""
    for idx, item in enumerate(headlines):
        headlines_str += f"{idx}. Title: {item['title']}\n   Link: {item['link']}\n   Source: {item['source']}\n\n"
        
    profiles_str = ""
    for niche_id, p in profiles.items():
        profiles_str += f"Niche ID: {niche_id}\nName: {p['name']}\nAvatar: {p['avatar']}\nTone: {p['tone']}\n\n"
        
    prompt = f"""
    You are an editorial director managing multiple niche business directories.
    
    Here are the active directories and their target audiences (avatars):
    {profiles_str}
    
    Here are the top national and business headlines of the day:
    {headlines_str}
    
    Identify any news stories that present a strong, relevant newsjacking opportunity for ANY of the niches.
    A story is a match if it directly impacts the avatar or offers a major lesson/angle they care about.
    
    Return a structured JSON list of matches containing the exact title, the link, the matching niche ID, and a 1-sentence newsjacking angle.
    If no headlines are relevant to any niche, return an empty matches list.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": TriageResult,
        },
    )
    data = json.loads(response.text)
    return data

def run_editor_prompt(text: str, niche_profile: dict, recent_titles: list) -> EditorScore:
    """Passes the article and avatar to Gemini Flash for cheap scoring."""
    recent_titles_str = "\n".join([f"- {t}" for t in recent_titles]) if recent_titles else "None"
    
    prompt = f"""
    You are the Senior Editor for a business directory serving this niche:
    Niche Name: {niche_profile['name']}
    Target Avatar: {niche_profile['avatar']}
    Tone: {niche_profile['tone']}
    
    Recently Approved Articles:
    {recent_titles_str}
    
    Review the following news article text and score it on a scale of 1-10 for Site Relevance, User Relevance, and Importance.
    A good newsjacking opportunity connects a broad trend to the specific pain points of our Avatar.
    Calculate the total score. If the total score is 21 or higher, set status to 'APPROVED', otherwise 'REJECTED'.
    
    CRITICAL DEDUPLICATION RULE: If the core event of this article is the EXACT SAME EVENT covered in any of the 'Recently Approved Articles' listed above, you MUST set status to 'REJECTED' and explain that it is a 'DUPLICATE SUBJECT' in your reasoning.
    
    Article Text:
    {text[:5000]} # Truncate to save tokens, the first 5000 chars are enough for scoring
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": EditorScore,
        },
    )
    # The SDK automatically handles structured output parsing via Pydantic if we used a schema.
    # Wait, the response.parsed attribute is populated if we pass response_schema.
    # Let's just parse the JSON text directly to be safe, or use response.text.
    data = json.loads(response.text)
    return data

def run_journalist_prompt(text: str, niche_profile: dict, editor_reasoning: str) -> str:
    """Passes the approved article to Gemini Pro/Flash to write the blog post."""
    prompt = f"""
    You are an expert copywriter for a directory serving:
    Niche Name: {niche_profile['name']}
    Target Avatar: {niche_profile['avatar']}
    Editorial Tone: {niche_profile['tone']}
    
    The Senior Editor approved this article with the following angle: "{editor_reasoning}"
    
    Write a high-converting, 400-600 word newsjacking blog post formatted in Markdown.
    
    Requirements:
    1. Do NOT include an introduction like "Here is your blog post." Start directly with the Markdown.
    2. Write a compelling Title formatted as an H1 (`# `) after the frontmatter.
    3. Output valid YAML frontmatter at the very top of the file exactly like this:
---
title: "YOUR COMPELLING TITLE"
pubDate: 2026-06-16T12:00:00Z
author: "Industry Analyst"
summary: "YOUR ONE SENTENCE SUMMARY"
---
    4. Start with a hook summarizing the core news event briefly.
    5. Pivot immediately to the 'Newsjacking Angle': Why does the {niche_profile['avatar']} need to care about this right now? What are the implications?
    6. End with a subtle Call to Action encouraging them to use the {niche_profile['name']} evaluation tools or search for providers.
    
    Article Text:
    {text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Flash is extremely capable for this, but Pro can be used if needed.
        contents=prompt
    )
    return response.text

def main():
    print("[START] Initializing Bigfoot Newsjacking Engine...")
    conn = init_db()
    cursor = conn.cursor()
    
    # 1. Load Configs
    with open("source/niche_profiles.json", "r") as f:
        profiles = json.load(f)
        
    for niche_id, profile in profiles.items():
        print(f"\n--- Processing Niche: {profile['name']} ---")
        
        # Fetch recent approved titles for deduplication memory
        cursor.execute("SELECT original_title FROM articles WHERE niche_id = ? AND status = 'APPROVED' ORDER BY id DESC LIMIT 10", (niche_id,))
        recent_titles = [row[0] for row in cursor.fetchall()]
        
        for query in profile['queries']:
            print(f"\n[QUERY] Executing query: {query}")
            encoded_query = urllib.parse.quote(query + " when:1d")
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(rss_url)
            print(f"Found {len(feed.entries)} recent articles.")
            
            # Limit to top 3 to avoid long execution times during testing
            for entry in feed.entries[:3]:
                title = entry.title
                google_url = entry.link
                
                # Check if already processed
                cursor.execute("SELECT id FROM articles WHERE original_url = ?", (google_url,))
                if cursor.fetchone():
                    print(f"[SKIP] Skipping already processed article: {title}")
                    continue
                
                print(f"\n[ARTICLE] Target: {title}")
                print(f"[DECODE] Decoding URL...")
                try:
                    decoded_result = new_decoderv1(google_url)
                    actual_url = decoded_result.get("decoded_url")
                except Exception as e:
                    print(f"[ERROR] Failed to decode URL: {e}")
                    continue
                    
                if not actual_url:
                    print("[ERROR] Decoder returned None for actual URL.")
                    continue
                    
                print(f"[EXTRACT] Extracting text from: {actual_url}")
                downloaded = trafilatura.fetch_url(actual_url)
                if not downloaded:
                    print("[ERROR] Failed to download HTML (possible bot block).")
                    continue
                    
                full_text = trafilatura.extract(downloaded)
                if not full_text:
                    print("[ERROR] Failed to extract text (likely paywall/JS barrier).")
                    continue
                    
                print(f"[SUCCESS] Text extracted ({len(full_text)} characters). Sending to LLM Editor for scoring...")
                
                try:
                    # Step 3: Editor Scoring
                    score_json = run_editor_prompt(full_text, profile, recent_titles)
                    
                    status = score_json.get("status", "REJECTED")
                    total_score = score_json.get("total_score", 0)
                    print(f"[SCORE] Editor Score: {total_score}/30 -> {status}")
                    print(f"   Reasoning: {score_json.get('reasoning')}")
                    
                    generated_markdown = ""
                    
                    # Step 4: Journalist Generation
                    if status == "APPROVED":
                        print(f"[APPROVED] Article approved! Sending to LLM Journalist...")
                        recent_titles.append(title) # Update memory to prevent dupes in the same run
                        source_name = getattr(entry, 'source', {}).get('title', 'Google News Source')
                        generated_markdown = run_journalist_prompt(full_text, profile, score_json.get("reasoning"))
                        
                        # Append the source citation data into the frontmatter securely via string manipulation
                        if "---" in generated_markdown:
                            parts = generated_markdown.split("---", 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1].strip()
                                frontmatter += f'\nsourceUrl: "{actual_url}"\nsourceName: "{source_name}"\n'
                                generated_markdown = f"---\n{frontmatter}\n---{parts[2]}"
                        
                        print("[SUCCESS] Generation complete!")
                        
                    # Save to DB
                    cursor.execute("""
                        INSERT INTO articles (niche_id, original_title, original_url, status, editor_score_json, generated_markdown)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (niche_id, title, google_url, status, json.dumps(score_json), generated_markdown))
                    conn.commit()
                    print("[SAVE] Saved to content_queue.db")
                    
                except Exception as e:
                    print(f"[ERROR] Error during LLM processing: {e}")

    # === START PRONG B: MACRO SYNTHESIZER ===
    print("\n" + "="*50)
    print("=== STARTING PRONG B: MACRO SYNTHESIZER ===")
    print("="*50)
    
    general_headlines = fetch_general_headlines()
    if general_headlines:
        print("\nRunning Triage Matrix on macro headlines...")
        try:
            triage_res = run_triage_prompt(general_headlines, profiles)
            matches = triage_res.get("matches", [])
            print(f"Triage Matrix found {len(matches)} potential newsjacking matches.")
            
            for match in matches:
                niche_id = match.get("niche_id")
                title = match.get("headline_title")
                google_url = match.get("original_url")
                proposed_angle = match.get("angle")
                source_name = match.get("source", "Google News")
                
                if niche_id not in profiles:
                    print(f"⏭️ Skipping match for unknown niche ID: {niche_id}")
                    continue
                    
                profile = profiles[niche_id]
                
                # Fetch recent approved titles for deduplication memory
                cursor.execute("SELECT original_title FROM articles WHERE niche_id = ? AND status = 'APPROVED' ORDER BY id DESC LIMIT 10", (niche_id,))
                recent_titles = [row[0] for row in cursor.fetchall()]
                
                # Check if already processed
                cursor.execute("SELECT id FROM articles WHERE original_url = ?", (google_url,))
                if cursor.fetchone():
                    print(f"⏭️ Skipping already processed article: {title}")
                    continue
                    
                print(f"\n[MACRO MATCH] Niche: {profile['name']} | Headline: {title}")
                print(f"[DECODE] Decoding URL...")
                try:
                    decoded_result = new_decoderv1(google_url)
                    actual_url = decoded_result.get("decoded_url")
                except Exception as e:
                    print(f"[ERROR] Failed to decode URL: {e}")
                    continue
                    
                if not actual_url:
                    print("[ERROR] Decoder returned None for actual URL.")
                    continue
                    
                print(f"[EXTRACT] Extracting text from: {actual_url}")
                downloaded = trafilatura.fetch_url(actual_url)
                if not downloaded:
                    print("[ERROR] Failed to download HTML (possible bot block).")
                    continue
                    
                full_text = trafilatura.extract(downloaded)
                if not full_text:
                    print("[ERROR] Failed to extract text (likely paywall/JS barrier).")
                    continue
                    
                print(f"[SUCCESS] Text extracted. Running LLM Editor for detailed score...")
                try:
                    score_json = run_editor_prompt(full_text, profile, recent_titles)
                    status = score_json.get("status", "REJECTED")
                    total_score = score_json.get("total_score", 0)
                    print(f"[SCORE] Editor Score: {total_score}/30 -> {status}")
                    print(f"   Reasoning: {score_json.get('reasoning')}")
                    
                    generated_markdown = ""
                    if status == "APPROVED":
                        print(f"[APPROVED] Article approved! Sending to LLM Journalist with angle: {proposed_angle}")
                        generated_markdown = run_journalist_prompt(full_text, profile, score_json.get("reasoning"))
                        
                        if "---" in generated_markdown:
                            parts = generated_markdown.split("---", 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1].strip()
                                frontmatter += f'\nsourceUrl: "{actual_url}"\nsourceName: "{source_name}"\n'
                                generated_markdown = f"---\n{frontmatter}\n---{parts[2]}"
                        print("[SUCCESS] Generation complete!")
                        
                    # Save to DB
                    cursor.execute("""
                        INSERT INTO articles (niche_id, original_title, original_url, status, editor_score_json, generated_markdown)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (niche_id, title, google_url, status, json.dumps(score_json), generated_markdown))
                    conn.commit()
                    print("[SAVE] Saved to content_queue.db")
                except Exception as e:
                    print(f"[ERROR] Error during LLM processing of macro match: {e}")
        except Exception as e:
            print(f"[ERROR] Error running Triage Matrix: {e}")
            
    print("\n[COMPLETE] Newsjacking Engine Run Complete!")

if __name__ == "__main__":
    main()
