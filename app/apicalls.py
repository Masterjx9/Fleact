import requests

def get_fake_data():
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    if response.status_code == 200:
        return {
            "reactiveActions": [
                {
                "action": "if-else",
                "value": False,
                "targetValue": True
            },
                {
                    "action": "update-content",
                    "content": response.json()[0]["id"]
                }
                ]
        }
    else:
        return {
            "action": "update-content",
            "target": "div-loading",
            "content": "Failed to fetch data.",
        }
