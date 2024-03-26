from abstract_order_api import OrderAPIServer

from flask import Flask, request, jsonify

class VanillaOrderAPIServer(OrderAPIServer):
    def __init__(self, port):
        self.port = port
        self.app = Flask(__name__)
        self.register_routes()

    def run(self):
        self.app.run(port=self.port)  # Runs the server on port 5000

    def register_routes(self):
        @self.app.route('/order', methods=['POST'])
        def receive_data_confirmation():
            data = request.json  
            # print(data)  
            return jsonify({"message": "Data received successfully", "yourData": data}), 200

        @self.app.errorhandler(400)
        def bad_request(error):
            print("A 400 Bad Request error occurred: {}".format(error))
            return jsonify({"error": "Bad request"}), 400
