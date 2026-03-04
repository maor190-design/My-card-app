import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# כותרת האפליקציה
st.set_page_config(page_title="מעריך קלפים חכם", page_icon="🏀")

# ניסיון חיבור ל-API
if "GEMINI_API_KEY" not in st.secrets:
    st.error("שגיאה: לא נמצא מפתח API ב-Secrets של Streamlit!")
else:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🪄 מעריך קלפים אוטומטי")
st.write("צלם קלף ספורט וקבל הערכת שווי מבוססת איביי")

uploaded_file = st.file_uploader("העלה תמונה...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="הקלף שנקלט", width=300)
    
    if st.button("זהה קלף והצג מחיר"):
        try:
            with st.spinner("הבינה המלאכותית מנתחת את התמונה..."):
                # שימוש במודל יציב
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                prompt = "Identify this sports card. Tell me the player name, year, and set. Give me ONLY a short search string for eBay."
                
                response = model.generate_content([prompt, img])
                search_query = response.text.strip()
                
                st.subheader(f"🔍 מחפש באיביי: {search_query}")
                
                # חיפוש באיביי
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    p_text = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                    try:
                        prices.append(float(p_text))
                    except:
                        continue
                
                if prices:
                    avg_usd = sum(prices[:5]) / len(prices[:5])
                    st.success(f"הערכת שווי: ₪{avg_usd * 3.75:.2f}")
                    st.write(f"מבוסס על ממוצע מכירות אחרונות בארה\"ב.")
                else:
                    st.warning("לא נמצאו מכירות אחרונות מדויקות. נסה לצלם מקרוב יותר.")
                    
        except Exception as e:
            st.error(f"קרתה שגיאה: {e}")
            st.info("טיפ: וודא שה-API Key תקין ושהתמונה ברורה.")
