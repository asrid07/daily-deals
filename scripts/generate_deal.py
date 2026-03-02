#!/usr/bin/env python3
"""
DealHunt Daily - Automatic Deal Post Generator
================================================
Generates deal/offer blog posts with product comparisons,
pros/cons, pricing tables, and affiliate CTAs.
Writes Jekyll-compatible markdown files.

Usage:
  python generate_deal.py                   # Generate 1 random deal post
  python generate_deal.py --count 3         # Generate 3 deal posts
  python generate_deal.py --category Electronics
  python generate_deal.py --dry-run         # Preview without creating files
  python generate_deal.py --backfill 7      # Generate 7 days of past deals
"""

import os
import re
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

# ============================================================
# DEAL DATABASE - Products, Prices, Content Templates
# ============================================================

DEAL_CATEGORIES = {
    "Electronics": {
        "emoji": "🖥️",
        "stores": ["Amazon", "Flipkart", "Best Buy", "Croma"],
        "products": [
            {
                "name": "Apple MacBook Air M3 (2025)",
                "original": "₹1,24,900", "deal": "₹99,990", "discount": 20, "savings": "₹24,910",
                "rating": 5, "currency": "INR",
                "features": ["M3 Chip with 8-core GPU", "15.3-inch Liquid Retina Display", "18-hour battery life", "8GB Unified Memory", "256GB SSD", "MagSafe charging", "1080p FaceTime HD camera"],
                "pros": ["Blazing fast M3 performance", "All-day battery life", "Stunning display", "Silent fanless design"],
                "cons": ["Only 8GB RAM in base model", "Limited port selection", "No touchscreen"],
                "why": "The MacBook Air M3 is the gold standard for productivity laptops. Perfect for students, developers, and creative professionals who need power without bulk.",
            },
            {
                "name": "Sony WH-1000XM5 Headphones",
                "original": "₹29,990", "deal": "₹19,990", "discount": 33, "savings": "₹10,000",
                "rating": 5, "currency": "INR",
                "features": ["Industry-leading noise cancellation", "30-hour battery", "Multipoint connection", "Speak-to-Chat", "LDAC Hi-Res Audio", "Ultra-lightweight 250g design"],
                "pros": ["Best-in-class ANC", "Exceptional comfort for long sessions", "Premium sound quality", "Great call quality"],
                "cons": ["No IP rating for water resistance", "Doesn't fold flat", "Premium price even on sale"],
                "why": "The XM5 headphones are the undisputed king of noise-cancelling headphones. Perfect for commuters, remote workers, and audiophiles.",
            },
            {
                "name": "Samsung Galaxy S25 Ultra 256GB",
                "original": "₹1,29,999", "deal": "₹1,04,999", "discount": 19, "savings": "₹25,000",
                "rating": 5, "currency": "INR",
                "features": ["Snapdragon 8 Elite processor", "6.9-inch Dynamic AMOLED", "200MP main camera", "Galaxy AI built-in", "5000mAh battery", "S Pen included", "Titanium frame"],
                "pros": ["Best Android camera system", "Galaxy AI features are game-changing", "S Pen for productivity", "Premium titanium build"],
                "cons": ["Expensive even on sale", "Large and heavy", "Slow charging compared to competitors"],
                "why": "The Galaxy S25 Ultra is the ultimate Android flagship. If you want the best camera, display, and AI features in one device, this is it.",
            },
            {
                "name": "iPad Air M2 (2024) 11-inch",
                "original": "₹69,900", "deal": "₹54,900", "discount": 21, "savings": "₹15,000",
                "rating": 4, "currency": "INR",
                "features": ["M2 chip performance", "11-inch Liquid Retina display", "Apple Pencil Pro support", "Wi-Fi 6E", "12MP front and back cameras", "USB-C", "Touch ID"],
                "pros": ["Fantastic M2 performance", "Apple Pencil Pro support", "Versatile for work and play", "Lightweight and portable"],
                "cons": ["Base model only 128GB", "Smart Keyboard sold separately", "60Hz display"],
                "why": "The iPad Air M2 hits the sweet spot between power and price. Ideal for note-taking, media consumption, light video editing, and casual gaming.",
            },
            {
                "name": "LG C4 55-inch OLED 4K TV",
                "original": "₹1,59,990", "deal": "₹1,09,990", "discount": 31, "savings": "₹50,000",
                "rating": 5, "currency": "INR",
                "features": ["OLED evo panel with perfect blacks", "α9 Gen7 AI Processor", "Dolby Vision & Atmos", "4x HDMI 2.1 ports", "120Hz refresh rate", "webOS 24", "Gaming features: VRR, ALLM, G-Sync"],
                "pros": ["Unbeatable OLED picture quality", "Perfect for PS5/Xbox gaming", "Dolby Vision + Atmos", "Slim and stunning design"],
                "cons": ["Risk of burn-in with static content", "Gets very bright in HDR (good but uses more power)", "No legs in box — wall mount recommended"],
                "why": "The LG C4 OLED is the best TV for most people. Incredible picture quality for movies, sports, and gaming at a price that's finally reasonable.",
            },
            {
                "name": "Logitech MX Master 3S Mouse",
                "original": "₹10,995", "deal": "₹7,495", "discount": 32, "savings": "₹3,500",
                "rating": 5, "currency": "INR",
                "features": ["8K DPI optical sensor", "Quiet clicks", "MagSpeed scroll wheel", "Connect up to 3 devices", "USB-C rechargeable", "70-day battery life", "Works on any surface including glass"],
                "pros": ["Best productivity mouse ever made", "Incredible scroll wheel", "Multi-device switching", "Ergonomic design"],
                "cons": ["Not ideal for gaming", "Expensive for a mouse", "Right-hand only"],
                "why": "The MX Master 3S is the ultimate productivity mouse. If you work on a computer all day, this one upgrade will change your workflow.",
            },
        ]
    },
    "Fashion": {
        "emoji": "👗",
        "stores": ["Amazon", "Myntra", "Flipkart", "Ajio"],
        "products": [
            {
                "name": "Levi's 511 Slim Fit Jeans (Pack of 1)",
                "original": "₹4,599", "deal": "₹1,999", "discount": 57, "savings": "₹2,600",
                "rating": 4, "currency": "INR",
                "features": ["Premium stretch denim", "Slim fit through thigh", "Classic 5-pocket styling", "Multiple wash options", "Sits below waist", "Machine washable"],
                "pros": ["Timeless Levi's quality", "Great fit for most body types", "Versatile — casual to smart-casual", "Incredible value at this price"],
                "cons": ["Sizing can be inconsistent online", "Limited color options on sale", "Stretch may loosen over time"],
                "why": "Levi's 511 is a wardrobe essential. At 57% off, you're getting premium denim quality at fast-fashion prices. Stock up!",
            },
            {
                "name": "Nike Air Max 270 Running Shoes",
                "original": "₹12,795", "deal": "₹7,677", "discount": 40, "savings": "₹5,118",
                "rating": 4, "currency": "INR",
                "features": ["Max Air 270 unit for cushioning", "Mesh upper for breathability", "Foam midsole", "Rubber outsole", "Multiple colorways", "Iconic Nike design"],
                "pros": ["Incredibly comfortable for all-day wear", "Head-turning design", "Great cushioning", "Works for casual and light exercise"],
                "cons": ["Not ideal for serious running", "Can feel warm in summer", "Premium price (but great on sale)"],
                "why": "The Air Max 270 is Nike's most iconic lifestyle shoe. At 40% off, this is one of the best prices we've ever seen.",
            },
            {
                "name": "Casio G-Shock GA-2100 Watch",
                "original": "₹10,995", "deal": "₹6,995", "discount": 36, "savings": "₹4,000",
                "rating": 5, "currency": "INR",
                "features": ["Carbon Core Guard structure", "200M water resistance", "World time (31 zones)", "LED illumination", "Shock resistant", "3-year battery life", "Thin 11.8mm profile"],
                "pros": ["Incredibly tough and durable", "Sleek minimal design ('CasiOak')", "Affordable luxury look", "Lightweight for a G-Shock"],
                "cons": ["Display can be hard to read in sunlight", "No Bluetooth or smart features", "Plastic case (by design)"],
                "why": "The GA-2100 'CasiOak' is the most popular G-Shock ever made. Looks like a luxury watch at a fraction of the price.",
            },
        ]
    },
    "Home": {
        "emoji": "🏡",
        "stores": ["Amazon", "Flipkart", "IKEA", "Pepperfry"],
        "products": [
            {
                "name": "Dyson V12 Detect Slim Vacuum",
                "original": "₹52,900", "deal": "₹39,900", "discount": 25, "savings": "₹13,000",
                "rating": 5, "currency": "INR",
                "features": ["Laser dust detection", "Dyson Hyperdymium motor", "60 min runtime", "LCD screen shows dust count", "HEPA filtration", "5 cleaning heads included", "Wall-mount dock"],
                "pros": ["Laser reveals hidden dust — genuinely useful", "Powerful suction", "Great battery life", "Light and maneuverable"],
                "cons": ["Expensive even on sale", "Small dustbin needs frequent emptying", "Replacement filters cost extra"],
                "why": "The Dyson V12 is the best cordless vacuum you can buy. The laser dust detection is not a gimmick — it genuinely changes how you clean.",
            },
            {
                "name": "Instant Pot Duo 7-in-1 (6 Quart)",
                "original": "₹9,999", "deal": "₹5,999", "discount": 40, "savings": "₹4,000",
                "rating": 5, "currency": "INR",
                "features": ["7 appliances in 1", "Pressure cooker, slow cooker, rice cooker", "Steamer, sauté pan, yogurt maker, warmer", "13 smart programs", "Stainless steel inner pot", "Dishwasher-safe parts"],
                "pros": ["Replaces multiple kitchen devices", "Saves 70% cooking time", "Energy efficient", "Huge recipe community online"],
                "cons": ["Learning curve for pressure cooking", "Bulky for small kitchens", "Silicone ring absorbs odors"],
                "why": "The Instant Pot is a kitchen revolution. At 40% off, there's never been a better time to join the millions of Instant Pot converts.",
            },
            {
                "name": "Philips Air Fryer HD9200 (4.1L)",
                "original": "₹9,995", "deal": "₹5,495", "discount": 45, "savings": "₹4,500",
                "rating": 4, "currency": "INR",
                "features": ["Rapid Air Technology", "4.1L capacity (serves 3-4)", "1400W power", "Temperature control 80°C-200°C", "30-min timer", "Non-stick basket", "Dishwasher safe parts"],
                "pros": ["Healthier cooking with 90% less oil", "Quick and easy to use", "Easy to clean", "Compact but good capacity"],
                "cons": ["Food texture differs from deep frying", "Can be noisy", "Limited capacity for large families"],
                "why": "Air fryers are genuinely life-changing for healthier eating. The Philips HD9200 is reliable, trusted, and at 45% off — it's a steal.",
            },
        ]
    },
    "Books": {
        "emoji": "📚",
        "stores": ["Amazon Kindle", "Amazon", "Flipkart"],
        "products": [
            {
                "name": "Kindle Paperwhite (16GB, 2024)",
                "original": "₹16,499", "deal": "₹11,499", "discount": 30, "savings": "₹5,000",
                "rating": 5, "currency": "INR",
                "features": ["6.8-inch glare-free display", "Adjustable warm light", "Waterproof (IPX8)", "Up to 10 weeks battery", "USB-C charging", "300 ppi resolution", "16GB storage (~thousands of books)"],
                "pros": ["Best e-reader on the market", "Glare-free — reads like real paper", "Waterproof for pool/bath reading", "Weeks of battery life"],
                "cons": ["No color display", "No audiobook playback", "Locked to Amazon ecosystem"],
                "why": "The Kindle Paperwhite is the best investment for readers. If you read even 2-3 books a year, it pays for itself in Kindle deal savings.",
            },
            {
                "name": "Atomic Habits by James Clear (Paperback)",
                "original": "₹699", "deal": "₹299", "discount": 57, "savings": "₹400",
                "rating": 5, "currency": "INR",
                "features": ["#1 New York Times Bestseller", "320 pages", "Practical habit-building framework", "1% improvement philosophy", "Proven strategies backed by science"],
                "pros": ["Life-changing practical advice", "Easy to read and implement", "Works for any area of life", "Great value for knowledge gained"],
                "cons": ["Some concepts may feel familiar if you read similar books", "Could use more diverse examples"],
                "why": "Atomic Habits is THE book on building good habits and breaking bad ones. At ₹299, this is the cheapest self-improvement investment you'll ever make.",
            },
        ]
    },
    "Software": {
        "emoji": "💻",
        "stores": ["Official Website", "Amazon", "Stack Commerce"],
        "products": [
            {
                "name": "NordVPN 2-Year Plan",
                "original": "$286.80", "deal": "$89.13", "discount": 69, "savings": "$197.67",
                "rating": 5, "currency": "USD",
                "features": ["5,500+ servers in 60 countries", "Threat Protection Pro", "Dark Web Monitoring", "Meshnet feature", "6 simultaneous connections", "30-day money-back guarantee", "No-logs policy (audited)"],
                "pros": ["Fast and reliable connections", "Excellent for streaming Netflix/Disney+", "Strong privacy and security", "Works on all devices"],
                "cons": ["Requires 2-year commitment for best price", "Can slow connection slightly", "Some servers slower than others"],
                "why": "NordVPN is the #1 rated VPN for speed, security, and streaming. At 69% off, the 2-year plan works out to just $3.71/month.",
            },
            {
                "name": "Notion Plus Plan (Annual)",
                "original": "$120/year", "deal": "$96/year", "discount": 20, "savings": "$24/year",
                "rating": 5, "currency": "USD",
                "features": ["Unlimited blocks and pages", "30-day version history", "100 AI responses per member", "Unlimited file uploads", "API access", "Guest collaborators", "Custom automations"],
                "pros": ["All-in-one workspace (notes, docs, databases, projects)", "Incredibly flexible and customizable", "Great templates library", "Active community"],
                "cons": ["Steep learning curve", "Can be overwhelming for simple needs", "Offline mode is limited"],
                "why": "Notion is the Swiss Army knife of productivity. If you manage projects, take notes, or organize anything — this tool replaces 5+ apps.",
            },
        ]
    },
    "Gaming": {
        "emoji": "🎮",
        "stores": ["Amazon", "Flipkart", "Steam", "PlayStation Store"],
        "products": [
            {
                "name": "PlayStation 5 Slim Digital Edition",
                "original": "₹44,990", "deal": "₹37,990", "discount": 16, "savings": "₹7,000",
                "rating": 5, "currency": "INR",
                "features": ["Custom AMD Zen 2 CPU", "10.28 TFLOPS GPU", "825GB SSD", "4K gaming up to 120fps", "Ray tracing", "DualSense controller", "Backward compatible with PS4"],
                "pros": ["Incredible gaming performance", "DualSense controller is revolutionary", "Fast SSD loading times", "Huge game library"],
                "cons": ["Digital only — no disc drive", "SSD fills up fast", "Online requires PS Plus subscription"],
                "why": "The PS5 Slim Digital is the most affordable way into next-gen gaming. At ₹7,000 off, this is a rare discount on Sony's flagship console.",
            },
            {
                "name": "Xbox Game Pass Ultimate (12 Months)",
                "original": "₹7,999", "deal": "₹4,799", "discount": 40, "savings": "₹3,200",
                "rating": 5, "currency": "INR",
                "features": ["400+ games on console, PC & cloud", "Day-one access to Xbox exclusives", "EA Play included", "Xbox Live Gold included", "Cloud gaming on mobile", "Member discounts on purchases"],
                "pros": ["Best value in gaming — period", "Day-one access to Starfield, Forza, etc.", "Play on console, PC, or phone", "New games added monthly"],
                "cons": ["Games rotate out of library", "Requires good internet for cloud gaming", "Price has been increasing"],
                "why": "Xbox Game Pass is like Netflix for games. At 40% off annual, you get access to hundreds of premium games for less than ₹400/month.",
            },
        ]
    },
    "Courses": {
        "emoji": "🎓",
        "stores": ["Udemy", "Coursera", "Skillshare"],
        "products": [
            {
                "name": "Udemy Complete Python Bootcamp (2026 Edition)",
                "original": "₹3,499", "deal": "₹449", "discount": 87, "savings": "₹3,050",
                "rating": 5, "currency": "INR",
                "features": ["22+ hours of video content", "Lifetime access", "14 coding exercises", "3 real-world projects", "Certificate of completion", "30-day money-back guarantee", "Mobile and TV access"],
                "pros": ["Best Python course for beginners", "Project-based learning", "Lifetime access — learn at your pace", "Incredible ₹449 price"],
                "cons": ["Self-paced means no accountability", "Some sections could be more advanced", "Certificate not accredited"],
                "why": "Python is the #1 most in-demand programming language. At ₹449 (87% off!), this course costs less than a meal out but can change your career.",
            },
            {
                "name": "Coursera Google Data Analytics Certificate",
                "original": "$49/month", "deal": "$39/month", "discount": 20, "savings": "$10/month",
                "rating": 5, "currency": "USD",
                "features": ["Professional Certificate from Google", "8-course series", "Hands-on projects with real data", "Shareable on LinkedIn", "No prior experience needed", "Flexible schedule", "7-day free trial"],
                "pros": ["Google brand on your resume", "Job-ready skills in 6 months", "Hands-on portfolio projects", "High completion rate"],
                "cons": ["Monthly subscription adds up", "Certificate alone won't guarantee a job", "Pace can be slow for experienced learners"],
                "why": "Google's Data Analytics certificate is one of the most respected online credentials. Companies actively look for this on resumes.",
            },
        ]
    },
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:80]


