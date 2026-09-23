import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
all_data = [] # transactions ane peru marchanu

# Validation - logic same but style different
def validate_amount(amt):
    if amt > 0:
        return True
    return False

def validate_category(cat):
    if len(cat.strip()) == 0:
        return False
    return True

def validate_date(d_str):
    try:
        datetime.strptime(d_str, "%Y-%m-%d")
        return True
    except:
        return False

def get_all_transactions():
    return all_data

def get_monthly_summary():
    monthly = {}
    for item in all_data:
        m_key = item["date"][0:7] # [:7] place lo [0:7] rasanu
        if m_key not in monthly:
            monthly[m_key] = {"income": 0, "expense": 0}

        if item["type"] == "income":
            monthly[m_key]["income"] = monthly[m_key]["income"] + item["amount"]
        else:
            monthly[m_key]["expense"] = monthly[m_key]["expense"] + item["amount"]
    return monthly

def create_transaction(amt, t_type, cat, desc, d_str):
    new_trans = {
        "id": int(datetime.now().timestamp()),
        "type": t_type.lower(),
        "amount": float(amt),
        "category": cat.strip(),
        "description": desc.strip(),
        "date": d_str,
        "created_at": datetime.now().isoformat()
    }
    return new_trans

def add_transaction(amt, t_type, cat, desc, d_str):
    if validate_amount(amt) == False:
        return False
    if validate_category(cat) == False:
        return False
    if validate_date(d_str) == False:
        return False

    trans = create_transaction(amt, t_type, cat, desc, d_str)
    all_data.append(trans)
    return True

def save_transactions():
    save_data = {
        "transactions": get_all_transactions(),
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_transactions": len(all_data)
        }
    }
    with open("transactions.json", "w") as f:
        json.dump(save_data, f, indent=2)
    return True

def load_transactions():
    global all_data
    if os.path.exists("transactions.json"):
        try:
            with open("transactions.json", "r") as f:
                file_data = json.load(f)
                all_data = file_data.get("transactions", [])
        except:
            all_data = []
    else:
        all_data = []

def calculate_total_income():
    income_total = 0
    for i in all_data:
        if i["type"] == "income":
            income_total += i["amount"]
    return income_total

def calculate_total_expenses():
    expense_total = 0
    for i in all_data:
        if i["type"] == "expense":
            expense_total += i["amount"]
    return expense_total

def calculate_net_balance():
    return calculate_total_income() - calculate_total_expenses()

def get_exchange_rate(from_cur, to_cur):
    key = os.getenv("EXCHANGE_RATE_API_KEY")
    api_url = f'https://v6.exchangerate-api.com/v6/{key}/latest/{from_cur}'
    try:
        res = requests.get(api_url, timeout=5)
        res_data = res.json()
        exch_rate = res_data["conversion_rates"][to_cur]
        return float(exch_rate)
    except:
        print("Error fetching exchange rate.")
        return None

def draw_monthly_bar_chart():
    summary_data = get_monthly_summary()
    m_names = {"01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun","07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec"}
    print("\n=== Monthly Report ===")
    for m_key in sorted(summary_data.keys()):
        y, m = m_key.split("-")
        print(f"{m_names[m]} :")
        print(f"Income : {summary_data[m_key]['income']}")
        print(f"Expense : {summary_data[m_key]['expense']}")
        print("------------------")

def delete_transaction(t_id):
    global all_data
    for item in all_data:
        if item["id"] == t_id:
            all_data.remove(item)
            save_transactions()
            return True
    return False

def filter_transactions(cat_name):
    out = []
    for item in all_data:
        if item["category"].lower() == cat_name.lower():
            out.append(item)
    return out

def show_dashboard():
    print("\n=== DASHBOARD ===")
    print("Income :", calculate_total_income())
    print("Expense:", calculate_total_expenses())
    print("Balance:", calculate_net_balance())

def display_menu():
    print("=== Finance Tracker ===")
    print("1. Add Transaction")
    print("2. Delete Transactions")
    print("3. View All Transactions")
    print("4. Filter Transactions")
    print("5. Reports")
    print("6. Currency Conversion")
    print("7. Charts")
    print("8. Dashboard")
    print("9. Exit")
    user_choice = input("Enter your choice (1-9):")
    return user_choice

if __name__ == "__main__":
    load_transactions()
    while True:
        choice = display_menu()
        if choice == "1":
            amount = float(input("Enter amount: "))
            trans_type = input("Enter type (income/expense): ")
            category = input("Enter category: ")
            description = input("Enter description: ")
            date_str = input("Enter date (YYYY-MM-DD): ")
            if add_transaction(amount, trans_type, category, description, date_str):
                save_transactions()
                print("Transaction added successfully!")
            else:
                print("Invalid transaction data!")
        elif choice == "2":
            transaction_id = int(input("Enter Transaction ID to delete: "))
            if delete_transaction(transaction_id):
                print("Transaction deleted successfully!")
            else:
                print("Transaction not found.")
        elif choice == "3":
            all_trans = get_all_transactions()
            if len(all_trans) == 0:
                print("No transactions found.")
            else:
                for trans in all_trans:
                    print(trans)
        elif choice == "4":
            category = input("Enter category to filter: ")
            filtered = filter_transactions(category)
            if filtered:
                for trans in filtered:
                    print(trans)
            else:
                print("No transactions found.")
        elif choice == "5":
            inc = calculate_total_income()
            exp = calculate_total_expenses()
            bal = calculate_net_balance()
            print("Total Income:", inc)
            print("Total Expenses:", exp)
            print("Net Balance:", bal)
            if bal > 0:
                print("Status: Profit 👍")
            elif bal < 0:
                print("Status: Loss ⚠️")
            else:
                print("Status: Break-even")
        elif choice == "6":
            print("\n=== Currency Exchange Rate ===")
            from_currency = input("From Currency: ").upper()
            to_currency = input("To Currency: ").upper()
            rate = get_exchange_rate(from_currency, to_currency)
            if rate:
                print(f"\n1 {from_currency} = {rate:.2f} {to_currency}")
            else:
                print("Unable to get exchange rate.")
        elif choice == "7":
            draw_monthly_bar_chart()
        elif choice == "8":
            show_dashboard()
        elif choice == "9":
            print("Thank you for using Finance Tracker!")
            break
        else:
            print("Invalid choice. Please enter 1-9.")