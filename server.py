from http.server import HTTPServer, BaseHTTPRequestHandler

import argparse
import json
import logging
import re
import urllib

logging.basicConfig(
    level=logging.INFO,
    # filename='server_log.txt',
    format='{asctime} {levelname} {filename}:{lineno}] {message}',
    style='{',
)


class ServerData:
    def __init__(self):
        self.profiles = {}
        self.location = {}
        self.re_ratio_id = re.compile(r'/ratios/(\d+)$')
        self.re_ratio_id_location = re.compile(r'/ratios/(\d+)/location$')


_server_data = ServerData()


def post_profile(url, get_post_data):
    match = re.match(_server_data.re_ratio_id, url.path)
    if not match:
        return False, 0
    uid = int(match.group(1))

    post_data = get_post_data()
    _server_data.profiles[uid] = post_data

    logging.info('new profile {}'.format(post_data))
    return True, 200


def post_location(url, get_post_data):
    match = re.match(_server_data.re_ratio_id_location, url.path)
    if not match:
        return False, 0
    uid = int(match.group(1))
    post_data = get_post_data()

    location = post_data.get('location', None)
    if location is None:
        logging.error('null location')
        return True, 403

    if not uid in _server_data.profiles:
        logging.error('NOT FOUND {}'.format(uid))
        return True, 404

    if not location in _server_data.profiles[uid].get('allowed_locations', []):
        logging.error('FORBIDDEN: {}'.format(location))
        return True, 403

    _server_data.location[uid] = location
    logging.info('Set location {} for user {}'.format(location, uid))
    return True, 200


def get_location(url):
    match = re.match(_server_data.re_ratio_id_location, url.path)
    if not match:
        return False, 0, None

    uid = int(match.group(1))
    if not uid in _server_data.location:
        logging.error('NOT FOUND {}'.format(uid))
        return True, 404, None

    location = _server_data.location[uid]
    logging.info('"location":" {}"'.format(location))

    data = json.dumps(dict(location=location)).encode()
    return True, 200, data


class Handler(BaseHTTPRequestHandler):
    def _send_code(self, code):
        self.send_response(code)
        self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)

        def get_post_data():
            length = int(self.headers['Content-Length'])
            try:
                data = json.loads(self.rfile.read(length).decode())
            except json.JSONDecodeError:
                # treat bad format data as empty
                return {}
            return data

        for handle in [post_profile, post_location]:
            match, code = handle(url, get_post_data)
            if match:
                self._send_code(code)
                return

        logging.error('NOT FOUND {}'.format(url.path))
        self._send_code(404)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)

        for handle in [get_location]:
            match, code, data = handle(url)
            if match:
                self._send_code(code)
                if code == 200:
                    self.wfile.write(data)
                return

        logging.error("NOT FOUND: {}".format(url))
        self._send_code(404)


def main():
    parser = argparse.ArgumentParser(description='Simple RESTful server')
    parser.add_argument('--port', default=8765, type=int)
    cli = parser.parse_args()

    address = ('', cli.port)
    server = HTTPServer(address, Handler)
    server.serve_forever()


if __name__ == '__main__':
    main()
