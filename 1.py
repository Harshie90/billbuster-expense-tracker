import streamlit as st
import os
import pandas as pd

#USER AUTHENTICATION SYSTEM
USER_DB = "users.csv"

def init_user_db():
    if not os.path.exists(USER_DB):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USER_DB, index=False)

def load_users():
    init_user_db()
    return pd.read_csv(USER_DB)

def add_user(username, password):
    df = load_users()
    if username in df["username"].values:
        return False
    df.loc[len(df)] = [username, password]
    df.to_csv(USER_DB, index=False)
    return True

#SESSION SETUP
st.set_page_config(page_title="BillBuster", layout="centered")
st.markdown("""
    <style>
    .stApp {
        background-image: url("file:///C:/Users/Harshita/Documents/project/background_photo.jpg");

        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.5);
    }

    .welcome-text {
        background: rgba(0, 0, 0, 0.6);
        padding: 25px;
        border-radius: 12px;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)





if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def go_to_signup():
    st.session_state.show_signup = True

def go_to_login():
    st.session_state.show_signup = False

#LOGIN + SIGN UP PAGE
if not st.session_state.logged_in:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 0px;'>
            <h2>Welcome to BillBuster</h2>
            <img src='logo.png' width='160' style='margin-top: -10px; margin-bottom: 10px;' />
        </div>
    """, unsafe_allow_html=True)

    #     .center-box {
    #         display: flex;
    #         flex-direction: column;
    #         align-items: center;
    #         justify-content: center;
    #         max-width: 400px;
    #         margin: auto;
    #         padding: 2rem;
    #         background-color: rgba(240,240,240,0.1);
    #         border-radius: 12px;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="center-box">', unsafe_allow_html=True)

        if not st.session_state.show_signup:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Log In"):
                users_df = load_users()
                if username in users_df["username"].values:
                    if users_df[users_df["username"] == username]["password"].values[0] == password:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("Username not found.")

            st.markdown("Don't have an account?")
            if st.button("Sign Up"):
                go_to_signup()

        else:
            new_username = st.text_input("Choose a Username")
            new_password = st.text_input("Choose a Password", type="password")

            if st.button("Create Account"):
                if add_user(new_username, new_password):
                    st.success(f"Account created for {new_username}!")
                    go_to_login()
                else:
                    st.error("Username already exists. Try another.")

            st.markdown("Already have an account?")
            if st.button("Back to Login"):
                go_to_login()

        st.markdown('</div>', unsafe_allow_html=True)

