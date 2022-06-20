from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
from urllib.parse import urlparse, parse_qs
from threading import Thread
from ForecastRequestProcessor import process_forecast_request
import os
from configparser import ConfigParser

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read config file
config_object = ConfigParser()
config_object.read("server.cfg")
server_cfg = config_object["SERVERCONFIG"]

# Certificate and key path
KEY_FILE = server_cfg["KEY_FILE"]
CERT_FILE = server_cfg["CERT_FILE"]

# Server address and port
SERVER_ADDRESS = server_cfg["SERVER_ADDRESS"]
PORT = int(server_cfg["PORT"])

USER_TOKEN = config_object["AUTHCONFIG"]["USER_TOKEN"]

class SampleForecastServer(SimpleHTTPRequestHandler):
    """
    Sample external forecast server implementation for development. Do not use it in production systems!

    Args:
        SimpleHTTPRequestHandler (class): Python built in simple HTTP server class
    """

    def do_GET(self):

        if self.headers["Authorization"] is None:
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\'Test\'")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("No auth header received", "utf-8"))
            print("No auth header received")

        elif self.headers["Authorization"] == USER_TOKEN:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>Hello IBP.</p>", "utf-8"))

            path = urlparse(self.path).path

            if path == "/ibp/demand/ExternalForecastNotification":
                ext_req_id = int(
                    parse_qs(urlparse(self.path).query)["RequestID"][0])
                self.wfile.write(bytes(f"<p>External forecast notification received for id: \
                     {ext_req_id}. Processing triggered!</p>", "utf-8"))

                thread = Thread(target=process_forecast_request,
                                args=(ext_req_id,))
                thread.start()

            else:
                self.wfile.write(
                    bytes(f"<p>Invalid request: {self.path}</p>", "utf-8"))

            self.wfile.write(bytes("</body></html>", "utf-8"))
        else:
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\'Test\'")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(self.headers["Authorization"], "utf-8"))
            self.wfile.write(bytes("Unauthenticated", "utf-8"))
            print("Unauthenticated")


if __name__ == "__main__":
    webServer = HTTPServer((SERVER_ADDRESS, PORT), SampleForecastServer)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE,
                            keyfile=KEY_FILE)
    webServer.socket = context.wrap_socket(webServer.socket, server_side=True)

    print("Server started. Waiting for external notification requests.")
    try:
        webServer.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    webServer.server_close()
    print("Server stopped.")
