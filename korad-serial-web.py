#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import argparse
import logging
import serial
from koradserial.koradserial import KoradSerial

power_supply = None

ACTIONS = {
    # url without '/action': function
    #'/output/on': lambda: print('on'),
    '/output/on': lambda: power_supply.output.on(),
    #'/output/off': lambda: print('off'),
    '/output/off': lambda: power_supply.output.off(),
    }


class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            with open('index.html') as file_index:
                self.wfile.write(bytes(file_index.read(), 'utf-8'))

        elif self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            with open('favicon.ico', 'rb') as file_favicon:
                self.wfile.write(file_favicon.read())

        elif self.path.startswith('/action/'):
            if self.path.replace('/action', '') in ACTIONS:
                ACTIONS[self.path.replace('/action', '')]()

            # Redirect the client to /
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        else:
            self.send_error(404)

        return


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=8008,
                        help='Web server port (default: 8008)')

    parser.add_argument('COM',
                        help='Serial port the source is attached to')

    global args
    args = parser.parse_args()

    logging.info('Connecting to the power supply')
    global power_supply
    try:
        power_supply = KoradSerial(args.COM)
    except serial.serialutil.SerialException:
        logging.error('Bad serial port: {}'.format(args.COM))
        sys.exit(1)

    logging.info('Power supply model: {}'.format(power_supply.model))
    logging.info('Power supply status: {}'.format(power_supply.status))

    try:
        server = HTTPServer(('', args.port), myHandler)
        print('Started httpserver on port {}'.format(args.port))
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()
        power_supply.close()


if __name__ == '__main__':
    main()
