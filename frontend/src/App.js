import React, { useState, useEffect } from 'react';
import './App.css';
import { Card } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Alert, AlertDescription } from './components/ui/alert';
import { 
  BookOpen, 
  Settings, 
  FileText, 
  Image as ImageIcon, 
  CheckCircle, 
  RefreshCw, 
  Download,
  Upload,
  Sun,
  Moon,
  Flame
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [posts, setPosts] = useState([]);
  const [approvedPosts, setApprovedPosts] = useState([]);
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({});
  const [newSettings, setNewSettings] = useState({});
  const [notification, setNotification] = useState('');

  // Fetch data
  const fetchPosts = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/posts/queue`);
      const data = await response.json();
      setPosts(data.posts || []);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    }
  };

  const fetchApprovedPosts = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/posts/approved`);
      const data = await response.json();
      setApprovedPosts(data.posts || []);
    } catch (error) {
      console.error('Failed to fetch approved posts:', error);
    }
  };

  const fetchQuotes = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/quotes`);
      const data = await response.json();
      setQuotes(data.quotes || []);
    } catch (error) {
      console.error('Failed to fetch quotes:', error);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/settings`);
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  useEffect(() => {
    fetchPosts();
    fetchApprovedPosts();
    fetchQuotes();
    fetchSettings();
  }, []);

  // Generate new post
  const generatePost = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/posts/generate`, {
        method: 'POST'
      });
      
      if (response.ok) {
        showNotification('Post generated successfully!');
        fetchPosts();
      } else {
        const error = await response.json();
        showNotification(`Generation failed: ${error.detail}`, 'error');
      }
    } catch (error) {
      showNotification('Generation failed. Please check your OpenAI API key.', 'error');
    }
    setLoading(false);
  };

  // Approve post
  const approvePost = async (postId) => {
    try {
      const response = await fetch(`${API_BASE}/api/posts/approve/${postId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        showNotification('Post approved!');
        fetchPosts();
        fetchApprovedPosts();
      }
    } catch (error) {
      showNotification('Approval failed', 'error');
    }
  };

  // Regenerate post
  const regeneratePost = async (postId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/posts/regenerate/${postId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        showNotification('Post regenerated!');
        fetchPosts();
      }
    } catch (error) {
      showNotification('Regeneration failed', 'error');
    }
    setLoading(false);
  };

  // Download post
  const downloadPost = async (postId) => {
    try {
      const response = await fetch(`${API_BASE}/api/posts/download/${postId}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ember_post_${postId}.zip`;
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Post downloaded!');
      }
    } catch (error) {
      showNotification('Download failed', 'error');
    }
  };

  // Upload quotes
  const uploadQuotes = async (file) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        let quotesData = [];
        
        if (file.name.endsWith('.json')) {
          quotesData = JSON.parse(e.target.result);
        } else if (file.name.endsWith('.csv')) {
          // Simple CSV parsing
          const lines = e.target.result.split('\n');
          const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
          
          for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) {
              const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
              const quote = {};
              headers.forEach((header, idx) => {
                quote[header.toLowerCase().replace(/\s+/g, '_')] = values[idx] || '';
              });
              quotesData.push(quote);
            }
          }
        }
        
        const response = await fetch(`${API_BASE}/api/quotes/upload`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ quotes: quotesData })
        });
        
        if (response.ok) {
          showNotification('Quotes uploaded successfully!');
          fetchQuotes();
        } else {
          showNotification('Upload failed', 'error');
        }
      } catch (error) {
        showNotification('File parsing failed', 'error');
      }
    };
    reader.readAsText(file);
  };

  // Update settings
  const updateSettings = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings)
      });
      
      if (response.ok) {
        showNotification('Settings updated successfully!');
        fetchSettings();
        setNewSettings({});
      } else {
        showNotification('Settings update failed', 'error');
      }
    } catch (error) {
      showNotification('Settings update failed', 'error');
    }
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(''), 5000);
  };

  const PostCard = ({ post, showActions = true }) => (
    <Card className="post-card mb-6 overflow-hidden">
      <div className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <div className="quote-symbol">
            <Flame className="w-5 h-5 text-ember-gold" />
          </div>
          <div className="flex-1">
            <blockquote className="text-lg font-serif italic text-parchment-dark mb-2">
              "{post.quote_text}"
            </blockquote>
            <div className="text-sm text-ember-muted mb-2">— We Burned, Quietly</div>
            <div className="flex gap-2 mb-4">
              <Badge variant="outline" className="text-xs">{post.theme}</Badge>
              <Badge variant="outline" className="text-xs">{post.tone}</Badge>
              <Badge variant="outline" className="text-xs">{post.length}</Badge>
            </div>
          </div>
        </div>
        
        {post.image_data && (
          <div className="mb-4 rounded-lg overflow-hidden shadow-lg">
            <img 
              src={`data:image/png;base64,${post.image_data}`} 
              alt="Generated artwork" 
              className="w-full h-auto"
            />
          </div>
        )}
        
        <div className="caption-preview bg-parchment-light p-4 rounded-lg mb-4">
          <div className="whitespace-pre-wrap font-serif text-sm text-parchment-dark">
            {post.full_caption || post.caption}
          </div>
        </div>
        
        {showActions && (
          <div className="flex gap-3 justify-end">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => regeneratePost(post.id)}
              disabled={loading}
              className="border-ember-gold text-ember-gold hover:bg-ember-gold hover:text-parchment-light"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Regenerate
            </Button>
            <Button 
              onClick={() => approvePost(post.id)}
              className="bg-ember-gold text-parchment-light hover:bg-ember-dark"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Approve
            </Button>
          </div>
        )}
        
        {!showActions && post.status === 'approved' && (
          <div className="flex justify-end">
            <Button 
              variant="outline"
              onClick={() => downloadPost(post.id)}
              className="border-ember-gold text-ember-gold hover:bg-ember-gold hover:text-parchment-light"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </div>
        )}
      </div>
    </Card>
  );

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <Sun className="w-8 h-8 text-ember-gold" />
            <h1 className="text-xl font-serif font-bold text-ember-gold">
              The Ember<br />Scriptorium
            </h1>
          </div>
          <div className="subtitle text-xs text-ember-muted">v1</div>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <Flame className="w-4 h-4" />
            Generate Post
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'queue' ? 'active' : ''}`}
            onClick={() => setActiveTab('queue')}
          >
            <ImageIcon className="w-4 h-4" />
            Approval Queue
            {posts.length > 0 && <Badge className="ml-auto">{posts.length}</Badge>}
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'approved' ? 'active' : ''}`}
            onClick={() => setActiveTab('approved')}
          >
            <CheckCircle className="w-4 h-4" />
            Approved Posts
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'quotes' ? 'active' : ''}`}
            onClick={() => setActiveTab('quotes')}
          >
            <BookOpen className="w-4 h-4" />
            Quote Bank
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {notification && (
          <Alert className={`notification ${notification.type === 'error' ? 'error' : 'success'}`}>
            <AlertDescription>{notification.message}</AlertDescription>
          </Alert>
        )}

        {/* Dashboard */}
        {activeTab === 'dashboard' && (
          <div className="content-section">
            <div className="section-header">
              <h2>Generate New Post</h2>
              <p>Create AI-generated content from your quote bank</p>
            </div>
            
            <Card className="p-8 text-center">
              <div className="mb-6">
                <Flame className="w-16 h-16 text-ember-gold mx-auto mb-4" />
                <h3 className="text-2xl font-serif mb-2">Ready to Create</h3>
                <p className="text-ember-muted mb-6">
                  Generate a new post with DALL-E imagery and ChatGPT caption
                </p>
              </div>
              
              <Button 
                onClick={generatePost} 
                disabled={loading || !settings.has_openai_key}
                size="lg"
                className="bg-ember-gold text-parchment-light hover:bg-ember-dark px-8 py-3"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Flame className="w-5 h-5 mr-2" />
                    Generate Post
                  </>
                )}
              </Button>
              
              {!settings.has_openai_key && (
                <p className="text-sm text-red-600 mt-4">
                  Configure OpenAI API key in Settings to generate posts
                </p>
              )}
            </Card>
          </div>
        )}

        {/* Approval Queue */}
        {activeTab === 'queue' && (
          <div className="content-section">
            <div className="section-header">
              <h2>Approval Queue</h2>
              <p>Review and approve generated posts</p>
            </div>
            
            {posts.length === 0 ? (
              <Card className="p-8 text-center">
                <ImageIcon className="w-16 h-16 text-ember-muted mx-auto mb-4" />
                <h3 className="text-xl font-serif mb-2">No Posts Pending</h3>
                <p className="text-ember-muted">Generate a new post to start reviewing</p>
              </Card>
            ) : (
              <div className="posts-grid">
                {posts.map(post => (
                  <PostCard key={post.id} post={post} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Approved Posts */}
        {activeTab === 'approved' && (
          <div className="content-section">
            <div className="section-header">
              <h2>Approved Posts</h2>
              <p>Download your approved content for posting</p>
            </div>
            
            {approvedPosts.length === 0 ? (
              <Card className="p-8 text-center">
                <CheckCircle className="w-16 h-16 text-ember-muted mx-auto mb-4" />
                <h3 className="text-xl font-serif mb-2">No Approved Posts</h3>
                <p className="text-ember-muted">Approve posts from the queue to see them here</p>
              </Card>
            ) : (
              <div className="posts-grid">
                {approvedPosts.map(post => (
                  <PostCard key={post.id} post={post} showActions={false} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quote Bank */}
        {activeTab === 'quotes' && (
          <div className="content-section">
            <div className="section-header">
              <h2>Quote Bank</h2>
              <p>Manage your collection of quotes</p>
            </div>
            
            <Card className="p-6 mb-6">
              <h3 className="text-lg font-serif mb-4">Upload Quotes</h3>
              <div className="flex gap-4">
                <Input 
                  type="file" 
                  accept=".csv,.json" 
                  onChange={(e) => {
                    if (e.target.files[0]) {
                      uploadQuotes(e.target.files[0]);
                    }
                  }}
                  className="flex-1"
                />
                <Button variant="outline">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload
                </Button>
              </div>
              <p className="text-sm text-ember-muted mt-2">
                Upload CSV or JSON with columns: quote, theme, tone, length, visual_keywords
              </p>
            </Card>
            
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-serif">Quote Collection</h3>
                <Badge variant="outline">{quotes.length} quotes</Badge>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {quotes.map((quote, index) => (
                  <div key={quote.id} className="border-b border-ember-light last:border-b-0 py-3">
                    <blockquote className="font-serif italic text-parchment-dark mb-2">
                      "{quote.quote}"
                    </blockquote>
                    <div className="flex gap-2 text-xs">
                      <Badge variant="outline">{quote.theme}</Badge>
                      <Badge variant="outline">{quote.tone}</Badge>
                      <Badge variant="outline">{quote.length}</Badge>
                    </div>
                    {quote.last_used && (
                      <p className="text-xs text-ember-muted mt-1">
                        Last used: {new Date(quote.last_used).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Settings */}
        {activeTab === 'settings' && (
          <div className="content-section">
            <div className="section-header">
              <h2>Settings</h2>
              <p>Configure API keys and integrations</p>
            </div>
            
            <div className="grid gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-serif mb-4 flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  API Configuration
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      OpenAI API Key *
                      {settings.has_openai_key && <Badge className="ml-2 text-xs">Configured</Badge>}
                    </label>
                    <Input
                      type="password"
                      placeholder="sk-..."
                      value={newSettings.openai_api_key || ''}
                      onChange={(e) => setNewSettings({...newSettings, openai_api_key: e.target.value})}
                    />
                    <p className="text-xs text-ember-muted mt-1">Required for image and caption generation</p>
                  </div>
                  
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-3 text-ember-muted">Instagram Integration (Coming Soon)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 opacity-50">
                      <div>
                        <label className="block text-sm font-medium mb-2">App ID</label>
                        <Input type="password" placeholder="Coming soon" disabled />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">App Secret</label>
                        <Input type="password" placeholder="Coming soon" disabled />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium mb-2">Access Token</label>
                        <Input type="password" placeholder="Coming soon" disabled />
                      </div>
                    </div>
                  </div>
                  
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-3 text-ember-muted">TikTok Integration (Coming Soon)</h4>
                    <div className="opacity-50">
                      <label className="block text-sm font-medium mb-2">Access Token</label>
                      <Input type="password" placeholder="Coming soon" disabled />
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end mt-6">
                  <Button 
                    onClick={updateSettings}
                    className="bg-ember-gold text-parchment-light hover:bg-ember-dark"
                  >
                    Save Settings
                  </Button>
                </div>
              </Card>
              
              <Card className="p-6">
                <h3 className="text-lg font-serif mb-4">Status</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span>OpenAI Integration</span>
                    <Badge className={settings.has_openai_key ? 'bg-green-600' : 'bg-red-600'}>
                      {settings.has_openai_key ? 'Connected' : 'Not Connected'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Quote Bank</span>
                    <Badge className={quotes.length > 0 ? 'bg-green-600' : 'bg-yellow-600'}>
                      {quotes.length} quotes loaded
                    </Badge>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;