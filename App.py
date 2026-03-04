import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# הגדרות דף
st.set_page_config(page_title="מעריך קלפים", page_icon="🏀")
st.title("🏆 מעריך קלפי ספורט אוטומטי")

# בדיקת מפתח
if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets!")
    st.stop()

# חיבור למודל
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("העלה תמונה של קלף...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    
    if st.button("זהה והערך שווי"):
        try:
            with st.spinner("ה-AI מנתח את הקלף..."):
                # שימוש בשם המודל הכי נפוץ למניעת 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # הנחיה לזיהוי
                prompt = "What sports card is this? Provide only the player, year, and set as a search string for eBay sold listings."
                response = model.generate_content([prompt, img])
                query = response.text.strip()
                
                st.info(f"🔎 מחפש באיביי: {query}")
                
                # חיפוש באיביי (Sold Listings)
                url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    try:
                        p_raw = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                        prices.append(float(p_raw))
                    except: continue
                
                if prices:
                    avg_usd = sum(prices[:5]) / len(prices[:5])
                    st.success(f"✅ הערכת שווי: ₪{avg_usd * 3.75:.2f}")
                    st.write(f"מבוסס על ממוצע מכירות אחרונות של קלפי {query}")
                else:
                    st.warning("לא נמצאו מכירות אחרונות מדויקות באיביי.")
                    
        except Exception as e:
            st.error(f"אופס, קרתה שגיאה: {str(e)}")
