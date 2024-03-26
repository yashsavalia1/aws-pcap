from vanilla_order_api import VanillaOrderAPIServer
from encrypted_order_api import EncryptedOrderAPIServer
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py [vanilla|en]")
    sys.exit(1)  # Exit the script if no parameter or too many parameters are provided

parameter = sys.argv[1]  # Get the parameter
order_api = None

if parameter == "vanilla":
    order_api = VanillaOrderAPIServer(5000)
elif parameter == "en":
    order_api = EncryptedOrderAPIServer(5000)
else:
    print("Invalid parameter. Use one of the following: vanilla, en")
    sys.exit(1)

order_api.run()