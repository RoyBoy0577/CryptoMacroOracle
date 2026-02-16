import os
import yfinance as yf
from google import genai
import requests
import feedparser

# משיכת סודות
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_market_data():
    tickers = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "10Y_Yield": "^TNX", "BTC": "BTC-USD"}
    summary = "📊 נתוני שוק נוכחיים:\n"
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            price = t.history(period="1d")['Close'].iloc[-1]
            summary += f"- {name}: {price:.2f}\n"
        except:
            summary += f"- {name}: תקלה\n"
    return summary

def get_news_headlines():
    feed_url = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"
    feed = feedparser.parse(feed_url)
    headlines = [item.title for item in feed.entries[:8]]
    return "\n".join(headlines)

def generate_report(market_data, news):
    # שימוש בספרייה החדשה google-genai
    client = genai.Client(api_key=GEMINI_KEY)
    
    prompt = f"""
    אתה אנליסט שוק בכיר בשיטת Market Makers Method. 
    נתח את הנתונים וספק סקירה פונדמנטלית קצרה לסוחר יום בביטקוין (5/15 דקות).
    נתונים: {market_data}
    חדשות: {news}
    מבנה: # המאקרו והפד, # זירה גיאופוליטית, 🚩 דגלים אדומים, 💡 בנימה אישית.
    כתוב בעברית ממוקדת.
    """
    
    # שימוש במודל 2.0-flash הרגיל
    response = client.models.generate_content(
        model='gemini-2.0-flash', contents=prompt
    )
    return response.text

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if message:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    m_data = get_market_data()
    n_data = get_news_headlines()
    report = generate_report(m_data, n_data)
    send_telegram(report)
