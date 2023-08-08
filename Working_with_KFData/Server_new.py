from http.server import HTTPServer, SimpleHTTPRequestHandler 
from urllib.parse import urlparse, parse_qs
from threading import Thread 
import os
from configparser import ConfigParser


#Custom functions
from RequestHandler import read_key_figure
from RequestHandler import writeKF

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read config file
config_object = ConfigParser()
config_object.read("server.cfg")
server_cfg = config_object["SERVERCONFIG"]

# Server address and port
SERVER_ADDRESS = server_cfg["SERVER_ADDRESS"]
PORT = int(server_cfg["PORT"])

class SampleKFServer(SimpleHTTPRequestHandler):
    """
    Sample server to extract key figures from IBP for development. Do not use it in production systems!

    Args:
        SimpleHTTPRequestHandler (class): Python built in simple HTTP server class
    """

    def do_GET(self):
        path = urlparse(self.path).path
        # TRIGGER TO READ KEY FIGURE DATA
        if path == "/ibp/sample/readKF":            
            readThread = Thread(target=read_key_figure)            
            readThread.start()
            readThread.join()
             
            self.send_response(200) 
            self.send_header("Content-type", "application/json") 
            self.end_headers()
        # TRIGGER TO WRITE DATA TO IBP
        if path == "/ibp/sample/writeKF":
            self.send_response(200) 
            self.send_header("Content-type", "application/json")
            self.end_headers() 
            writeThread = Thread(target=writeKF)
            writeThread.start() 


if __name__ == "__main__":
    webServer = HTTPServer((SERVER_ADDRESS, PORT), SampleKFServer)
    
    print("Server started. Waiting for key figure requests.")
    try:
        webServer.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    webServer.server_close()
    print("Server stopped.")
