import asyncio
from vanilla_data_feed import VanillaDataFeedServer
from encrypted_data_feed import EncryptedDataFeedServer
import sys

if len(sys.argv) != 3:
    print("Usage: python script.py [vanilla|en] [freq]")
    sys.exit(1)  # Exit the script if no parameter or too many parameters are provided

parameter = sys.argv[1]  # Get the parameter
freq = int(sys.argv[2])
df_server = None

if parameter == "vanilla":
    df_server = VanillaDataFeedServer("localhost", 6789, freq)
    print(f"Vanilla data feed server started on port {6789}")
elif parameter == "en":
    df_server = EncryptedDataFeedServer("localhost", 6789, freq)
    print(f"Encrypted data feed server started on port {6789}")
else:
    print("Invalid parameter. Use one of the following: vanilla, en")
    sys.exit(1)

asyncio.run(df_server.run())