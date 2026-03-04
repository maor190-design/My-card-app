import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# כותרת
st.set_page_config(page_title="מעריך קלפים", page_icon="🏀")
st.title("🏆 מעריך קלפים אוטומטי")

# בדיקה אם המפתח קיים ב-Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API! וודא שהגדרת אותו ב-Secrets בפורמט: GEMINI_API_KEY = '...'")
    st.stop()

# חיבור לגוגל
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("העלה תמונה...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    
    if st.button("זהה והערך שווי"):
        try:
            with st.spinner("מנתח את התמונה..."):
                # שימוש בשם מודל מלא ליתר ביטחון
                model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
                
                prompt = "Identify this sports card. Tell me player, year, set. Return ONLY a search string for eBay."
                response = model.generate_content([prompt, img])
                
                query = response.text.strip()
                st.info(f"🔎 מחפש: {query}")
                
                # חיפוש באיביי
                ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                res = requests.get(ebay_url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    try:
                        p = float(item.get_text().replace('$', '').replace(',', '').split(' ')[0])
                        prices.append(p)
                    except: continue
                
                if prices:
                    avg = sum(prices[:5]) / len(prices[:5])
                    st.success(f"הערכה: ₪{avg * 3.75:.2f}")
                else:
                    st.warning("לא נמצאו מכירות אחרונות.")
                    
        except Exception as e:
            st.error(f"שגיאה: {e}")
