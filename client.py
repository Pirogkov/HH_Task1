import asyncio
import random
import re
import time
import datetime
from collections.abc import Coroutine
from typing import Any

cnt: int = 0


async def pars_message(message: str) -> str | bool:
    global cnt
    try:
        res = re.search(r'\d+', message).group(0)
        if int(res) == cnt:
            return res
        else:
            return False
    except:
        return False


async def send_message(writer: asyncio.StreamWriter) -> None:
    global cnt
    await asyncio.sleep(round(random.uniform(0.3, 3.0), 1))
    message: str = f'[{cnt}] PING\n'
    print('Send message {}'.format(message))
    writer.write(f"{message}".encode())
    await writer.drain()


async def get_message(reader: asyncio.StreamReader) -> str | None:
    data: bytes = await reader.read(100)
    message: str = data.decode()
    print('Get message ', message)
    return message


async def handle_messeges(reader: asyncio.StreamReader, writer: asyncio) -> None:
    global cnt
    try:
        await send_message(writer)
        task_send: Coroutine[Any, Any, str] = asyncio.wait_for(get_message(reader), timeout=5)
        await task_send
        cnt += 1
    except asyncio.TimeoutError:
        print('Server timeout')


async def server_client(host: str, port: int) -> None:
    print(f"connected to ({host}, {port})")
    reader, writer = await asyncio.open_connection(host, port)
    while True:
        await handle_messeges(reader, writer)


if __name__ == '__main__':
    asyncio.run(server_client("127.0.0.1", 8888))
