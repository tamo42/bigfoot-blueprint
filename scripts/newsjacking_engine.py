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

def run_editor_prompt(text: str, niche_profile: dict) -> EditorScore:
    """Passes the article and avatar to Gemini Flash for cheap scoring."""
    prompt = f"""
    You are the Senior Editor for a business directory serving this niche:
    Niche Name: {niche_profile['name']}
    Target Avatar: {niche_profile['avatar']}
    Tone: {niche_profile['tone']}
    
    Review the following news article text and score it on a scale of 1-10 for Site Relevance, User Relevance, and Importance.
    A good newsjacking opportunity connects a broad trend to the specific pain points of our Avatar.
    Calculate the total score. If the total score is 21 or higher, set status to 'APPROVED', otherwise 'REJECTED'.
    
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
    2. Write a compelling Title formatted as an H1 (`# `).
    3. Start with a hook summarizing the core news event briefly.
    4. Pivot immediately to the 'Newsjacking Angle': Why does the {niche_profile['avatar']} need to care about this right now? What are the implications?
    5. End with a subtle Call to Action encouraging them to use the {niche_profile['name']} evaluation tools or search for providers.
    
    Article Text:
    {text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Flash is extremely capable for this, but Pro can be used if needed.
        contents=prompt
    )
    return response.text

def main():
    print("🚀 Initializing Bigfoot Newsjacking Engine...")
    conn = init_db()
    cursor = conn.cursor()
    
    # 1. Load Configs
    with open("source/niche_profiles.json", "r") as f:
        profiles = json.load(f)
        
    for niche_id, profile in profiles.items():
        print(f"\n--- Processing Niche: {profile['name']} ---")
        
        for query in profile['queries']:
            print(f"\n🔍 Executing query: {query}")
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
                    print(f"⏭️ Skipping already processed article: {title}")
                    continue
                
                print(f"\n📰 Target: {title}")
                print(f"🔗 Decoding URL...")
                try:
                    decoded_result = new_decoderv1(google_url)
                    actual_url = decoded_result.get("decoded_url")
                except Exception as e:
                    print(f"❌ Failed to decode URL: {e}")
                    continue
                    
                if not actual_url:
                    print("❌ Decoder returned None for actual URL.")
                    continue
                    
                print(f"📝 Extracting text from: {actual_url}")
                downloaded = trafilatura.fetch_url(actual_url)
                if not downloaded:
                    print("❌ Failed to download HTML (possible bot block).")
                    continue
                    
                full_text = trafilatura.extract(downloaded)
                if not full_text:
                    print("❌ Failed to extract text (likely paywall/JS barrier).")
                    continue
                    
                print(f"✅ Text extracted ({len(full_text)} characters). Sending to LLM Editor for scoring...")
                
                try:
                    # Step 3: Editor Scoring
                    score_json = run_editor_prompt(full_text, profile)
                    
                    status = score_json.get("status", "REJECTED")
                    total_score = score_json.get("total_score", 0)
                    print(f"🧠 Editor Score: {total_score}/30 -> {status}")
                    print(f"   Reasoning: {score_json.get('reasoning')}")
                    
                    generated_markdown = ""
                    
                    # Step 4: Journalist Generation
                    if status == "APPROVED":
                        print(f"✍️ Article approved! Sending to LLM Journalist...")
                        generated_markdown = run_journalist_prompt(full_text, profile, score_json.get("reasoning"))
                        print("✅ Generation complete!")
                        
                    # Save to DB
                    cursor.execute("""
                        INSERT INTO articles (niche_id, original_title, original_url, status, editor_score_json, generated_markdown)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (niche_id, title, google_url, status, json.dumps(score_json), generated_markdown))
                    conn.commit()
                    print("💾 Saved to content_queue.db")
                    
                except Exception as e:
                    print(f"❌ Error during LLM processing: {e}")
                    
    print("\n🎉 Newsjacking Engine Run Complete!")

if __name__ == "__main__":
    main()
