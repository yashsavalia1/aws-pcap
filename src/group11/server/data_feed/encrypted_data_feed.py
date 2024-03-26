from vanilla_data_feed import VanillaDataFeedServer

import ssl
import websockets

class EncryptedDataFeedServer(VanillaDataFeedServer):
    def create_server(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('certificate/certificate.pem', 'certificate/key.pem')
        return websockets.serve(self.worker, self.hostname, self.port, ssl=ssl_context)