def generate_deal_content(product: dict, category: str, store: str) -> str:
    """Generate full blog post content for a deal."""

    # Features section
    features_md = "\n".join([f"- ✅ **{f}**" for f in product["features"]])

    # Pros & Cons
    pros_md = "\n".join([f"- ✅ {p}" for p in product["pros"]])
    cons_md = "\n".join([f"- ❌ {c}" for c in product["cons"]])

    # Who should buy
    audiences = [
        "students and young professionals",
        "tech enthusiasts and early adopters",
        "budget-conscious shoppers looking for premium quality",
        "anyone looking to upgrade from their current setup",
        "gift buyers looking for a crowd-pleaser",
        "remote workers and work-from-home professionals",
    ]

    content = f"""## Why This Deal Is Worth Your Attention

{product['why']}

At **{product['discount']}% off**, this is one of the lowest prices we've tracked for the **{product['name']}**. Deals like this don't last long — especially on premium products.

---

## Key Features & Specifications

{features_md}

---

## What We Love (Pros)

{pros_md}

## What Could Be Better (Cons)

{cons_md}

---

## Who Should Buy This?

This deal is perfect for **{random.choice(audiences)}**. If you've been waiting for the right time to buy, **this is it**.

| Feature | Details |
|---------|---------|
| Product | {product['name']} |
| Category | {category} |
| Store | {store} |
| Original Price | {product['original']} |
| Deal Price | **{product['deal']}** |
| You Save | **{product['savings']} ({product['discount']}% off)** |
| Our Rating | {'⭐' * product['rating']} ({product['rating']}/5) |

---

## Price History & Deal Analysis

We've been tracking the price of the **{product['name']}** for months. Here's our analysis:

- **Regular Price**: {product['original']}
- **Average Sale Price**: Usually 10-15% off during regular sales
- **Today's Price**: **{product['deal']}** — this is **{product['discount']}% below retail**
- **Verdict**: 🟢 **BUY NOW** — This is at or near the lowest price we've ever recorded

> 💡 **Pro Tip:** Add to cart now even if you're undecided. Deals at this price level often sell out within hours. You can always cancel before it ships.

---

## Final Verdict

The **{product['name']}** at **{product['deal']}** is an exceptional deal. You're saving **{product['savings']}** compared to the regular price, and you're getting a product that consistently earns top ratings.

**Our recommendation: Don't hesitate.** This price won't last.

---

*Prices and availability are accurate as of the publication date. Deals may expire or sell out at any time.*
"""
    return content


