#!/usr/bin/env python3
"""Smart Website Generator - Creates custom websites from natural language requirements."""
import sys
import os
import re
import random

PROJECTS_DIR = os.path.expanduser("~/Projects")

def parse_requirements(user_input):
    """Parse user's natural language into website requirements."""
    user_input = user_input.lower()
    
    req = {
        "name": "My Website",
        "type": "landing",  # landing, portfolio, blog, ecommerce, dashboard, app
        "style": "modern",
        "colors": [],
        "features": [],
        "animations": False,
        "dark": False,
        "responsive": True,
        "sections": [],
        "fonts": ["system-ui"],
    }
    
    # Detect name - priority: "called X" > "named X" > "for X" (but not "site for X")
    # If no explicit pattern, use first meaningful word as name
    name_match = re.search(r"(?:called|named)\s+['\"]?(\w+)", user_input)
    if name_match:
        req["name"] = name_match.group(1).title()
    else:
        # Try "for X" - this is usually who the site is for
        match = re.search(r"for\s+(\w+)", user_input)
        if match:
            potential_name = match.group(1)
            # Skip if it's a common word, not a name
            if potential_name.lower() not in ["help", "more", "info", "example", "demo", "test"]:
                req["name"] = potential_name.title()
            else:
                words = user_input.split()
                for w in words:
                    if len(w) > 3 and w not in ["website", "site", "create", "make", "build", "with", "using", "have", "need", "want", "get"]:
                        req["name"] = w.title()
                        break
        else:
            words = user_input.split()
            for w in words:
                if len(w) > 3 and w not in ["website", "site", "create", "make", "build", "with", "using", "have", "need", "want", "get"]:
                    req["name"] = w.title()
                    break
    
    # Detect type
    if any(w in user_input for w in ["blog", "post", "article", "news"]):
        req["type"] = "blog"
    elif any(w in user_input for w in ["shop", "store", "product", "cart", "buy", "ecommerce", "e-commerce"]):
        req["type"] = "ecommerce"
    elif any(w in user_input for w in ["dashboard", "admin", "panel", "analytics", "stats"]):
        req["type"] = "dashboard"
    elif any(w in user_input for w in ["portfolio", "showcase", "work", "project", "gallery"]):
        req["type"] = "portfolio"
    elif any(w in user_input for w in ["app", "application", "saas", "service", "tool"]):
        req["type"] = "app"
    
    # Detect style/theme
    if any(w in user_input for w in ["cyber", "futuristic", "neon", "hacker", "matrix", "tech"]):
        req["style"] = "cyber"
    elif any(w in user_input for w in ["dark", "night", "black"]):
        req["style"] = "dark"
    elif any(w in user_input for w in ["light", "clean", "minimal", "simple", "white"]):
        req["style"] = "light"
    elif any(w in user_input for w in ["colorful", "vibrant", "gradient", "rainbow", "modern"]):
        req["style"] = "colorful"
    elif any(w in user_input for w in ["corporate", "business", "professional", "enterprise"]):
        req["style"] = "corporate"
    elif any(w in user_input for w in ["gaming", "game", "streamer", "twitch"]):
        req["style"] = "gaming"
    elif any(w in user_input for w in ["personal", "about", "me", "bio", "resume", "cv"]):
        req["style"] = "personal"
    
    # Detect colors mentioned
    color_map = {
        "blue": "#3b82f6", "red": "#ef4444", "green": "#22c55e", "purple": "#a855f7",
        "pink": "#ec4899", "orange": "#f97316", "yellow": "#eab308", "cyan": "#06b6d4",
        "white": "#ffffff", "black": "#000000", "gold": "#ffd700", "silver": "#c0c0c0",
        "navy": "#1e3a5f", "teal": "#14b8a6", "magenta": "#d946ef", "lime": "#84cc16",
    }
    for color, hex_val in color_map.items():
        if color in user_input:
            req["colors"].append(hex_val)
    
    if not req["colors"]:
        req["colors"] = ["#3b82f6", "#8b5cf6"]
    
    # Detect features
    feature_keywords = {
        "contact": ["contact", "email", "form", "message"],
        "pricing": ["pricing", "price", "plan", "cost", "subscription"],
        "features": ["feature", "benefit", "advantage", "capability"],
        "testimonials": ["testimonial", "review", "feedback", "client", "customer"],
        "team": ["team", "member", "staff", "about us"],
        "faq": ["faq", "question", "answer", "help"],
        "blog": ["blog", "post", "article", "news"],
        "shop": ["shop", "store", "product", "buy"],
        "gallery": ["gallery", "image", "photo", "portfolio"],
        "login": ["login", "signin", "auth", "register", "signup"],
        "chat": ["chat", "message", "support", "bot"],
    }
    
    for feature, keywords in feature_keywords.items():
        if any(k in user_input for k in keywords):
            req["features"].append(feature)
    
    # Detect animations
    if any(w in user_input for w in ["animation", "animate", "animated", "transition", "effect", "motion", "hover"]):
        req["animations"] = True
    
    # Detect dark mode preference
    if "dark" in user_input:
        req["dark"] = True
    
    # Build sections based on type
    req["sections"] = get_sections_for_type(req["type"])
    
    # Add requested sections
    if "contact" in req["features"]:
        if "contact" not in req["sections"]:
            req["sections"].append("contact")
    if "pricing" in req["features"]:
        req["sections"].append("pricing")
    if "features" in req["features"]:
        if "features" not in req["sections"]:
            req["sections"].insert(1, "features")
    
    return req


