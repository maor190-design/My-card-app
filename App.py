import streamlit as st
import requests

# כותרת האפליקציה
st.set_page_config(page_title="מעריך קלפי ספורט", page_icon="🏀")
st.title("🏆 מעריך שווי קלפי ספורט (Last Sold)")
st.subheader("סרוק קלף וקבל מחיר שוק בשקלים")

# העלאת תמונה
uploaded_file = st.file_uploader("העלה תמונה של הקלף (או לוט קלפים)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="הקלף שלך", use_column_width=True)
    st.warning("🔄 מנתח את הקלף ומחפש מכירות אחרונות ב-eBay ו-130Point...")

    # כאן אנחנו מגדירים את פונקציית החיפוש (כרגע הדמיה של התוצאה)
    # בשלב הבא נחבר את זה למנוע חיפוש אמיתי
    def get_sports_card_price(card_details):
        # מנוע החיפוש יתמקד ב- 'Sold Items' בלבד
        # דוגמה לנתונים שיחזרו:
        fake_results = {
            "card_name": "LeBron James 2003 Topps Chrome #111",
            "last_sold_prices": [1200, 1150, 1300], # מחירים בדולר מאיביי
            "currency": "USD"
        }
        avg_price_usd = sum(fake_results["last_sold_prices"]) / len(fake_results["last_sold_prices"])
        
        # המרה לשקלים (שער נוכחי משוער)
        ils_price = avg_price_usd * 3.7
        return fake_results["card_name"], ils_price

    # הצגת התוצאה
    name, price = get_sports_card_price("Card identified from image")
    
    st.success(f"✅ זוהה: **{name}**")
    st.metric(label="הערכת שווי לוט/קלף (בשקלים)", value=f"₪{price:,.2f}")
    st.info("המחיר מבוסס על ממוצע מכירות אחרונות (Last Sold) בלבד.")

# הסבר על האתרים
st.markdown("---")
st.write("**מקורות מידע:** eBay Sold Listings, 130Point, TCG (לפי הצורך)")
