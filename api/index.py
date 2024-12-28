from http.server import BaseHTTPRequestHandler
import requests
import json

from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # Parse the request URL to extract the query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Extract the target URL from the query parameters
        target_url = query_params.get('url', [''])[0]

        if not target_url:
            # If no target URL provided, return 204 No Content
            self.send_response(204)
            self.end_headers()
            return

        try:
            # Forward the request to the target URL
            response = requests.get(target_url)

            if response.status_code == 200:
                self.send_response(200)
                self.send_header('Content-type', 'application/pdf')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.content)

                # Try to decode the response as JSON
                # try:
                #     json_data = response.json()
                #     # If successful, return the JSON response with a 200 OK status
                #     self.send_response(200)
                #     self.send_header('Content-type', 'application/json')
                #     self.send_header('Access-Control-Allow-Origin', '*')
                #     self.end_headers()
                #     self.wfile.write(json.dumps(json_data).encode('utf-8'))
                # except ValueError:
                #     # If decoding as JSON fails, return the response as plain text
                #     self.send_response(200)
                #     self.send_header('Content-type', 'application/json')
                #     self.send_header('Access-Control-Allow-Origin', '*')
                #     self.end_headers()
                #     self.wfile.write(json.dumps({'data': response.text}).encode('utf-8'))
            else:
                # If GET request failed, return 502 Bad Gateway
                self.send_response(502)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Failed to get from {target_url}, response: {response.content}'}).encode('utf-8'))
        except Exception as e:
            # If any other error occurs, return 500 Internal Server Error
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Proxy error: {str(e)}'}).encode('utf-8'))