def get_sections_for_type(site_type):
    """Get default sections for each site type."""
    sections_map = {
        "landing": ["hero", "about", "features", "cta"],
        "portfolio": ["hero", "work", "about", "contact"],
        "blog": ["hero", "posts", "about", "newsletter"],
        "ecommerce": ["hero", "products", "features", "cart"],
        "dashboard": ["sidebar", "stats", "charts", "table"],
        "app": ["hero", "features", "pricing", "testimonials"],
        "personal": ["hero", "about", "experience", "contact"],
    }
    return sections_map.get(site_type, ["hero", "about", "contact"])


def generate_custom_website(user_input):
    """Generate a custom website based on user's natural language requirements."""
    req = parse_requirements(user_input)
    
    # Create project directory
    project_name = req["name"].replace(" ", "")
    project_path = os.path.join(PROJECTS_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)
    
    # Generate based on style
    if req["style"] == "cyber":
        html = generate_cyber_site(req)
    elif req["style"] == "dark":
        html = generate_dark_site(req)
    elif req["style"] == "light":
        html = generate_light_site(req)
    elif req["style"] == "gaming":
        html = generate_gaming_site(req)
    elif req["style"] == "corporate":
        html = generate_corporate_site(req)
    elif req["style"] == "personal":
        html = generate_personal_site(req)
    else:
        html = generate_modern_site(req)
    
    # Write files
    with open(os.path.join(project_path, "index.html"), "w") as f:
        f.write(html)
    
    with open(os.path.join(project_path, "style.css"), "w") as f:
        f.write(generate_css(req))
    
    # Add JavaScript if animations or features
    if req["animations"] or req["type"] == "dashboard":
        with open(os.path.join(project_path, "script.js"), "w") as f:
            f.write(generate_js(req))
    
    return project_path, req


def generate_cyber_site(req):
    """Generate cyber/hacker themed site."""
    primary = req["colors"][0] if req["colors"] else "#00ff00"
    secondary = req["colors"][1] if len(req["colors"]) > 1 else "#ff00ff"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