def generate_deal_post(category: str = None, post_date: datetime = None) -> dict:
    """Generate a complete deal post."""
    if category is None:
        category = random.choice(list(DEAL_CATEGORIES.keys()))

    if post_date is None:
        post_date = datetime.now()

    cat_data = DEAL_CATEGORIES[category]
    product = random.choice(cat_data["products"])
    store = random.choice(cat_data["stores"])

    # Title variations
    title_templates = [
        "🔥 {name} at {deal} ({discount}% OFF) — Lowest Price Alert!",
        "Deal Alert: {name} Drops to {deal} — Save {savings}!",
        "{name} — {discount}% OFF at {deal} | Today's Best {cat} Deal",
        "🛒 {name} Flash Sale: {deal} (Save {savings}) — Limited Time!",
        "Steal Deal: {name} at Just {deal} — {discount}% Off!",
    ]

    title = random.choice(title_templates).format(
        name=product["name"], deal=product["deal"],
        discount=product["discount"], savings=product["savings"],
        cat=category
    )

    description = f"Get the {product['name']} at {product['deal']} — that's {product['discount']}% off the original {product['original']} price. Save {product['savings']} on this verified deal from {store}."

    content = generate_deal_content(product, category, store)

    hot = product["discount"] >= 30 or random.random() > 0.5
    expires_options = ["Limited time only", "While stocks last", "Ends in 48 hours",
                       "Flash sale — today only", "This weekend only", f"Valid until {(post_date + timedelta(days=random.randint(1,5))).strftime('%B %d, %Y')}"]

    slug = slugify(f"{product['name']}-deal-{product['discount']}-off")
    filename = f"{post_date.strftime('%Y-%m-%d')}-{slug}.md"

    keywords = [product["name"].lower(), category.lower(), "deal", "discount",
                "offer", store.lower(), f"{category.lower()} deals", "best price"]

    front_matter = f"""---
layout: deal
title: "{title}"
description: "{description}"
date: {post_date.strftime('%Y-%m-%d')}
category: {category}
keywords: [{', '.join(keywords)}]
author: "DealHunt Team"
product_name: "{product['name']}"
store: "{store}"
original_price: "{product['original']}"
deal_price: "{product['deal']}"
discount: {product['discount']}
savings: "{product['savings']}"
rating: {product['rating']}
currency: "{product['currency']}"
hot: {'true' if hot else 'false'}
expires: "{random.choice(expires_options)}"
affiliate_url: "#"
---
"""

    return {
        "filename": filename,
        "content": front_matter + content,
        "title": title,
        "category": category,
        "product": product["name"],
        "date": post_date.strftime('%Y-%m-%d'),
    }


