from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pymongo
import os
import json
import csv
import io
import uuid
import zipfile
import tempfile
from datetime import datetime, timedelta
import random
import openai
from PIL import Image, ImageDraw, ImageFont
import requests
import base64
from cryptography.fernet import Fernet
import asyncio

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ember_scriptorium')

client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
quotes_collection = db.quotes
posts_collection = db.generated_posts
settings_collection = db.settings

# Encryption key for API keys
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

# Pydantic Models
class Quote(BaseModel):
    id: Optional[str] = None
    quote: str
    theme: str
    tone: str
    length: str
    visual_keywords: str
    last_used: Optional[datetime] = None
    times_used: int = 0

class GeneratedPost(BaseModel):
    id: Optional[str] = None
    quote_id: str
    quote_text: str
    theme: str
    tone: str
    visual_keywords: str
    image_url: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded image
    caption: str
    hashtags: List[str] = []
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime
    approved_at: Optional[datetime] = None

class SettingsUpdate(BaseModel):
    openai_api_key: Optional[str] = None
    instagram_app_id: Optional[str] = None
    instagram_app_secret: Optional[str] = None
    instagram_access_token: Optional[str] = None
    tiktok_access_token: Optional[str] = None

class QuoteUpload(BaseModel):
    quotes: List[Dict[str, Any]]

# Helper Functions
def encrypt_key(key: str) -> str:
    """Encrypt API key for storage"""
    return cipher_suite.encrypt(key.encode()).decode()

def decrypt_key(encrypted_key: str) -> str:
    """Decrypt API key for use"""
    return cipher_suite.decrypt(encrypted_key.encode()).decode()

def get_openai_client():
    """Get OpenAI client with API key from settings"""
    settings = settings_collection.find_one()
    if not settings or 'openai_api_key' not in settings:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    api_key = decrypt_key(settings['openai_api_key'])
    return openai.OpenAI(api_key=api_key)

def select_random_quote():
    """Select a random quote avoiding 14-day repeats"""
    # Get cutoff date (14 days ago)
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    
    # Find quotes that haven't been used in 14 days or never used
    available_quotes = list(quotes_collection.find({
        "$or": [
            {"last_used": {"$lt": cutoff_date}},
            {"last_used": None}
        ]
    }))
    
    if not available_quotes:
        # If no quotes available, use the oldest used quote
        available_quotes = list(quotes_collection.find().sort("last_used", 1).limit(1))
    
    if not available_quotes:
        raise HTTPException(status_code=404, detail="No quotes available")
    
    # Select random quote
    selected_quote = random.choice(available_quotes)
    
    # Update usage tracking
    quotes_collection.update_one(
        {"_id": selected_quote["_id"]},
        {
            "$set": {"last_used": datetime.utcnow()},
            "$inc": {"times_used": 1}
        }
    )
    
    return selected_quote

async def generate_dalle_image(quote_text: str, visual_keywords: str) -> str:
    """Generate image using DALL-E"""
    client = get_openai_client()
    
    # Structured prompt for dark academia oil painting style
    prompt = f"Oil painting, dark academia aesthetic — {visual_keywords} — moody cinematic lighting, poetic atmosphere, muted earth tones, candlelight gold, deep shadows — inspired by the quote: '{quote_text}'. Classical painting style, romantic period, atmospheric depth."
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download and convert to base64
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        # Process image and add text overlay
        image_with_text = add_text_overlay(img_response.content, quote_text)
        
        # Convert to base64
        img_buffer = io.BytesIO()
        image_with_text.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return img_base64
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

