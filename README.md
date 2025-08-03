# The Ember Scriptorium v1

**An automated social media content engine for the literary novel "We Burned, Quietly"**

## 🔥 Overview

The Ember Scriptorium v1 is a sophisticated web application designed to generate Instagram and TikTok content from a pre-tagged Quote Bank. Built with a stunning dark academia aesthetic, it creates AI-generated images and captions that capture the gothic literary atmosphere of the novel.

## ✨ Features

### Core Functionality
- **Quote Bank Management**: Upload and manage quotes from CSV/JSON files
- **AI Image Generation**: DALL-E creates oil painting, dark academia styled images
- **Caption Generation**: ChatGPT writes poetic captions in the novel's tone
- **Approval Workflow**: Web-based review and approval system
- **Smart Quote Selection**: Avoids repeats within 14-day periods
- **Export System**: Download approved posts for manual publishing

### Design
- Beautiful dark academia aesthetic with parchment tones
- Serif typography (EB Garamond, Playfair Display)
- Candlelight gold accents and subtle shadows
- Fully responsive design
- Professional sidebar navigation

## 🚀 Quick Start

### 1. Access the Application
Visit: https://6fdc1bd5-6f98-4b4f-9645-e88780e02f59.preview.emergentagent.com

### 2. Upload Your Quote Bank
1. Click **Quote Bank** in the sidebar
2. Use the **Upload** button to select your CSV or JSON file
3. Required columns: `quote`, `theme`, `tone`, `length`, `visual_keywords`

**Sample Format (CSV):**
```csv
quote,theme,tone,length,visual_keywords
"Silence. It is the first word I remember, and the last.",Silence & Isolation,Poetic,Short,"silence, stillness, cold"
"The Sun was not warmth—it was fire. And fire did not love.",Doctrine & Control,Ominous,Short,"sun, fire, danger"
```

### 3. Configure API Keys
1. Click **Settings** in the sidebar
2. Enter your **OpenAI API Key** (required for generation)
3. Instagram/TikTok API keys (coming in future versions)

### 4. Generate Content
1. Click **Generate Post** in the sidebar
2. The system will:
   - Select a random quote (avoiding 14-day repeats)
   - Generate a DALL-E image in dark academia style
   - Create a poetic caption with hashtags
   - Add text overlay with literary serif font

### 5. Review & Approve
1. Check **Approval Queue** to review generated posts
2. Use **Approve** to accept content
3. Use **Regenerate** to create new versions
4. Download approved posts from **Approved Posts**

## 📊 Quote Bank Structure

Your quote bank should include these fields:

- **quote**: The actual quote text
- **theme**: Content theme (e.g., "Love & Connection", "Defiance & Power")
- **tone**: Emotional tone (e.g., "Poetic", "Melancholic", "Resolute")
- **length**: Quote length (e.g., "Short", "Medium", "Long")
- **visual_keywords**: Comma-separated keywords for image generation

## 🎨 AI Generation Details

### Image Generation (DALL-E)
- **Style Prompt**: "Oil painting, dark academia aesthetic — {visual keywords} — moody cinematic lighting, poetic atmosphere, muted earth tones, candlelight gold, deep shadows"
- **Text Overlay**: Literary serif font with "— We Burned, Quietly" attribution
- **Size**: 1024x1024px, optimized for social media

### Caption Generation (ChatGPT)
- **Style**: Poetic, cinematic, restrained, dark academia, gothic literary
- **Structure**: 2-4 sentences ending with reflective question
- **Call-to-Action**: Rotates between "Follow for more fragments of the Order" or "Join the newsletter for deeper pages of the Pocket Guide"
- **Hashtags**: 5-7 relevant dark academia and gothic literature tags

## 🔧 Technical Details

### Architecture
- **Frontend**: React with Tailwind CSS and shadcn/ui components
- **Backend**: FastAPI with MongoDB storage
- **AI Integration**: OpenAI GPT-4 and DALL-E 3
- **Image Processing**: PIL for text overlay
- **Security**: Encrypted API key storage

### API Endpoints
- `GET /api/quotes` - Fetch quotes
- `POST /api/quotes/upload` - Upload quote bank
- `POST /api/posts/generate` - Generate new post
- `GET /api/posts/queue` - Get approval queue
- `POST /api/posts/approve/{id}` - Approve post
- `GET /api/posts/download/{id}` - Download post

## 📱 Future Features (Coming Soon)

### Social Media Integration
- **Instagram Graph API**: Direct posting to Instagram
- **TikTok API**: Automated TikTok content creation
- **Scheduling**: Optimal posting time recommendations

### Enhanced Features
- **Video Generation**: Ken Burns effect for Instagram Reels
- **Email Notifications**: Approval workflow via email
- **Analytics**: Post performance tracking
- **Templates**: Multiple visual styles

## 🎯 Usage Tips

### Quote Selection Strategy
- The system tracks usage and avoids repeating quotes within 14 days
- Larger quote banks provide more variety
- Mix different themes and tones for diverse content

### Image Generation
- Visual keywords significantly impact image quality
- Use atmospheric descriptors: "candlelight", "shadows", "stone"
- Architectural elements work well: "temple", "cathedral", "arches"

### Caption Optimization
- Generated captions maintain the novel's voice
- Reflective questions encourage engagement
- Hashtags target dark academia and gothic literature audiences

## 🔑 API Key Setup

### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Create a new secret key
3. Enter in Settings panel
4. Ensure sufficient credits for DALL-E and GPT-4 usage

### Costs (Approximate)
- **DALL-E 3**: $0.040 per 1024x1024 image
- **GPT-4**: ~$0.001 per caption
- **Daily Budget**: ~$0.05 per post (image + caption)

## 🎨 Brand Guidelines

### Visual Style
- **Color Palette**: Parchment tones, ember gold, deep shadows
- **Typography**: EB Garamond (serif), Playfair Display (headers)
- **Imagery**: Oil painting style, dark academia aesthetic
- **Mood**: Sophisticated, gothic, literary, atmospheric

### Voice & Tone
- **Style**: Poetic, cinematic, restrained
- **Vocabulary**: Sophisticated, literary, atmospheric
- **Structure**: Thoughtful, contemplative, evocative
- **Engagement**: Reflective questions, literary call-to-actions

## 🛠️ Troubleshooting

### Common Issues
1. **"OpenAI API key not configured"**: Add your API key in Settings
2. **"No quotes available"**: Upload quotes in Quote Bank
3. **Generation fails**: Check API key credits and connectivity
4. **Slow generation**: DALL-E processing can take 10-30 seconds

### Support
- Check browser console for error messages
- Verify API key has sufficient credits
- Ensure quote bank is properly formatted
- Contact support for integration issues

---

**The Ember Scriptorium v1** - Where literature meets social media automation.

*Built for "We Burned, Quietly" - A gothic tale of love, rebellion, and the courage to remember.*
