zakotap
===
파이썬으로 구현된 zakotap api 래퍼

with asyncio


Installing
===
파이썬 3.9 이상이 요구됩니다

zakotap 은 아직 pypi 로 배포되지 않습니다

`python3 -m pip install -U git+https://github.com/ityeri/zakotap.git`


예제
===

```python
import io
import zakotap

name = "YOUR_ZAKO_CLIENT_NAME"
token = "YOUR_ZAKO_CLIENT_TOKEN"

client = zakotap.ZakoClient(token, name)

@client.on_receive
def on_receive(content: str) -> io.BytesIO:
    print(f"메세지 수신: {content}")

    with open("some_audio_file.mp3", "rb") as f:
        file_bytes = f.read()

    return io.BytesIO(file_bytes)


client.run()
```