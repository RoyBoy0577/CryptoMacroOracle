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

def get_market_data():
    """מושך נתוני מאקרו ורמות נזילות קריטיות (PDH/PDL)"""
    summary = 'נתוני שוק חיים:\n'
    
    # משיכת נתוני BTC לזיהוי רמות נזילות (PDH/PDL)
    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="2d")
        current_price = hist['Close'].iloc[-1]
        pdh = hist['High'].iloc[0]  # הגבוה של אתמול
        pdl = hist['Low'].iloc[0]   # הנמוך של אתמול
        summary += f"- BTC נוכחי: {current_price:.2f}\n"
        summary += f"- גבוה של אתמול (PDH): {pdh:.2f}\n"
        summary += f"- נמוך של אתמול (PDL): {pdl:.2f}\n"
    except:
        summary += "- BTC: תקלה במשיכת רמות מחיר\n"

    # משיכת מדדי מאקרו
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
    """מושך חדשות עומק מ-Reuters ומ-CNBC כדי להבין נרטיבים עולמיים"""
    feeds = [
        "https://www.reutersagency.com/feed/?best-topics=political-general&format=xml",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"
    ]
    all_headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                # מושכים כותרת ותקציר כדי לתת ל-AI הקשר רחב יותר
                summary_text = entry.summary[:150] if 'summary' in entry else ""
                all_headlines.append(f"TITLE: {entry.title}\nCONTEXT: {summary_text}")
        except:
            continue
    return "\n\n".join(all_headlines)

def generate_report(market_data, news):
    """המוח של המערכת - יוצר סקירה בסגנון MMM פונדמנטלי עמוק"""
    client = genai.Client(api_key=GEMINI_KEY)
    today = datetime.now().strftime('%d/%m/%Y')
    
    prompt = f"""
    אתה אנליסט מאקרו בכיר וסוחר מומחה בשיטת Market Makers Method (MMM). 
    תאריך: {today}.
    משימה: כתוב סקירה פונדמנטלית בפורמט 'סיפורי' המנתח אינטרסים של כוחות עולמיים.
    
    נתונים: {market_data}
    חדשות: {news}
    
    הנחיות לכתיבה (סגנון המאסטר):
    1. חבר נקודות (Connect the dots): אל תדווח חדשות יבשות. הסבר איך אירוע (למשל בחירות ביפן או ציוץ של נשיא) משפיע על ה'קרי טרייד' ואיך זה ינער את הביטקוין.
    2. אינטרסים: מה הדוד סם רוצה? מה המטרה של הבנק המרכזי? חפש את ה'למה'.
    3. מושגי MMM: השתמש במושגים כמו 'כסף חכם', 'נזילות (Liquidity)', 'פיתוי (Inducement)', ו'סדר עולמי חדש'.
    4. התייחסות למחיר: התייחס ל-PDH (גבוה של אתמול) ו-PDL (נמוך של אתמול) כנקודות ציד סטופים פוטנציאליות.
    
    פורמט הדו"ח (טקסט פשוט בלבד):
    # [כותרת דעתנית על נושא המאקרו המרכזי]
    (ניתוח עומק של האינטרסים מאחורי הכותרות)
    
    # זירה גיאופוליטית והסלמות יזומות
    (ניתוח מהלכי כוח, מכסים ואיומים והשפעתם על הפחד בשווקים)
    
    # נתונים כלכליים - מבט לעומק
    (ניתוח DXY, VIX ותשואות לא כמספרים, אלא כסנטימנט של הכסף הגדול)
    
    # בשורה התחתונה ונקודות עניין על הגרף
    (סיכום ממוקד: איפה הנזילות? מה המרקט מייקרס מתכננים לנו היום?)
    
    בלי כוכביות, בלי הדגשות. השתמש רק ב-# לכותרות.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash', contents=prompt
    )
    return response.text

def send_telegram(message):
    """שולח את הדו"ח כטקסט פשוט ויציב"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print('✅ הדו"ח המשופר נשלח בהצלחה!')
        else:
            print(f'❌ שגיאה בשליחה: {response.text}')
    except Exception as e:
        print(f'❌ תקלה טכנית: {e}')

if __name__ == "__main__":
    print('🚀 Oracle 2.0 יוצא לדרך...')
    m_data = get_market_data()
    n_data = get_news_headlines()
    report = generate_report(m_data, n_data)
    send_telegram(report)
