import requests
header = {'Cookie': 'csrftoken=QrWOFhuJg1NSjHeZfXgIyreagbzdxizJ3In7QcFKjZvZ3LONaUH78gXXdG42QUXf; sessionid=p7kiu5p2zy65521sz34pvz48htfe1xve'}
for i in range(1000, 2000):
    url = "http://47.100.248.217:8000/insert/?area=hello&type=8&phone="+ str(i)
    response = requests.get(url, headers=header)
    print(response, i)