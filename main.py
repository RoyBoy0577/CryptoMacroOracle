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
    """מושך נתוני מאקרו, רמות נזילות, סנטימנט ומחיר פתיחה יומית"""
    summary = 'נתוני שוק חיים:\n'
    
    # הוספת מדד הסנטימנט
    summary += get_fear_greed_index()
    
    # נתוני BTC: פתיחה יומית, מחיר נוכחי ורמות נזילות מאתמול
    try:
        btc = yf.Ticker("BTC-USD")
        # נתונים של היום לקבלת ה-Open
        today_data = btc.history(period="1d")
        daily_open = today_data['Open'].iloc[0]
        current_price = today_data['Close'].iloc[-1]
        
        # נתונים של יומיים לקבלת PDH/PDL של אתמול
        hist = btc.history(period="2d")
        pdh = hist['High'].iloc[0]
        pdl = hist['Low'].iloc[0]
        
        summary += f"- BTC נוכחי: {current_price:.2f}\n"
        summary += f"- פתיחה יומית (Daily Open): {daily_open:.2f}\n"
        summary += f"- גבוה של אתמול (PDH): {pdh:.2f}\n"
        summary += f"- נמוך של אתמול (PDL): {pdl:.2f}\n"
        
        # זיהוי סטטוס ביחס לפתיחה (Premium/Discount)
        status = "Premium (יקר)" if current_price > daily_open else "Discount (זול)"
        summary += f"- סטטוס מחיר: {status} ביחס לפתיחה היומית\n"
    except:
        summary += "- BTC: תקלה במשיכת רמות מחיר\n"

    # מדדי מאקרו נוספים
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
    """מושך חדשות עומק גלובליות ופוליטיות"""
    feeds = [
        "https://www.reutersagency.com/feed/?best-topics=political-general&format=xml",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"
    ]
    all_headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                summary_text = entry.summary[:200] if 'summary' in entry else ""
                all_headlines.append(f"TITLE: {entry.title}\nCONTEXT: {summary_text}")
        except:
            continue
    return "\n\n".join(all_headlines)

def generate_report(market_data, news):
    """יוצר סקירה בשיטת MMM עם דגש על Killzones, נזילות ואירועי קלנדר קרובים"""
    client = genai.Client(api_key=GEMINI_KEY)
    today = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    prompt = f"""
    אתה אנליסט מאקרו בכיר וסוחר מומחה בשיטת Market Makers Method (MMM). 
    זמן הדו"ח: {today}. 
    
    נתוני שוק וסנטימנט: {market_data}
    חדשות עומק: {news}
    
    הנחיות קריטיות לניתוח (סגנון המאסטר):
    1. **התראת קלנדר:** סרוק את החדשות וחפש אירועים כלכליים גדולים בטווח של השבועיים הקרובים (החלטות ריבית, CPI, נאומים של הפד). התרע עליהם והסבר איך השוק יתחיל לתמחר אותם.
    2. **ניתוח Daily Open:** השתמש בנתון ה-Daily Open. אם אנחנו ב-Premium, חפש סימנים להפצה. אם ב-Discount, חפש איסוף מתחת לפתיחה.
    3. **Killzone ו-Judas Swing:** זהה אפשרות לתנועת הטעיה (Judas Swing) שפורצת את ה-Daily Open או את ה-PDH/PDL רק כדי לצוד נזילות לפני המהלך האמיתי.
    4. **מושגי מפתח:** השתמש בביטויים 'הסלמות יזומות', 'ניעורים בשווקים', 'הכסף הטיפש', 'נזילות מתחת ל-PDL', ו'אינטרס מובהק של הדוד סם'.
    
    פורמט (טקסט פשוט בלבד):
    # [כותרת דעתנית על הנרטיב הנוכחי וה-Killzone]
    (ניתוח עומק של האינטרסים והנרטיב)
    
    # 📅 התראת אירועי מאקרו (שבועיים קרובים)
    (פירוט אירועים קלנדריים משמעותיים וצפי לתמחור שוק)
    
    # ניתוח סנטימנט, פתיחה יומית ונזילות
    (ניתוח Fear & Greed ביחס ל-Daily Open ולרמות PDH/PDL)
    
    # בשורה התחתונה ונקודות עניין על הגרף
    (איפה הנזילות? מה המרקט מייקרס מתכננים לנו? רמות עניין למסחר היום)
    
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
            print('✅ הדו"ח המאופטם (Master Edition) נשלח בהצלחה!')
        else:
            print(f'❌ שגיאה בשליחה: {response.text}')
    except Exception as e:
        print(f'❌ תקלה טכנית: {e}')

if __name__ == "__main__":
    print('🚀 Oracle 2.0 (Master Edition) יוצא לדרך...')
    m_data = get_market_data()
    n_data = get_news_headlines()
    report = generate_report(m_data, n_data)
    send_telegram(report)
