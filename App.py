import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# הגדרות דף
st.set_page_config(page_title="מעריך קלפים", page_icon="🏆")
st.title("🏆 מעריך קלפי ספורט אוטומטי")

# בדיקה שהמפתח קיים ב-Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets! וודא שהגדרת אותו בפורמט: GEMINI_API_KEY = '...'")
    st.stop()

# הגדרת ה-AI עם המפתח שלך
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("העלה תמונה של קלף או לוט...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300, caption="התמונה שנקלטה")
    
    if st.button("זהה והערך שווי"):
        try:
            with st.spinner("המערכת מזהה את הקלפים..."):
                # שימוש בשם המודל הכי סטנדרטי למניעת שגיאת 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # הנחיה לזיהוי קלף בודד או לוט (חבילה)
                prompt = "Identify the sports cards in this image. If it is one card, give player name, year, and set. If it is a lot, identify the main cards. Return ONLY a concise search string for eBay sold listings."
                
                response = model.generate_content([prompt, img])
                search_query = response.text.strip().replace('*', '').replace('"', '')
                
                st.info(f"🔎 זוהה: {search_query}")
                
                # חיפוש באיביי (מכירות שהסתיימו - Sold)
                ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(ebay_url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    p_text = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                    try:
                        prices.append(float(p_text))
                    except: continue
                
                if prices:
                    # חישוב ממוצע של המכירות האחרונות (מדלגים על התוצאה הראשונה שהיא לעיתים פרסומת)
                    relevant_prices = prices[1:6] if len(prices) > 1 else prices
                    avg_usd = sum(relevant_prices) / len(relevant_prices)
                    ils_price = avg_usd * 3.75 # המרה לשקלים
                    
                    st.success(f"✅ הערכת שווי: ₪{ils_price:,.2f}")
                    st.metric("מחיר ממוצע (דולר)", f"${avg_usd:.2f}")
                    st.write(f"מבוסס על מחירי 'Last Sold' באיביי.")
                else:
                    st.warning("הקלף זוהה, אך לא נמצאו מכירות אחרונות שתואמות בדיוק. נסה תמונה ברורה יותר.")
                    
        except Exception as e:
            st.error(f"אופס, קרתה שגיאה טכנית: {str(e)}")
            st.info("אם השגיאה נמשכת, נסה לרענן את דף האפליקציה.")
