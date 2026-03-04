import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# הגדרות דף
st.set_page_config(page_title="מעריך קלפי ספורט", page_icon="🏀")

def get_ebay_sold_prices(card_name):
    """פונקציה שסורקת את איביי ומחזירה מחירי מכירות אחרונות"""
    # יצירת כתובת חיפוש לאיביי עם פילטר של 'Sold' ו-'Completed'
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={card_name.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # חיפוש אלמנטים של מחירים בדף
    price_elements = soup.find_all('span', {'class': 's-item__price'})
    
    prices = []
    for item in price_elements:
        # ניקוי המחיר מסימני דולר ופסיקים
        price_text = item.get_text().replace('$', '').replace(',', '')
        # טיפול בטווח מחירים (למשל $10 to $20)
        if 'to' in price_text:
            price_text = price_text.split('to')[0]
        
        try:
            prices.append(float(re.findall(r"[-+]?\d*\.\d+|\d+", price_text)[0]))
        except:
            continue
            
    return prices[:10] # מחזיר את 10 התוצאות האחרונות

# --- ממשק המשתמש ---
st.title("🏆 מעריך שווי (Last Sold)")
st.write("העלה תמונה והזן את שם הקלף לחיפוש מדויק ב-eBay")

uploaded_file = st.file_uploader("העלה תמונה...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, width=300)
    
    # תיבת טקסט להזנת שם הקלף (זמני עד שנחבר זיהוי תמונה אוטומטי מלא)
    card_query = st.text_input("איזה קלף מופיע בתמונה? (למשל: Stephen Curry 2009 Topps #101)")
    
    if st.button("חשב שווי שוק"):
        if card_query:
            with st.spinner('מחפש מכירות אחרונות באיביי...'):
                sold_prices = get_ebay_sold_prices(card_query)
                
                if sold_prices:
                    avg_usd = sum(sold_prices) / len(sold_prices)
                    ils_price = avg_usd * 3.72 # שער חליפין משוער
                    
                    st.success(f"נמצאו {len(sold_prices)} מכירות אחרונות!")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("מחיר ממוצע (USD)", f"${avg_usd:.2f}")
                    col2.metric("מחיר בשקלים (ILS)", f"₪{ils_price:.2f}")
                    
                    st.write("### מחירי מכירות אחרונות שנמצאו:")
                    for p in sold_prices:
                        st.write(f"- ${p:.2f}")
                else:
                    st.error("לא נמצאו מכירות אחרונות עבור הקלף הזה. נסה לדייק את השם.")
        else:
            st.warning("בבקשה רשום את שם הקלף כדי שאוכל לחפש.")

st.markdown("---")
st.caption("הנתונים נשלפים בזמן אמת מ-eBay Sold Listings")