</head>
<body>
    <nav>
        <div class="nav-container">
            <a href="#" class="logo"><span class="glitch" data-text="{req['name']}">{req['name']}</span></a>
            <ul class="nav-links">
                <li><a href="#home">HOME</a></li>
                <li><a href="#about">ABOUT</a></li>
                <li><a href="#features">FEATURES</a></li>
                <li><a href="#contact">CONTACT</a></li>
            </ul>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <div class="typing-text">> INITIALIZING SYSTEM...</div>
            <h1 class="glitch-text">{req['name'].upper()}</h1>
            <p>/// NEXT GENERATION SOLUTION</p>
            <a href="#contact" class="cta-btn">GET ACCESS</a>
        </div>
        <div class="hero-visual">
            <div class="cyber-grid"></div>
        </div>
    </section>
    
    <section id="about">
        <h2>// ABOUT THE SYSTEM</h2>
        <div class="about-content">
            <p>Advanced solution built with cutting-edge technology. Optimized for performance and scalability.</p>
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number" data-target="99">0</span>%
                    <span class="stat-label">UPTIME</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number" data-target="24">0</span>/7
                    <span class="stat-label">SUPPORT</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number" data-target="100">0</span>%
                    <span class="stat-label">SECURE</span>
                </div>
            </div>
        </div>
    </section>
    
    <section id="features">
        <h2>// SYSTEM FEATURES</h2>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>HIGH PERFORMANCE</h3>
                <p>Lightning fast response times</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3>SECURE</h3>
                <p>Enterprise-grade security</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🌐</div>
                <h3>SCALABLE</h3>
                <p>Grows with your needs</p>
            </div>
        </div>
    </section>
    
    <section id="contact">
        <h2>// ESTABLISH CONNECTION</h2>
        <form class="cyber-form">
            <input type="text" placeholder="IDENTIFIER" required>
            <input type="email" placeholder="COMM_CHANNEL" required>
            <textarea placeholder="DATA_PACKET" rows="5"></textarea>
            <button type="submit" class="submit-btn">TRANSMIT</button>
        </form>
    </section>
    
    <footer>
        <p>&copy; 2026 {req['name']} // SYSTEM ONLINE</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>"""


def generate_modern_site(req):
    """Generate modern vibrant site."""
    primary = req["colors"][0]
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <nav>
        <div class="nav-container">
            <a href="#" class="logo">{req['name']}</a>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
            <a href="#contact" class="nav-cta">Get Started</a>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <span class="badge">✨ NEW</span>
            <h1>Build Something <span class="gradient-text">Amazing</span></h1>
            <p>Create stunning experiences with modern design and powerful features.</p>
            <div class="hero-buttons">
                <a href="#contact" class="btn-primary">Get Started</a>
                <a href="#about" class="btn-secondary">Learn More</a>
            </div>
            <div class="hero-stats">
                <div><strong>500+</strong><span>Clients</span></div>
                <div><strong>99%</strong><span>Satisfaction</span></div>
                <div><strong>24/7</strong><span>Support</span></div>
            </div>
        </div>
    </section>
    
    <section id="about">
        <h2>About Us</h2>
        <p class="section-desc">We're passionate about creating exceptional digital experiences.</p>
        <div class="about-grid">
            <div class="about-card">
                <h3>Our Mission</h3>
                <p>To transform ideas into powerful digital solutions.</p>
            </div>
            <div class="about-card">
                <h3>Our Vision</h3>
                <p>Setting new standards in digital innovation.</p>
            </div>
            <div class="about-card">
                <h3>Our Values</h3>
                <p>Innovation, quality, and customer focus.</p>
            </div>
        </div>
    </section>
    
    <section id="services">
        <h2>Services</h2>
        <div class="services-grid">
            <div class="service-card">
                <div class="service-icon">💻</div>
                <h3>Web Development</h3>
                <p>Custom websites and web applications.</p>
            </div>
            <div class="service-card">
                <div class="service-icon">🎨</div>
                <h3>Design</h3>
                <p>Beautiful, user-centered designs.</p>
            </div>
            <div class="service-card">
                <div class="service-icon">📈</div>
                <h3>Marketing</h3>
                <p>Grow your online presence.</p>
            </div>
        </div>
    </section>
    
    <section id="contact">
        <h2>Let's Talk</h2>
        <form class="contact-form">
            <div class="form-group">
                <input type="text" placeholder="Your Name" required>
            </div>
            <div class="form-group">
                <input type="email" placeholder="Your Email" required>
            </div>
            <div class="form-group">
                <textarea placeholder="Your Message" rows="5"></textarea>
            </div>
            <button type="submit" class="btn-submit">Send Message</button>
        </form>
    </section>
    
    <footer>
        <p>&copy; 2026 {req['name']}. All rights reserved.</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>"""


def generate_dark_site(req):
    """Generate dark elegant site."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="dark">
    <nav>
        <div class="nav-container">
            <a href="#" class="logo">{req['name']}</a>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#work">Work</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <h1>Welcome to <span class="highlight">{req['name']}</span></h1>
            <p>Crafting digital experiences that inspire.</p>
            <a href="#contact" class="btn">Get in Touch</a>
        </div>
    </section>
    
    <section id="about">
        <h2>About</h2>
        <p>We create digital products that make a difference.</p>
    </section>
    
    <section id="work">
        <h2>Selected Work</h2>
        <div class="work-grid">
            <div class="work-item">Project One</div>
            <div class="work-item">Project Two</div>
            <div class="work-item">Project Three</div>
        </div>
    </section>
    
    <section id="contact">
        <h2>Contact</h2>
        <form>
            <input type="text" placeholder="Name">
            <input type="email" placeholder="Email">
            <textarea placeholder="Message"></textarea>
            <button type="submit">Send</button>
        </form>
    </section>
    
    <footer>
        <p>&copy; 2026 {req['name']}</p>
    </footer>
