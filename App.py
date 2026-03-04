import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="מעריך קלפים", page_icon="🏆")
st.title("🏆 מעריך קלפי ספורט אוטומטי")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("העלה תמונה...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    
    if st.button("זהה והערך שווי"):
        try:
            with st.spinner("מנסה להתחבר למוח של גוגל..."):
                # מנסה כמה שמות של דגמים עד שאחד עובד
                model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'models/gemini-1.5-flash']
                model = None
                
                for name in model_names:
                    try:
                        temp_model = genai.GenerativeModel(name)
                        # בדיקה קצרה אם הוא מגיב
                        response = temp_model.generate_content(["Identify this sports card briefly", img])
                        model = temp_model
                        search_query = response.text.strip().replace('*', '').replace('"', '')
                        break
                    except:
                        continue
                
                if not model:
                    st.error("גוגל לא מאפשרת גישה למודל כרגע. נסה שוב בעוד כמה דקות.")
                    st.stop()

                st.info(f"🔎 זוהה: {search_query}")
                
                # חיפוש באיביי
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    try:
                        p = float(item.get_text().replace('$', '').replace(',', '').split(' ')[0])
                        prices.append(p)
                    except: continue
                
                if prices:
                    avg = sum(prices[1:6] if len(prices) > 1 else prices) / len(prices[1:6] if len(prices) > 1 else prices)
                    st.success(f"✅ הערכת שווי: ₪{avg * 3.75:,.2f}")
                    st.metric("מחיר ממוצע", f"${avg:.2f}")
                else:
                    st.warning("לא נמצאו מכירות אחרונות.")
                    
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