#MAIN APP
def main_app():
    import matplotlib.pyplot as plt
    import pytesseract
    import io
    import re
    import numpy as np
    import cv2
    from PIL import Image
    import datetime

    st.set_page_config(page_title="BillBuster - Smart Expense Tracker", layout="wide")

    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe" 

    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://images.pexels.com/photos/9668535/pexels-photo-9668535.jpeg");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: white;
        }
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.5);
        }
        .welcome-text {
            background: rgba(0, 0, 0, 0.6);
            padding: 25px;
            border-radius: 12px;
            font-size: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Sidebar")
    currency = st.sidebar.radio("Currency", ["INR ₹", "USD $"])
    selection = st.sidebar.radio("Go to", [
        "1.Home Dashboard",
        "2.Upload Transactions",
        "3.Cash Expenses",
        "4.Add Manually",
        "5.Goals",
        "6.Reminders",
        "7.Spend Summary"
        
    ])
    

    st.title(" BillBuster - Smart Expense Tracker")

    def extract_text_tesseract(image_bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert('L')
        image = image.resize((image.width * 2, image.height * 2))
        img_np = np.array(image)
        _, binary = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
        processed_img = Image.fromarray(binary)
        text = pytesseract.image_to_string(processed_img)
        return text
    
    def extract_final_amount(text):
        import re

        lines = text.split('\n')
        final_keywords = [
            "grand total", "Total Amount(In Figures:)", "total", "balance",
            "amount payable", "net payable", "final amount",
            "pay", "to be paid", "to pay", "due", "amount due"
        ]

        # First: Try to find amount near known keywords
        for line in reversed(lines):
            lower_line = line.lower()
            for keyword in final_keywords:
                if keyword in lower_line:
                    match = re.search(r'[\d,]+\.?\d*', line)
                    if match:
                        amt_str = match.group().replace(',', '')
                        try:
                            return float(amt_str)
                        except:
                            continue

        # Second: Fallback to valid-looking currency numbers only
        amounts = []
        for line in lines:
            matches = re.findall(r'[\d,]+\.?\d*', line)
            for amt in matches:
                try:
                    amt_clean = float(amt.replace(',', ''))
                    # Filter: Accept only amounts that make sense (not phone numbers)
                    if amt_clean > 50 and amt_clean < 200000:  # Accept ₹50 to ₹2 lakh
                        amounts.append(amt_clean)
                except:
                    continue

        if amounts:
            return max(amounts)
        return None


    if selection == "1.Home Dashboard":
        st.subheader("📍Welcome to BillBuster")
        st.markdown("""
        <div class='welcome-text'>
            Track all your:<br><br>
            ** Upload Trasactions<br>
            ** Goals<br>
            ** Reminders<br>
            **Cash Receipt<br>
            ** Spend Summary<br>
            Use the sidebar to explore.
        </div>
        """, unsafe_allow_html=True)


    elif selection == "2.Upload Transactions":
        st.subheader("Upload Transactions (Bank PDF, CSV or Receipt Image)")
        total_expense = 0

        pdf = st.file_uploader("📄 Upload Bank Statement (PDF)", type="pdf")
        csv = st.file_uploader("📊 Upload Transaction CSV File", type="csv")
        receipt = st.file_uploader("🧾 Upload Receipt Image", type=["png", "jpg", "jpeg"])

        if pdf:
            import pdfplumber
            try:
                transactions = []
                with pdfplumber.open(pdf) as pdf_doc:
                    for page in pdf_doc.pages:
                        text = page.extract_text()
                        for line in text.split('\n'):
                            match = re.match(r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+([\d,]+\.\d{2})$', line)
                            if match:
                                date, vendor, amount = match.groups()
                                amt = float(amount.replace(',', ''))
                                transactions.append({"Date": date, "Vendor": vendor, "Amount": amt})
                                total_expense += amt
                df = pd.DataFrame(transactions)
                st.success("✅ Transactions from PDF extracted!")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

        elif csv:
            df = None
            try:
                df = pd.read_csv(csv, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv, encoding="latin1")
                except Exception as e:
                    st.error(f"CSV Read Error: {e}")

            if df is not None:
                if "Amount" in df.columns:
                    total_expense += df["Amount"].sum()
                    st.success("✅ CSV uploaded successfully!")
                    st.dataframe(df)
                else:
                    st.warning("CSV must contain an 'Amount' column.")


        elif receipt:
            try:
                text = extract_text_tesseract(receipt.read())
                st.code(text)
                amount = extract_final_amount(text)
                if amount:
                    st.success(f"Detected Final Amount: ₹{amount}")
                    total_expense+=amount
                else:
                    st.warning("No final amount detected.")

            except Exception as e:
                st.error(f"Error: {e}")

        if total_expense:
            if "bank_expense" not in st.session_state:
                st.session_state.bank_expense = 0
            st.session_state.bank_expense += total_expense
            st.success(f"Total Expense Uploaded: ₹{total_expense}")

    elif selection == "3.Cash Expenses":
        st.subheader("🧾 Upload Receipt Image")
        image = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        if image:
            st.image(image)
            try:
                text = extract_text_tesseract(image.read())
                st.code(text)
                amount = extract_final_amount(text)
                if amount:
                    st.success(f"Detected Final Amount: ₹{amount}")
                    if "cash_expense" not in st.session_state:
                        st.session_state.cash_expense = 0
                    st.session_state.cash_expense += amount


                else:
                    st.warning("No final amount detected.")

            except Exception as e:
                st.error(f"Error: {e}")

    elif selection == "4.Add Manually":
        st.subheader("➕ Add Your Expense Here")
        if "manual_expenses" not in st.session_state:
            st.session_state.manual_expenses = []

        with st.form("add_expense"):
            date = st.date_input("Date", value=datetime.date.today())
            category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Other"])
            amount = st.number_input("Amount", min_value=0.0)
            desc = st.text_area("Description")
            submitted = st.form_submit_button("Add Expense")
            if submitted:
                st.session_state.manual_expenses.append({
                    "Date": str(date), "Category": category, "Amount": amount, "Description": desc
                })
                st.success("Expense added!")

        if st.session_state.manual_expenses:
            df = pd.DataFrame(st.session_state.manual_expenses)
            st.dataframe(df)
    elif selection == "5.Goals":
        st.subheader("🎯 Savings Goals")

        if "goals" not in st.session_state:
            st.session_state.goals = []

        with st.form("goal_form"):
            goal_name = st.text_input("Goal Name (e.g., Buy Phone)")
            goal_amount = st.number_input("Goal Amount (e.g., ₹20000)", min_value=0.0)
            months = st.slider("Months to Achieve", 1, 24, 6)
            submitted = st.form_submit_button("Submit Goal")

            if submitted:
                if goal_name and goal_amount > 0:
                    per_month = goal_amount / months
                    st.session_state.goals.append({
                        "Goal": goal_name,
                        "Total Amount (₹)": goal_amount,
                        "Months": months,
                        "Monthly Saving (₹)": round(per_month, 2)
                    })
                    st.success(
                        f"Goal saved! Save ₹{round(per_month, 2)} per month for {months} months "
                        f"to achieve *{goal_name}*."
                    )
                else:
                    st.warning("Please enter a valid goal name and amount.")

        if st.session_state.goals:
            st.markdown("### 📝 Your Goals")
            st.dataframe(pd.DataFrame(st.session_state.goals))
    elif selection == "6.Reminders":
            REMINDER_FILE = "reminders.csv"

            def load_reminders():
                if os.path.exists(REMINDER_FILE):
                    return pd.read_csv(REMINDER_FILE)
                else:
                    return pd.DataFrame(columns=["username", "title", "datetime", "note"])

            def save_reminder(username, title, reminder_time, note):
                df = load_reminders()
                df.loc[len(df)] = [username, title, reminder_time, note]
                df.to_csv(REMINDER_FILE, index=False)

            import datetime
            st.subheader("🔔 Set a Reminder")

            with st.form("reminder_form_main"):
                title = st.text_input("Reminder Title")
                date = st.date_input("Select Date", value=datetime.date.today())
                time = st.time_input("Select Time", value=datetime.datetime.now().time())
                reminder_time = datetime.datetime.combine(date, time)
                note = st.text_area("Note (optional)")
                submitted = st.form_submit_button("Add Reminder")

                if submitted:
                    if title and reminder_time:
                        save_reminder(st.session_state["username"], title, reminder_time, note)
                        st.success("Reminder added successfully!")
                    else:
                        st.error("Please enter a title and valid time.")

            st.markdown("### 📋 Your Upcoming Reminders")
            reminders = load_reminders()
            user_reminders = reminders[reminders["username"] == st.session_state["username"]].copy()
            user_reminders["datetime"] = pd.to_datetime(user_reminders["datetime"])
            upcoming = user_reminders[user_reminders["datetime"] >= datetime.datetime.now()].sort_values("datetime")

            if upcoming.empty:
                st.info("No upcoming reminders.")
            else:
                for _, row in upcoming.iterrows():
                    st.markdown(f"🔔 <b>{row['title']}</b> — {row['datetime'].strftime('%Y-%m-%d %H:%M')}<br><i>{row['note']}</i>", unsafe_allow_html=True)



    elif selection == "7.Spend Summary":
            st.subheader("📊 Spend Summary")
            
            credit = st.session_state.get("bank_expense", 0)
            
            #Get manually added cash expenses
            manual_expenses = st.session_state.get("manual_expenses", [])
            cash_manual = sum(exp["Amount"] for exp in manual_expenses)
            
            #Get OCR detected cash expenses
            cash_ocr = st.session_state.get("cash_expense", 0)
            
            #Total cash
            cash = cash_manual + cash_ocr

            #Total
            total = credit + cash

            df = pd.DataFrame({
                "Mode": ["Bank/CSV/Receipts", "Cash (Manual)", "Cash (OCR Receipt)"],
                "Amount (₹)": [credit, cash_manual, cash_ocr]
            })
            st.dataframe(df)
            st.success(f"Total Spent: ₹{total}")

            fig, ax = plt.subplots()
            ax.pie(df["Amount (₹)"], labels=df["Mode"], autopct="%1.1f%%")
            st.pyplot(fig)

        #NEW SECTION: Reminders (Main Page Area)
        #Sidebar:Add Reminder
    
#LOGOUT
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

#RUN MAIN APP
if st.session_state.logged_in:
    st.sidebar.success(f" Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
    main_app()
