import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# הגדרות דף
st.set_page_config(page_title="מעריך קלפים", page_icon="🏆")
st.title("🏆 מעריך קלפי ספורט אוטומטי")

# חיבור למפתח מה-Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("חסר מפתח API ב-Secrets!")
    st.stop()

uploaded_file = st.file_uploader("העלה תמונה של קלף...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    
    if st.button("זהה והערך שווי"):
        try:
            with st.spinner("המערכת מזהה את הקלף ומחפשת באיביי..."):
                # שימוש במודל יציב
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # בקשה לזיהוי קצר שמתאים לחיפוש
                prompt = "Identify this sports card. Provide ONLY the player name, year, and set name for an eBay search. Example: '2023 Topps Lamine Yamal Barcelona'"
                response = model.generate_content([prompt, img])
                search_query = response.text.strip()
                
                st.info(f"🔎 זוהה: {search_query}")
                
                # חיפוש באיביי - רק מכירות שהסתיימו (Sold)
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                # חיפוש מחירי איביי (הקוד מחפש את התגים שבהם מופיע המחיר)
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    p_text = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                    try:
                        prices.append(float(p_text))
                    except: continue
                
                if prices:
                    # לוקחים ממוצע של המכירות האחרונות (מתעלמים מהתוצאה הראשונה של איביי שהיא לפעמים פרסומת)
                    real_prices = prices[1:6] if len(prices) > 1 else prices
                    avg_usd = sum(real_prices) / len(real_prices)
                    ils_price = avg_usd * 3.75 # המרה לשקלים
                    
                    st.success(f"✅ הערכת שווי: ₪{ils_price:,.2f}")
                    st.metric("מחיר ממוצע בדולר", f"${avg_usd:.2f}")
                    st.write(f"הנתונים מבוססים על {len(real_prices)} מכירות אחרונות ב-eBay.")
                else:
                    st.warning("הקלף זוהה, אך לא נמצאו מכירות אחרונות. נסה לדייק את שם הסט ידנית.")
                    
        except Exception as e:
            st.error(f"אופס, קרתה שגיאה: {str(e)}")
            st.info("אם מופיעה שגיאת 404, וודא שקובץ ה-requirements מעודכן ב-GitHub.")
