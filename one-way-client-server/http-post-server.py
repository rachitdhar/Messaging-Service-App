import requests

ipaddr = '' # enter the ip address of receiver here
url = f'http://{ipaddr}:8080/get-msg'

def sendMsg():
    while True:
        msgInput = input()

        if msgInput.lower() == "exit" or msgInput.lower() == "quit":
            break

        payload = {
            'sentBy':'rd',
            'msg':msgInput
        }
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print('POST request sent successfully.')
                print('Response:')
                print(response.text)  # Print response data (if any)
            else:
                print(f'Failed to send POST request. Status code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            print('Error sending POST request:', e)

def main():
    print("Message sender service initiated.\n")
    sendMsg()
    print("End of service.")

if __name__ == '__main__':
    main()
    
