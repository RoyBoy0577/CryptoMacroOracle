import os
import yfinance as yf
from google import genai
import requests
import feedparser

# משיכת סודות מהכספת של GitHub
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_market_data():
    tickers = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "10Y_Yield": "^TNX", "BTC": "BTC-USD"}
    summary = 'נתוני שוק:\n'
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
    client = genai.Client(api_key=GEMINI_KEY)
    
    prompt = f"""
    אתה אנליסט בכיר בשיטת Market Makers Method. 
    נתח את הנתונים הבאים וכתוב סקירה קצרה לסוחר יום בביטקוין.
    
    נתונים: {market_data}
    חדשות: {news}
    
    הנחיות חשובות:
    1. כתוב בטקסט פשוט בלבד (בלי כוכביות, בלי הדגשות, בלי סימני קוד).
    2. השתמש בסימנים פשוטים כמו # או - לחלוקה.
    3. כתוב בעברית ממוקדת, קריאה ובלי 'חפירות'.
    
    מבנה הדו"ח:
    # המאקרו והפד
    # זירה גיאופוליטית
    # דגלים אדומים
    # בנימה אישית
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash', contents=prompt
    )
    return response.text

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print('✅ הדו"ח נשלח בהצלחה לטלגרם!')
        else:
            print(f'❌ שגיאה בשליחה: {response.text}')
    except Exception as e:
        print(f'❌ תקלה טכנית: {e}')

if __name__ == "__main__":
    print('🚀 מריץ את ה-Oracle...')
    m_data = get_market_data()
    n_data = get_news_headlines()
    report = generate_report(m_data, n_data)
    send_telegram(report)