</body>
</html>"""


def generate_light_site(req):
    """Generate clean minimal light site."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <nav>
        <div class="nav-container">
            <a href="#" class="logo">{req['name']}</a>
            <ul class="nav-links">
                <li><a href="#">Home</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Contact</a></li>
            </ul>
        </div>
    </nav>
    
    <section class="hero">
        <h1>{req['name']}</h1>
        <p>Simple. Clean. Minimal.</p>
    </section>
    
    <section>
        <h2>About</h2>
        <p>Less is more.</p>
    </section>
    
    <section>
        <h2>Contact</h2>
        <form>
            <input type="text" placeholder="Name">
            <input type="email" placeholder="Email">
            <textarea placeholder="Message"></textarea>
            <button type="submit">Send</button>
        </form>
    </section>
    
    <footer>
        <p>&copy; 2026 {req['name']}</p>
    </footer>
</body>
</html>"""


def generate_gaming_site(req):
    """Generate gaming/streamer site."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']} - Gaming</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="gaming">
    <nav>
        <a href="#" class="logo">{req['name']}</a>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#streams">Streams</a></li>
            <li><a href="#videos">Videos</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    
    <section id="home" class="hero">
        <h1 class="glow">{req['name']}</h1>
        <p>Gaming Content Creator</p>
        <div class="socials">
            <a href="#" class="twitch">Twitch</a>
            <a href="#" class="youtube">YouTube</a>
            <a href="#" class="discord">Discord</a>
        </div>
    </section>
    
    <section id="streams">
        <h2>Live Streams</h2>
        <div class="stream-grid">
            <div class="stream-card">Live Now</div>
            <div class="stream-card">Past Stream</div>
            <div class="stream-card">Past Stream</div>
        </div>
    </section>
    
    <footer>
        <p>© 2026 {req['name']}</p>
    </footer>
</body>
</html>"""


def generate_corporate_site(req):
    """Generate corporate business site."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']} - Business Solutions</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">{req['name']}</div>
            <nav>
                <a href="#home">Home</a>
                <a href="#solutions">Solutions</a>
                <a href="#about">About</a>
                <a href="#contact">Contact</a>
            </nav>
            <a href="#contact" class="btn-blue">Get Quote</a>
        </div>
    </header>
    
    <section id="home" class="hero-corporate">
        <h1>Enterprise Solutions for Your Business</h1>
        <p>Trusted by leading companies worldwide</p>
        <a href="#contact" class="btn-primary">Contact Sales</a>
    </section>
    
    <section id="solutions">
        <h2>Our Solutions</h2>
        <div class="solutions-grid">
            <div class="solution-card">
                <h3>Consulting</h3>
                <p>Expert guidance for your business transformation.</p>
            </div>
            <div class="solution-card">
                <h3>Technology</h3>
                <p>Cutting-edge tech solutions.</p>
            </div>
            <div class="solution-card">
                <h3>Support</h3>
                <p>24/7 dedicated support team.</p>
            </div>
        </div>
    </section>
    
    <section id="contact" class="contact-corporate">
        <h2>Contact Us</h2>
        <form>
            <input type="text" placeholder="Company Name">
            <input type="email" placeholder="Business Email">
            <textarea placeholder="How can we help?"></textarea>
            <button type="submit" class="btn-submit">Submit Inquiry</button>
        </form>
    </section>
    
    <footer>
        <div class="footer-content">
            <p>&copy; 2026 {req['name']}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""


