import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Card Evaluator", layout="centered")
st.title("🏀 מעריך קלפים אוטומטי")

# בדיקה בסיסית של המפתח
if "GEMINI_API_KEY" not in st.secrets:
    st.error("עצור! המפתח לא הוגדר ב-Secrets. חזור להגדרות ב-Streamlit והוסף אותו.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=250)
    
    if st.button("בצע זיהוי והערכה"):
        # שלב 1: ניסיון זיהוי עם המודל הכי בטוח
        search_query = ""
        try:
            with st.spinner("מזהה את הקלף..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(["Identify this sports card player, year and set. Return only a search string.", img])
                search_query = response.text.strip().replace('*', '')
        except Exception as e:
            st.warning("הזיהוי האוטומטי נכשל. נסה להקליד את שם הקלף למטה.")
            search_query = st.text_input("שם הקלף (למשל: Lamine Yamal 2024 Topps):")

        if search_query:
            st.info(f"🔎 מחפש ב-eBay: {search_query}")
            
            # שלב 2: סריקת eBay (גרסה משופרת)
            try:
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                prices = []
                for item in soup.find_all('span', {'class': 's-item__price'}):
                    p = item.get_text().replace('$', '').replace(',', '').split(' ')[0]
                    try: prices.append(float(p))
                    except: continue
                
                if prices:
                    avg_usd = sum(prices[1:6]) / len(prices[1:6]) if len(prices) > 1 else prices[0]
                    st.success(f"💰 הערכת שווי: ₪{avg_usd * 3.72:,.2f}")
                    st.metric("מחיר דולרי ממוצע", f"${avg_usd:.2f}")
                else:
                    st.error("לא נמצאו מכירות אחרונות ב-eBay. נסה לדייק את השם.")
            except:
                st.error("שגיאה בגישה לנתוני eBay.")
