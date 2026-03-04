import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

# הגדרת ה"עיניים" של גוגל (AI)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("שכחת להוסיף את ה-API Key ב-Secrets!")

st.set_page_config(page_title="מעריך קלפים חכם", page_icon="🏀")
st.title("🪄 מעריך קלפים אוטומטי")

uploaded_file = st.file_uploader("העלה תמונה של קלף ספורט (או לוט)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="התמונה שהועלתה", width=300)
    
    if st.button("זהה קלף והצג מחיר"):
        with st.spinner("ה-AI מזהה את הקלפים..."):
            # שלב 1: זיהוי הקלף מהתמונה
            prompt = "Identify the sports cards in this image. For each card, provide the player name, year, set name, and card number. format as a search query for eBay."
            response = model.generate_content([prompt, img])
            card_name = response.text.strip()
            
            st.info(f"זוהה: {card_name}")
            
            # שלב 2: חיפוש באיביי (פונקציה קיימת)
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={card_name.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            prices = []
            for item in soup.find_all('span', {'class': 's-item__price'}):
                p_text = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                try: prices.append(float(p_text))
                except: continue
            
            if prices:
                avg_usd = sum(prices[:5]) / len(prices[:5])
                st.metric("הערכת שווי (שקלים)", f"₪{avg_usd * 3.72:.2f}")
                st.write(f"מבוסס על ממוצע של {len(prices[:5])} מכירות אחרונות ב-eBay.")
            else:
                st.error("לא הצלחתי למצוא מחירי מכירה אחרונים. נסה תמונה ברורה יותר.")

