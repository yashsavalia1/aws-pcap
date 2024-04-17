from vanilla_order_api import VanillaOrderAPIServer

from flask import Flask, request, jsonify

class EncryptedOrderAPIServer(VanillaOrderAPIServer):
    def __init__(self, port):
        super().__init__(port)
        self.ssl_cert_path = "certificate/certificate.pem"
        self.ssl_key_path = "certificate/key.pem"

    def run(self):
        self.app.run(port=self.port, ssl_context=(self.ssl_cert_path, self.ssl_key_path))  