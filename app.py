from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json
import socket
from colorama import Fore, Style
import threading as th
import sys

PORT = 8080
EXIT_APP = False
LOG_FILE_NAME = 'app_logs.txt'


def handle_printing_received_message(sent_by, received_msg):
    sys.stdout.write("\0337")           # Save the current cursor position
    sys.stdout.write("\033[0G")         # Move to the beginning of the line
    sys.stdout.write(Fore.GREEN + f"~{sent_by} : " + Style.RESET_ALL + received_msg + "\n")
    sys.stdout.write("\0338")           # Restore the cursor position
    sys.stdout.write("\033[B")          # Move the cursor down one line
    sys.stdout.flush()


class RequestHandler(BaseHTTPRequestHandler):
    # overriding this method to redirect the logs to the log file
    def log_message(self, format, *args):
        with open(LOG_FILE_NAME, 'a') as flogs:
            flogs.write(f"{self.address_string()} - - [{self.log_date_time_string()}] {format % args}")
            flogs.write("\n\n")

    def do_POST(self):
        # Determine the length of the incoming data
        content_length = int(self.headers['Content-Length'])
        
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')
        
        try:
            data = json.loads(post_data)
            handle_printing_received_message(data['sentBy'], data['msg'])
            
            # Send a response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            message = "CONNECTION SUCCESSFUL" if (data['sentBy'] == 'APP_CONN_CHECK') else "POST request was successful"
            response = json.dumps({'status': 'SUCCESS', 'message': message})
            self.wfile.write(response.encode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'status': 'JSONDecodeError', 'message': 'Invalid JSON'})
            self.wfile.write(response.encode('utf-8'))
        except ConnectionRefusedError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'status': 'ConnectionRefusedError', 'message': 'Network connection attempt refused by target machine'})
            self.wfile.write(response.encode('utf-8'))
        except TimeoutError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'status': 'TimeoutError', 'message': 'Connection timed out. Server did not respond in a timely manner'})
            self.wfile.write(response.encode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'status': 'Error', 'message': 'Some unknown exception has occurred.'})
            self.wfile.write(response.encode('utf-8'))


def sender(username, ipaddr):
    global EXIT_APP

    while True:
        msgInput = input(Fore.LIGHTMAGENTA_EX + "YOU ~" + username + " : " + Style.RESET_ALL)

        if msgInput == "!q":
            break
        elif msgInput == "!e":
            EXIT_APP = True
            break

        payload = {'sentBy':username,'msg':msgInput}
        url = f"http://{ipaddr}:{PORT}/get-msg"

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            response = json.loads(response.text)
            log_data = (f"Receiver ipaddress: {ipaddr}\nStatus: {response['status']}\nMessage: {response['message']}")
            
            with open(LOG_FILE_NAME, 'a') as flogs:
                flogs.write(log_data)
                flogs.write("\n\n")
        except requests.exceptions.RequestException as e:
            print(Fore.RED + 'Error sending POST request' + Style.RESET_ALL)


def receiver():
    hostname = socket.gethostname()
    server_address = (socket.gethostbyname(hostname), PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()


def displayHeading():
    print(Fore.CYAN + "********** Welcome to Messager! **********" + Style.RESET_ALL)
    print()
    print("You must enter the IPv4 address of the computer to which you want to send the message.")
    print("Preferably the other user should also be using this app in order to receive the message.")
    print()
    print(Fore.YELLOW + "IMPORTANT! : " + Style.RESET_ALL + "Type \"!q\" to quit sending to the current entered ipaddress.")
    print(Fore.YELLOW + "IMPORTANT! : " + Style.RESET_ALL + "Type \"!e\" to exit the app.")
    print()


def main():
    global EXIT_APP
    displayHeading()
    username = input(Fore.LIGHTMAGENTA_EX + "Enter a username of your choice (will be visible to message receivers): " + Style.RESET_ALL)

    while username == "APP_CONN_CHECK":
        username = input(Fore.RED + "Invalid username. Please enter another username." + Style.RESET_ALL)
    
    receiver_thread = th.Thread(target=receiver)
    receiver_thread.start()

    while (not EXIT_APP):
        ipaddr = input(Fore.CYAN + "Enter ipaddress of the user you want to send messages to: " + Style.RESET_ALL)
        
        # checking if ipaddress is valid
        url = f"http://{ipaddr}:{PORT}/get-msg"
        
        try:
            response = requests.post(url, json={'sentBy':'APP_CONN_CHECK','msg':'Testing connection.'}, headers={"Content-Type": "application/json"})
            response = json.loads(response.text)
            log_data = (f"Receiver ipaddress: {ipaddr}\nStatus: {response['status']}\nMessage: {response['message']}")
            
            if response['status'] == "CONNECTION SUCCESSFUL":
                print(Fore.GREEN + "Connection Successful." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "Connected, but did not receive confirmatory response." + Style.RESET_ALL)

            print()

            with open(LOG_FILE_NAME, 'a') as flogs:
                flogs.write(log_data)
                flogs.write("\n\n")
        except socket.gaierror:
            print(Fore.RED + "IP address could not be resolved. Try again." + Style.RESET_ALL)

            with open(LOG_FILE_NAME, 'a') as flogs:
                flogs.write(f"Receiver ipaddress: {ipaddr}\nIP address could not be resolved.")
                flogs.write("\n\n")
            continue
        except Exception:
            print(Fore.RED + "An error occurred while trying to connect. Try again." + Style.RESET_ALL)
            
            with open(LOG_FILE_NAME, 'a') as flogs:
                flogs.write(f"Receiver ipaddress: {ipaddr}\nAn error occurred while trying to connect.")
                flogs.write("\n\n")
            continue
        
        sender_thread = th.Thread(target=sender, args=(username, ipaddr))
        sender_thread.start()

        #wait for sender thread to complete
        sender_thread.join()
        print()

    # wait for receiver thread to complete
    receiver_thread.join()

    with open(LOG_FILE_NAME, 'a') as flogs:
        flogs.write("------------ SESSION OVER ------------")
        flogs.write("\n\n")

    print(Fore.CYAN + "Message Service has been exited. Press any key to close this window..." + Style.RESET_ALL)
    input()


if __name__ == '__main__':
    main()