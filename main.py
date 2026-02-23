import os
import yfinance as yf
from google import genai
import requests
import feedparser
from datetime import datetime

# משיכת סודות מהכספת של GitHub
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_fear_greed_index():
    """מושך את מדד הפחד והחמדנות של הקריפטו"""
    try:
        response = requests.get("https://api.alternative.me/fng/")
        data = response.json()
        value = data['data'][0]['value']
        classification = data['data'][0]['value_classification']
        return f"- מדד Fear & Greed: {value} ({classification})\n"
    except:
        return "- מדד Fear & Greed: תקלה במשיכת הסנטימנט\n"

def get_market_data():
    """מושך נתוני מאקרו, רמות נזילות וסנטימנט"""
    summary = 'נתוני שוק חיים:\n'
    
    # הוספת מדד הסנטימנט
    summary += get_fear_greed_index()
    
    # נתוני BTC ורמות נזילות
    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="2d")
        current_price = hist['Close'].iloc[-1]
        pdh = hist['High'].iloc[0]
        pdl = hist['Low'].iloc[0]
        summary += f"- BTC נוכחי: {current_price:.2f}\n"
        summary += f"- גבוה של אתמול (PDH): {pdh:.2f}\n"
        summary += f"- נמוך של אתמול (PDL): {pdl:.2f}\n"
    except:
        summary += "- BTC: תקלה במשיכת רמות מחיר\n"

    # מדדי מאקרו
    tickers = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "10Y_Yield": "^TNX"}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            price = t.history(period="1d")['Close'].iloc[-1]
            summary += f"- {name}: {price:.2f}\n"
        except:
            summary += f"- {name}: תקלה\n"
    return summary

def get_news_headlines():
    """מושך חדשות עומק גלובליות"""
    feeds = [
        "https://www.reutersagency.com/feed/?best-topics=political-general&format=xml",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"
    ]
    all_headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                summary_text = entry.summary[:150] if 'summary' in entry else ""
                all_headlines.append(f"TITLE: {entry.title}\nCONTEXT: {summary_text}")
        except:
            continue
    return "\n\n".join(all_headlines)

def generate_report(market_data, news):
    """יוצר סקירה בשיטת MMM עם דגש על Killzones וניעורים"""
    client = genai.Client(api_key=GEMINI_KEY)
    today = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    prompt = f"""
    אתה אנליסט מאקרו בכיר וסוחר מומחה בשיטת Market Makers Method (MMM). 
    זמן הדו"ח: {today}. 
    
    נתונים: {market_data}
    חדשות: {news}
    
    הנחיות לכתיבה (סגנון המאסטר):
    1. התייחס לזמן הדו"ח - אם אנחנו לפני לונדון או ניו-יורק (Killzones), חפש סימנים ל-Judas Swing או תנועות הטעיה.
    2. השתמש בביטויים: 'הסלמות יזומות', 'ניעורים בשווקים', 'הכסף הטיפש ניזון מכותרות', 'צייד נזילות מתחת ל-PDL', ו'אינטרס מובהק'.
    3. נתח את מדד ה-Fear & Greed - האם יש אופוריה מסוכנת או פחד שהמרקט מייקרס ינצלו?
    4. הסבר תמיד את ה'למה' מאחורי המהלכים הגיאופוליטיים של הדוד סם או הבנקים המרכזיים.
    
    פורמט (טקסט פשוט בלבד):
    # [כותרת דעתנית על המצב ב-Killzone הנוכחי]
    (ניתוח עומק של האינטרסים והנרטיב)
    
    # זירה גיאופוליטית והסלמות יזומות
    (ניתוח מהלכי כוח עולמיים והשפעתם על הסנטימנט)
    
    # ניתוח סנטימנט ונזילות (MMM)
    (ניתוח Fear & Greed ביחס לרמות PDH/PDL)
    
    # בשורה התחתונה ונקודות עניין על הגרף
    (איפה ה-Liquidity? מה המרקט מייקרס מתכננים לנו ב-Killzone הקרוב?)
    
    בלי כוכביות, בלי הדגשות. השתמש רק ב-# לכותרות.
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
            print('✅ הדו"ח הסופי נשלח בהצלחה!')
        else:
            print(f'❌ שגיאה בשליחה: {response.text}')
    except Exception as e:
        print(f'❌ תקלה טכנית: {e}')

if __name__ == "__main__":
    print('🚀 Oracle 2.0 (Killzone Edition) מתחיל...')
    m_data = get_market_data()
    n_data = get_news_headlines()
    report = generate_report(m_data, n_data)
    send_telegram(report)
