import os
import yfinance as yf
import google.generativeai as genai
import requests
import feedparser

# משיכת הסודות מהכספת של GitHub
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_market_data():
    # משיכת נתונים: VIX (פחד), DXY (דולר), תשואות אג"ח וביטקוין
    tickers = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "10Y_Yield": "^TNX", "BTC": "BTC-USD"}
    summary = "📊 נתוני שוק נוכחיים:\n"
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            price = t.history(period="1d")['Close'].iloc[-1]
            summary += f"- {name}: {price:.2f}\n"
        except:
            summary += f"- {name}: תקלה במשיכה\n"
    return summary

def get_news_headlines():
    # משיכת כותרות כלכליות מ-CNBC
    feed_url = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"
    feed = feedparser.parse(feed_url)
    headlines = [item.title for item in feed.entries[:8]]
    return "\n".join(headlines)

def generate_report(market_data, news):
    # הגדרת Gemini
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""
    אתה אנליסט שוק בכיר המומחה בשיטת Market Makers Method. 
    נתח את הנתונים הבאים וספק סקירה פונדמנטלית קצרה לסוחר יום בביטקוין (אינטרוולים של 5/15 דקות).
    
    נתוני שוק גולמיים:
    {market_data}
    
    כותרות חדשות אחרונות:
    {news}
    
    דגשים לסיכום:
    1. השתמש בכותרות ברורות עם # (למשל: # המאקרו והפד).
    2. הסבר איך האירועים משפיעים על נזילות (Liquidity) ועל תנועות ה-Market Makers (ניעורים, איסוף).
    3. כלול אזור "🚩 דגלים אדומים" המתייחס ל-VIX, תשואות אג"ח ואינפלציה.
    4. הוסף סעיף "💡 בנימה אישית" עם המלצת AI ממוקדת.
    
    נסח בעברית עניינית, ללא חזרות מיותרות, ובהתאם לסגנון שביקשתי (דומה למורה שלי).
    """
    
    response = model.generate_content(prompt)
    return response.text

def send_telegram(message):
    # שליחה לבוט בטלגרם
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # מגבלת תווים בטלגרם היא 4096, אנחנו נשלח רק אם יש תוכן
    if message:
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

if __name__ == "__main__":
    m_data = get_market_data()
    n_data = get_news_headlines()
    final_report = generate_report(m_data, n_data)
    send_telegram(final_report)
