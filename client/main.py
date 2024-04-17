
from vanilla_client import VanillaClient
from encrypted_client import EncryptedClient
from encrypted_data_feed_client import EncryptedDataFeedClient
from encrypted_order_api_client import EncryptedOrderAPIClient
from dotenv import load_dotenv
import os
import sys
import sslkeylog
import ssl

load_dotenv()
print(os.getenv("SSLKEYLOGFILE"))
print(ssl.OPENSSL_VERSION)
sslkeylog.set_keylog(os.environ.get('SSLKEYLOGFILE')) 

if len(sys.argv) != 2:
    print("Usage: python script.py [vanilla|df_en|oa_en|en]")
    sys.exit(1)  # Exit the script if no parameter or too many parameters are provided

parameter = sys.argv[1]  # Get the parameter
client = None

if parameter == "vanilla":
    client = VanillaClient("localhost", "6789", "127.0.0.1", "5000")
elif parameter == "df_en":
    client = EncryptedDataFeedClient("localhost", "6789", "127.0.0.1", "5000")
elif parameter == "oa_en":
    client = EncryptedOrderAPIClient("localhost", "6789", "127.0.0.1", "5000")
elif parameter == "en":
    client = EncryptedClient("localhost", "6789", "127.0.0.1", "5000")
else:
    print("Invalid parameter. Use one of the following: vanilla, df_en, oa_en, en")
    sys.exit(1)

client.run()