def add_text_overlay(image_data: bytes, quote_text: str) -> Image.Image:
    """Add text overlay to image with literary styling"""
    # Open the image
    img = Image.open(io.BytesIO(image_data))
    draw = ImageDraw.Draw(img)
    
    # Image dimensions
    img_width, img_height = img.size
    
    # Try to use a serif font, fallback to default
    try:
        # Try to use a serif font
        font_size = max(24, min(48, img_width // 20))
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", font_size)
    except:
        font_size = max(20, min(40, img_width // 25))
        font = ImageFont.load_default()
    
    # Prepare quote text with attribution
    full_text = f'"{quote_text}"\n\n— We Burned, Quietly'
    
    # Calculate text dimensions and position
    max_width = int(img_width * 0.8)  # 80% of image width
    
    # Wrap text
    lines = []
    words = full_text.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate total text height
    line_height = font.getbbox('A')[3] - font.getbbox('A')[1] + 10
    total_text_height = len(lines) * line_height
    
    # Position text in bottom third of image
    start_y = img_height - total_text_height - 100
    
    # Draw semi-transparent background box
    padding = 30
    box_left = img_width // 2 - max_width // 2 - padding
    box_top = start_y - padding
    box_right = img_width // 2 + max_width // 2 + padding
    box_bottom = start_y + total_text_height + padding
    
    # Create overlay for text background
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([box_left, box_top, box_right, box_bottom], 
                         fill=(0, 0, 0, 120))  # Semi-transparent black
    
    # Composite overlay onto image
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Draw text lines
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = img_width // 2 - text_width // 2
        y = start_y + i * line_height
        
        # Draw text shadow
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 100))
        # Draw main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
    
    return img

async def generate_caption(quote_text: str, theme: str, tone: str) -> Dict[str, Any]:
    """Generate caption using ChatGPT"""
    client = get_openai_client()
    
    # Call-to-action options
    cta_options = [
        "Follow for more fragments of the Order",
        "Join the newsletter for deeper pages of the Pocket Guide"
    ]
    cta = random.choice(cta_options)
    
    prompt = f"""Write a poetic social media caption in the style of 'We Burned, Quietly', inspired by the quote: '{quote_text}'.

Tone: {tone}
Theme: {theme}
Length: 2-4 sentences
Requirements:
- End with a reflective question
- Include call-to-action: '{cta}'
- Add 5-7 hashtags relevant to dark academia & gothic literature
- Maintain the poetic, cinematic, restrained tone of the novel
- Use sophisticated vocabulary and imagery

Format:
[Caption text with reflective question]

{cta}

[hashtags]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a literary social media manager creating content for the gothic novel 'We Burned, Quietly'. Write in a poetic, dark academia style with sophisticated language and atmospheric imagery."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.8
        )
        
        caption_text = response.choices[0].message.content.strip()
        
        # Extract hashtags (simple regex or split approach)
        hashtags = []
        lines = caption_text.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                hashtags.extend([tag.strip() for tag in line.split() if tag.startswith('#')])
        
        # Remove hashtag lines from caption
        caption_clean = '\n'.join([line for line in lines if not line.strip().startswith('#')])
        
        return {
            "caption": caption_clean.strip(),
            "hashtags": hashtags,
            "full_text": caption_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "The Ember Scriptorium v1 API"}

@app.post("/api/quotes/upload")
async def upload_quotes(upload_data: QuoteUpload):
    """Upload quotes from CSV/JSON data"""
    try:
        # Clear existing quotes
        quotes_collection.delete_many({})
        
        # Insert new quotes
        for quote_data in upload_data.quotes:
            quote_obj = {
                "_id": str(uuid.uuid4()),
                "quote": quote_data.get("quote", ""),
                "theme": quote_data.get("theme", ""),
                "tone": quote_data.get("tone", ""),
                "length": quote_data.get("length", ""),
                "visual_keywords": quote_data.get("visual_keywords", ""),
                "last_used": None,
                "times_used": 0
            }
            quotes_collection.insert_one(quote_obj)
        
        return {"message": f"Successfully uploaded {len(upload_data.quotes)} quotes"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/quotes")
async def get_quotes(skip: int = 0, limit: int = 50):
    """Get quotes with pagination"""
    try:
        quotes = list(quotes_collection.find().skip(skip).limit(limit))
        for quote in quotes:
            quote["id"] = quote["_id"]
            del quote["_id"]
        
        total = quotes_collection.count_documents({})
        
        return {
            "quotes": quotes,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quotes: {str(e)}")

@app.post("/api/posts/generate")
async def generate_post():
    """Generate a new post with image and caption"""
    try:
        # Select random quote
        selected_quote = select_random_quote()
        
        # Generate image
        image_data = await generate_dalle_image(
            selected_quote["quote"], 
            selected_quote["visual_keywords"]
        )
        
        # Generate caption
        caption_data = await generate_caption(
            selected_quote["quote"],
            selected_quote["theme"],
            selected_quote["tone"]
        )
        
        # Create post record
        post_data = {
            "_id": str(uuid.uuid4()),
            "quote_id": selected_quote["_id"],
            "quote_text": selected_quote["quote"],
            "theme": selected_quote["theme"],
            "tone": selected_quote["tone"],
            "visual_keywords": selected_quote["visual_keywords"],
            "image_data": image_data,
            "caption": caption_data["caption"],
            "hashtags": caption_data["hashtags"],
            "full_caption": caption_data["full_text"],
            "status": "pending",
            "created_at": datetime.utcnow(),
            "approved_at": None
        }
        
        # Insert post
        posts_collection.insert_one(post_data)
        
        # Return post data
        post_data["id"] = post_data["_id"]
        del post_data["_id"]
        
        return post_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post generation failed: {str(e)}")

@app.get("/api/posts/queue")
async def get_approval_queue():
    """Get pending posts for approval"""
    try:
        posts = list(posts_collection.find({"status": "pending"}).sort("created_at", -1))
        
        for post in posts:
            post["id"] = post["_id"]
            del post["_id"]
        
        return {"posts": posts}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch queue: {str(e)}")

@app.get("/api/posts/approved")
async def get_approved_posts():
    """Get approved posts"""
    try:
        posts = list(posts_collection.find({"status": "approved"}).sort("approved_at", -1))
        
        for post in posts:
            post["id"] = post["_id"]
            del post["_id"]
        
        return {"posts": posts}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch approved posts: {str(e)}")

@app.post("/api/posts/approve/{post_id}")
async def approve_post(post_id: str):
    """Approve a post"""
    try:
        result = posts_collection.update_one(
            {"_id": post_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"message": "Post approved successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@app.post("/api/posts/regenerate/{post_id}")
async def regenerate_post(post_id: str):
    """Regenerate image and caption for a post"""
    try:
        # Get original post
        original_post = posts_collection.find_one({"_id": post_id})
        if not original_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Generate new image
        image_data = await generate_dalle_image(
            original_post["quote_text"], 
            original_post["visual_keywords"]
        )
        
        # Generate new caption
        caption_data = await generate_caption(
            original_post["quote_text"],
            original_post["theme"],
            original_post["tone"]
        )
        
        # Update post
        posts_collection.update_one(
            {"_id": post_id},
            {
                "$set": {
                    "image_data": image_data,
                    "caption": caption_data["caption"],
                    "hashtags": caption_data["hashtags"],
                    "full_caption": caption_data["full_text"],
                    "created_at": datetime.utcnow()
                }
            }
        )
        
        # Return updated post
        updated_post = posts_collection.find_one({"_id": post_id})
        updated_post["id"] = updated_post["_id"]
        del updated_post["_id"]
        
        return updated_post
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")

@app.get("/api/posts/download/{post_id}")
async def download_post(post_id: str):
    """Download approved post as a zip file"""
    try:
        post = posts_collection.find_one({"_id": post_id, "status": "approved"})
        if not post:
            raise HTTPException(status_code=404, detail="Approved post not found")
        
        # Create temporary zip file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"post_{post_id}.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Add image
            image_data = base64.b64decode(post["image_data"])
            zip_file.writestr(f"image_{post_id}.png", image_data)
            
            # Add caption
            caption_content = f"{post['full_caption']}\n\nGenerated: {post['created_at']}\nQuote: {post['quote_text']}"
            zip_file.writestr(f"caption_{post_id}.txt", caption_content)
        
        return FileResponse(
            zip_path, 
            media_type='application/zip', 
            filename=f"ember_post_{post_id}.zip"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.post("/api/settings")
async def update_settings(settings: SettingsUpdate):
    """Update API keys and settings"""
    try:
        update_data = {}
        
        if settings.openai_api_key:
            update_data["openai_api_key"] = encrypt_key(settings.openai_api_key)
        
        if settings.instagram_app_id:
            update_data["instagram_app_id"] = encrypt_key(settings.instagram_app_id)
        
        if settings.instagram_app_secret:
            update_data["instagram_app_secret"] = encrypt_key(settings.instagram_app_secret)
        
        if settings.instagram_access_token:
            update_data["instagram_access_token"] = encrypt_key(settings.instagram_access_token)
        
        if settings.tiktok_access_token:
            update_data["tiktok_access_token"] = encrypt_key(settings.tiktok_access_token)
        
        if update_data:
            settings_collection.update_one(
                {},
                {"$set": update_data},
                upsert=True
            )
        
        return {"message": "Settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings update failed: {str(e)}")

@app.get("/api/settings")
async def get_settings():
    """Get current settings (without decrypting keys)"""
    try:
        settings = settings_collection.find_one()
        if not settings:
            return {"configured": False}
        
        return {
            "configured": True,
            "has_openai_key": "openai_api_key" in settings,
            "has_instagram_credentials": all(key in settings for key in ["instagram_app_id", "instagram_app_secret", "instagram_access_token"]),
            "has_tiktok_credentials": "tiktok_access_token" in settings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)