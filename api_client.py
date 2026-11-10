
import requests

url = "https://rochelleannpaclibar-1.onrender.com/course"

try:
    response = requests.get(url, timeout=60)

    print("===== COURSE INFORMATION =====")
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("Course Data:", data)

        for key, value in data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        print("Request failed.")
        print(response.text)

except requests.RequestException as error:
    print("Connection error:", error)
