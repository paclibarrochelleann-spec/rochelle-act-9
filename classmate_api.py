import requests

url = "https://noemedefacto-1.onrender.com/student"

try:
    response = requests.get(url, timeout=60)

    print("===== CLASSMATE API =====")
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("Classmate's Data:")

        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print(data)

    else:
        print("Request failed.")
        print(response.text)

except requests.RequestException as error:
    print("Connection error:", error)
except ValueError:
    print("The response is not valid JSON.")
