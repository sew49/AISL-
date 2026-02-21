import requests

URL = "http://192.168.8.74:5000/api/employees"

employees = [
    "Peter Nyawade", "Tonny Odongo", "Eric Kamau", "Kelvin Omondi", 
    "Ottawa Kinsvoscko", "Riziki Merriment", "Margaret Muthoni", 
    "Oscar Akala", "Craig Mwendwa", "Mark Okere", "Joash Amutavi", 
    "Julius Singila", "Wesonga Wilfred", "Innocent Mogaka", 
    "Nelson Kasiki", "Fredrick Owino", "Bentah Akinyi", "Mahmood Mir", 
    "Sharon Akinyi", "Kipsang Kipsetim", "Dennis Kipkemoi", "David Makau"
]

def add_employees():
    for name in employees:
        payload = {"name": name, "annual_leave_entitlement": 21}
        try:
            response = requests.post(URL, json=payload)
            if response.status_code == 201:
                print(f"✅ Added: {name}")
            else:
                print(f"❌ Failed {name}: {response.text}")
        except Exception as e:
            print(f"⚠️ Error connecting to server: {e}")

if __name__ == "__main__":
    add_employees()