def generate_personal_site(req):
    """Generate personal portfolio site."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req['name']} - Portfolio</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
</head>
<body>
    <nav>
        <a href="#" class="logo">{req['name']}</a>
        <ul>
            <li><a href="#about">About</a></li>
            <li><a href="#experience">Experience</a></li>
            <li><a href="#work">Work</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    
    <section id="about" class="hero-personal">
        <div class="profile-img"></div>
        <h1>Hi, I'm {req['name']}</h1>
        <p class="tagline">Developer & Designer</p>
        <p class="bio">Creating digital experiences with passion and precision.</p>
        <div class="social-links">
            <a href="#">GitHub</a>
            <a href="#">LinkedIn</a>
            <a href="#">Twitter</a>
        </div>
    </section>
    
    <section id="experience">
        <h2>Experience</h2>
        <div class="timeline">
            <div class="timeline-item">
                <h3>Senior Developer</h3>
                <p class="company">Tech Company</p>
                <p class="period">2022 - Present</p>
            </div>
            <div class="timeline-item">
                <h3>Designer</h3>
                <p class="company">Design Studio</p>
                <p class="period">2020 - 2022</p>
            </div>
        </div>
    </section>
    
    <section id="work">
        <h2>Selected Projects</h2>
        <div class="project-grid">
            <div class="project-card">Project 1</div>
            <div class="project-card">Project 2</div>
            <div class="project-card">Project 3</div>
        </div>
    </section>
    
    <section id="contact">
        <h2>Get In Touch</h2>
        <p>Let's work together.</p>
        <a href="mailto:hello@email.com" class="email-link">hello@email.com</a>
    </section>
    
    <footer>
        <p>© 2026 {req['name']}</p>
    </footer>
</body>
</html>"""


def generate_css(req):
    """Generate custom CSS based on requirements."""
    style = req["style"]
    primary = req["colors"][0] if req["colors"] else "#3b82f6"
    
    if style == "cyber":
        return CYBER_CSS
    elif style == "gaming":
        return GAMING_CSS
    elif style == "corporate":
        return CORPORATE_CSS
    elif style == "personal":
        return PERSONAL_CSS
    else:
        return MODERN_CSS


