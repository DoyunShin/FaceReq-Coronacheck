#! /usr/bin/python

# Imports
import requests

def send_simple_message():
    print("I am sending an email.")
    return requests.post(
        "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
        auth=("api", "YOUR_API_KEY"),
        data={"from": 'hello@example.com',
            "subject": "Visitor Alert",
            "html": "<html> Y의 온도가 높게 측정됩니다.보건용 온도계로 다시 측정하시기 바랍니다.. </html>"})
                      
request = send_simple_message()
print ('Status: '+format(request.status_code))
print ('Body:'+ format(request.text))
