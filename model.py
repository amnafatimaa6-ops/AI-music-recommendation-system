import re
import requests

CURRENCY_INFO = {
    "PKR": {"name":"Pakistani Rupee","country":"Pakistan","strength":2},
    "INR": {"name":"Indian Rupee","country":"India","strength":3},
    "USD": {"name":"US Dollar","country":"United States","strength":9},
    "EUR": {"name":"Euro","country":"Eurozone","strength":8},
    "GBP": {"name":"British Pound","country":"United Kingdom","strength":9},
    "JPY": {"name":"Japanese Yen","country":"Japan","strength":7},
    "AUD": {"name":"Australian Dollar","country":"Australia","strength":8},
    "CAD": {"name":"Canadian Dollar","country":"Canada","strength":8},
    "CNY": {"name":"Chinese Yuan","country":"China","strength":6},
    "CHF": {"name":"Swiss Franc","country":"Switzerland","strength":10},
    "RON": {"name":"Romanian Leu","country":"Romania","strength":4}
}

# 🌐 API
def get_rate(from_c, to_c):
    url = f"https://open.er-api.com/v6/latest/{from_c}"
    data = requests.get(url).json()
    return data["rates"][to_c]

# 🧠 PARSER (flexible)
def parse_query(text):
    text = text.lower()

    amount = re.search(r"\d+(\.\d+)?", text)
    if not amount:
        return None

    amount = float(amount.group())

    text = text.replace("convert", "").replace("to", " ")
    words = re.findall(r"[a-zA-Z]+", text)

    found = []
    for w in words:
        w = w.upper()
        if w in CURRENCY_INFO:
            found.append(w)

    found = list(dict.fromkeys(found))

    if len(found) < 2:
        return None

    return amount, found[0], found[1]

# 💰 BUYING POWER (safe default always exists)
def buying_power(amount, from_c):
    data = CURRENCY_INFO[from_c]

    return [
        f"☕ Coffee: {round(amount * 0.3, 2)} units",
        f"🍔 Burgers: {round(amount * 0.2, 2)} units",
        f"🏠 Rent: {round(amount * 0.01, 4)} days"
    ]

# 💱 MAIN FUNCTION (NEVER FAILS STRUCTURE)
def convert(query):
    parsed = parse_query(query)

    if not parsed:
        return {
            "error": "❌ Invalid input. Try: 100 PKR to USD"
        }

    amount, from_c, to_c = parsed

    try:
        rate = get_rate(from_c, to_c)
    except:
        rate = 0

    result = round(amount * rate, 2)

    f = CURRENCY_INFO[from_c]
    t = CURRENCY_INFO[to_c]

    return {
        "from": from_c,
        "to": to_c,
        "amount": amount,
        "rate": rate,
        "result": result,

        "insight": [
            f"1 {from_c} = {rate:.6f} {to_c}",
            f"{f['name']} ({f['country']}) → {t['name']} ({t['country']})"
        ],

        # 🔥 ALWAYS PRESENT (fixes KeyError)
        "buying_power": buying_power(amount, from_c)
    }

# 🌍 MAP
def get_country_strength_map():
    return {v["country"]: v["strength"] for v in CURRENCY_INFO.values()}
