import io
import os
import dotenv
import zakotap

dotenv.load_dotenv(".env")

name = os.getenv("ZAKO_CLIENT_NAME")
token = os.getenv("ZAKO_CLIENT_TOKEN")

client = zakotap.ZakoClient(token, name)

@client.on_receive
def on_receive(content: str) -> io.BytesIO:
    print(f"메세지 수신: {content}")

    with open("chill.mp3", "rb") as f:
        file_bytes = f.read()

    return io.BytesIO(file_bytes)


client.run()