from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Determine the length of the incoming data
        content_length = int(self.headers['Content-Length'])
        
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')
        
        try:
            data = json.loads(post_data)
            print("Received message.")
            print(f"{data['sentBy']}: {data['msg']}")

            # Send a response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = json.dumps({'status': 'success', 'received': data})
            self.wfile.write(response.encode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'status': 'error', 'message': 'Invalid JSON'})
            self.wfile.write(response.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    hostname = socket.gethostname()
    server_address = (socket.gethostbyname(hostname), port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