def write_post(post: dict, dry_run: bool = False) -> str:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = POSTS_DIR / post["filename"]

    if filepath.exists():
        print(f"  ⚠️  Skipped (exists): {post['filename']}")
        return None

    if dry_run:
        print(f"  🔍 [DRY RUN] Would create: {post['filename']}")
        print(f"     Product: {post['product']}")
        print(f"     Category: {post['category']}")
        return None

    filepath.write_text(post["content"], encoding="utf-8")
    print(f"  ✅ Created: {post['filename']}")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="DealHunt Daily - Deal Post Generator")
    parser.add_argument("--count", type=int, default=1, help="Number of deal posts to generate")
    parser.add_argument("--category", type=str, default=None,
                        help=f"Category: {', '.join(DEAL_CATEGORIES.keys())}")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--backfill", type=int, default=0, help="Generate deals for past N days")
    args = parser.parse_args()

    print("=" * 60)
    print("🔥 DealHunt Daily - Auto Deal Generator")
    print("=" * 60)

    existing = {f.name for f in POSTS_DIR.glob("*.md")} if POSTS_DIR.exists() else set()
    created = []

    if args.backfill > 0:
        print(f"\n📅 Backfilling {args.backfill} days of deals...\n")
        categories = list(DEAL_CATEGORIES.keys())
        for i in range(args.backfill, 0, -1):
            d = datetime.now() - timedelta(days=i)
            cat = categories[i % len(categories)]
            post = generate_deal_post(category=cat, post_date=d)
            if post["filename"] not in existing:
                r = write_post(post, dry_run=args.dry_run)
                if r: created.append(r)
                existing.add(post["filename"])
    else:
        print(f"\n🛒 Generating {args.count} deal post(s)...\n")
        for i in range(args.count):
            d = datetime.now() - timedelta(days=i)
            post = generate_deal_post(category=args.category, post_date=d)
            attempts = 0
            while post["filename"] in existing and attempts < 10:
                post = generate_deal_post(category=args.category, post_date=d)
                attempts += 1
            if post["filename"] not in existing:
                r = write_post(post, dry_run=args.dry_run)
                if r: created.append(r)
                existing.add(post["filename"])

    print(f"\n{'=' * 60}")
    print(f"📊 Summary: {len(created)} deal post(s) created")
    print(f"{'=' * 60}\n")
    return created


if __name__ == "__main__":
    main()
