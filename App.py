import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# הגדרות דף
st.set_page_config(page_title="מעריך קלפים", page_icon="🏆")
st.title("🏆 מעריך קלפי ספורט (eBay Sold)")

# בדיקת מפתח
if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("העלה תמונה של קלף...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    
    if st.button("זהה קלף ומצא מחיר"):
        # שלב 1: זיהוי הקלף (בעזרת גוגל)
        with st.status("שלב 1: הבינה המלאכותית מזהה את הקלף...") as status:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Identify this sports card. Return ONLY a search string for eBay sold listings. Example: '2023 Topps Lamine Yamal 27'"
                response = model.generate_content([prompt, img])
                search_query = response.text.strip().replace('*', '')
                st.write(f"הקלף זוהה כ: **{search_query}**")
                status.update(label="זיהוי הושלם!", state="complete")
            except Exception as e:
                st.error(f"שגיאה בזיהוי: {e}")
                st.stop()

        # שלב 2: חיפוש ב-eBay (הקוד שלי מבצע את החיפוש)
        with st.spinner(f"שלב 2: מחפש מכירות אחרונות של '{search_query}' ב-eBay..."):
            try:
                # כתובת חיפוש למכירות שהסתיימו בלבד
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    try:
                        p = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                        prices.append(float(p))
                    except: continue
                
                if prices:
                    # חישוב ממוצע (מתעלם מהתוצאה הראשונה שלפעמים היא זבל של איביי)
                    valid_prices = prices[1:10] if len(prices) > 1 else prices
                    avg_usd = sum(valid_prices) / len(valid_prices)
                    ils_price = avg_usd * 3.75 # שער המרה
                    
                    st.success(f"### הערכת שווי: ₪{ils_price:,.2f}")
                    st.metric("מחיר ממוצע בדולר", f"${avg_usd:.2f}")
                    st.write(f"המחיר מבוסס על {len(valid_prices)} מכירות אחרונות ב-eBay.")
                    st.caption(f"[צפה בתוצאות החיפוש המקוריות ב-eBay]({url})")
                else:
                    st.warning("הקלף זוהה, אך לא נמצאו מכירות שלו ב-eBay. נסה תמונה ברורה יותר.")
            except Exception as e:
                st.error(f"שגיאה בחיפוש המחיר: {e}")