# CSS Templates
CYBER_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a0f; color: #00ff88; font-family: 'Share Tech Mono', monospace; overflow-x: hidden; }
nav { position: fixed; width: 100%; top: 0; z-index: 100; background: rgba(10,10,15,0.9); border-bottom: 1px solid #00ff88; }
.nav-container { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.5rem; font-weight: bold; color: #00ff88; text-decoration: none; }
.nav-links { display: flex; list-style: none; gap: 2rem; }
.nav-links a { color: #00ff88; text-decoration: none; transition: 0.3s; }
.nav-links a:hover { text-shadow: 0 0 10px #00ff88; }
.hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; position: relative; overflow: hidden; }
.hero::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, transparent 0%, #0a0a0f 100%); }
.hero-content { position: relative; z-index: 1; }
h1 { font-size: 4rem; margin: 1rem 0; text-shadow: 0 0 20px #00ff88; animation: flicker 3s infinite; }
@keyframes flicker { 0%,100%{opacity:1} 50%{opacity:0.8} }
.typing-text { font-size: 1.2rem; margin-bottom: 1rem; }
.cta-btn { display: inline-block; padding: 1rem 3rem; border: 2px solid #00ff88; color: #00ff88; text-decoration: none; margin-top: 2rem; transition: 0.3s; }
.cta-btn:hover { background: #00ff88; color: #0a0a0f; box-shadow: 0 0 30px #00ff88; }
section { padding: 6rem 2rem; max-width: 1200px; margin: 0 auto; }
h2 { font-size: 2.5rem; margin-bottom: 2rem; border-bottom: 1px solid #00ff88; padding-bottom: 1rem; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-top: 3rem; }
.stat-box { border: 1px solid #00ff88; padding: 2rem; text-align: center; }
.stat-number { font-size: 3rem; display: block; }
.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.feature-card { border: 1px solid #00ff88; padding: 2rem; transition: 0.3s; }
.feature-card:hover { transform: translateY(-5px); box-shadow: 0 0 20px #00ff88; }
.feature-icon { font-size: 3rem; margin-bottom: 1rem; }
.cyber-form { max-width: 600px; margin: 0 auto; }
.cyber-form input, .cyber-form textarea { width: 100%; padding: 1rem; margin-bottom: 1rem; background: transparent; border: 1px solid #00ff88; color: #00ff88; font-family: inherit; }
.submit-btn { width: 100%; padding: 1rem; background: #00ff88; color: #0a0a0f; border: none; cursor: pointer; font-weight: bold; }
footer { text-align: center; padding: 2rem; border-top: 1px solid #00ff88; margin-top: 4rem; }
"""

MODERN_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
:root { --primary: #3b82f6; --dark: #1e293b; }
body { font-family: 'Inter', sans-serif; color: #333; line-height: 1.6; }
nav { position: fixed; width: 100%; top: 0; background: rgba(255,255,255,0.95); box-shadow: 0 2px 20px rgba(0,0,0,0.1); z-index: 100; }
.nav-container { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.5rem; font-weight: 800; color: var(--dark); }
.nav-links { display: flex; list-style: none; gap: 2rem; }
.nav-links a { color: #666; text-decoration: none; transition: 0.3s; }
.nav-links a:hover { color: var(--primary); }
.hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 6rem 2rem 4rem; }
.hero h1 { font-size: 4rem; font-weight: 800; margin-bottom: 1rem; line-height: 1.1; }
.gradient-text { background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.badge { display: inline-block; padding: 0.5rem 1rem; background: #dbeafe; color: #3b82f6; border-radius: 20px; font-size: 0.875rem; font-weight: 600; margin-bottom: 1rem; }
.hero-buttons { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
.btn-primary, .btn-secondary { padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: 0.3s; }
.btn-primary { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; }
.btn-secondary { background: white; color: #333; border: 2px solid #e2e8f0; }
section { padding: 6rem 2rem; max-width: 1200px; margin: 0 auto; }
section h2 { font-size: 2.5rem; text-align: center; margin-bottom: 3rem; }
.hero-stats { display: flex; gap: 3rem; justify-content: center; margin-top: 3rem; }
.hero-stats div { text-align: center; }
.hero-stats strong { display: block; font-size: 2rem; }
.hero-stats span { color: #666; }
.about-grid, .services-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.about-card, .service-card { padding: 2rem; border-radius: 12px; background: white; box-shadow: 0 4px 20px rgba(0,0,0,0.05); transition: 0.3s; }
.about-card:hover, .service-card:hover { transform: translateY(-5px); }
.service-icon { font-size: 3rem; margin-bottom: 1rem; }
.contact-form { max-width: 600px; margin: 0 auto; }
.form-group { margin-bottom: 1rem; }
input, textarea { width: 100%; padding: 1rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; }
input:focus, textarea:focus { outline: none; border-color: var(--primary); }
.btn-submit { width: 100%; padding: 1rem; background: var(--primary); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
footer { background: #1e293b; color: white; text-align: center; padding: 3rem 2rem; margin-top: 4rem; }
"""

GAMING_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body.gaming { background: #0f0f1a; color: #fff; font-family: 'Rajdhani', sans-serif; }
.gaming nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: rgba(15,15,26,0.9); }
.gaming .logo { font-size: 2rem; font-weight: 700; color: #ff0055; text-shadow: 0 0 10px #ff0055; }
.gaming nav ul { display: flex; list-style: none; gap: 2rem; }
.gaming nav a { color: #fff; text-decoration: none; text-transform: uppercase; }
.gaming .hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; background: radial-gradient(ellipse at center, #1a1a3a 0%, #0f0f1a 70%); }
.gaming h1.glow { font-size: 5rem; text-shadow: 0 0 30px #ff0055, 0 0 60px #ff0055; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{text-shadow: 0 0 30px #ff0055;} 50%{text-shadow: 0 0 50px #ff0055, 0 0 100px #ff0055;} }
.socials { display: flex; gap: 1rem; margin-top: 2rem; }
.socials a { padding: 0.75rem 2rem; border: 2px solid; border-radius: 4px; text-decoration: none; font-weight: 700; transition: 0.3s; }
.twitch { border-color: #9146ff; color: #9146ff; }
.youtube { border-color: #ff0000; color: #ff0000; }
.discord { border-color: #5865f2; color: #5865f2; }
section { padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
section h2 { font-size: 2.5rem; text-align: center; margin-bottom: 2rem; }
.stream-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.stream-card { background: #1a1a3a; padding: 2rem; text-align: center; border: 1px solid #333; border-radius: 8px; }
"""

CORPORATE_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Roboto', sans-serif; color: #333; }
header { background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; width: 100%; }
.header-container { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.5rem; font-weight: 700; color: #1e40af; }
header nav { display: flex; gap: 2rem; }
header nav a { color: #64748b; text-decoration: none; font-weight: 500; }
.btn-blue { background: #1e40af; color: white; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; }
.hero-corporate { min-height: 80vh; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding-top: 80px; }
.hero-corporate h1 { font-size: 3rem; margin-bottom: 1rem; }
.solutions-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; max-width: 1200px; margin: 0 auto; }
.solution-card { padding: 2rem; border-radius: 8px; background: #f8fafc; }
.contact-corporate { background: #f8fafc; padding: 4rem 2rem; }
.contact-corporate form { max-width: 600px; margin: 0 auto; }
footer { background: #1e293b; color: white; padding: 2rem; text-align: center; }
"""

PERSONAL_CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Open Sans', sans-serif; color: #333; }
nav { display: flex; justify-content: space-between; padding: 2rem; max-width: 1200px; margin: 0 auto; }
.logo { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; }
nav ul { display: flex; list-style: none; gap: 2rem; }
nav a { color: #666; text-decoration: none; }
.hero-personal { min-height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 4rem 2rem; }
.profile-img { width: 150px; height: 150px; border-radius: 50%; background: #ddd; margin-bottom: 2rem; }
.hero-personal h1 { font-family: 'Playfair Display', serif; font-size: 3rem; }
.tagline { font-size: 1.2rem; color: #666; margin: 0.5rem 0; }
.bio { max-width: 500px; color: #888; margin-top: 1rem; }
.social-links { display: flex; gap: 1rem; margin-top: 2rem; }
.social-links a { color: #333; text-decoration: none; }
section { padding: 4rem 2rem; max-width: 800px; margin: 0 auto; }
section h2 { font-family: 'Playfair Display', serif; margin-bottom: 2rem; }
.timeline-item { border-left: 2px solid #ddd; padding-left: 2rem; margin-bottom: 2rem; }
.project-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.project-card { background: #f5f5f5; padding: 3rem; text-align: center; }
.email-link { font-size: 1.5rem; color: #333; }
footer { text-align: center; padding: 2rem; background: #f5f5f5; }
"""

def generate_js(req):
    """Generate JavaScript for animations and interactivity."""
    if req["animations"]:
        return ANIMATION_JS
    return BASE_JS


BASE_JS = """// Base functionality
console.log('Website loaded');
"""

ANIMATION_JS = """// Animations
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.75) {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }
    });
});

// Counter animation
const counters = document.querySelectorAll('.stat-number');
counters.forEach(counter => {
    const target = parseInt(counter.dataset.target);
    let count = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        count += increment;
        if (count >= target) {
            counter.textContent = target;
            clearInterval(timer);
        } else {
            counter.textContent = Math.floor(count);
        }
    }, 30);
});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({ behavior: 'smooth' });
    });
});
"""


def main():
    if len(sys.argv) < 3:
        return f"""SMART WEBSITE GENERATOR

Usage: 
  python handler.py generate "<user requirements>"

Examples:
  python handler.py generate "Create a dark portfolio website called John with animations"
  python handler.py generate "Make a cyber themed ecommerce site for selling games"
  python handler.py generate "Build a modern corporate business website with contact form"
  python handler.py generate "A personal site for me with dark theme and animations"

The generator understands natural language and creates custom websites!
"""
    
    # Get user requirements from all remaining args
    user_input = " ".join(sys.argv[2:])
    
    # Generate the website
    project_path, req = generate_custom_website(user_input)
    
    return f"""✅ Custom Website Generated!

Project: {req['name']}
Type: {req['type']}
Style: {req['style']}
Features: {', '.join(req['features']) if req['features'] else 'Basic'}
Animations: {'Yes' if req['animations'] else 'No'}

Location: {project_path}

To view:
  open {project_path}/index.html
  
Or serve locally:
  cd {project_path} && python3 -m http.server 8080
"""


if __name__ == "__main__":
    print(main())
