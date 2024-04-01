import asyncio
import random
import re
from collections.abc import Coroutine
from typing import Any
import logging

cnt: int = 0
chek = True
timeout = False
mess_list: list = []

logging.basicConfig(level=logging.INFO,
                    filename="log\client.log",
                    filemode="w",
                    format="%(asctime)s  %(message)s")


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


async def send_message(writer: asyncio.StreamWriter) -> str:
    global cnt
    global timeout
    global mess_list
    if not timeout:
        cnt += 1
    await asyncio.sleep(round(random.uniform(0.3, 3.0), 1))
    message: str = f'[{cnt}] PING\n'
    mess_list.append(message)
    print('Send message {}'.format(message))
    writer.write(f"{message}".encode())
    await writer.drain()
    logging.info(message)
    return message


async def get_message(reader: asyncio.StreamReader) -> str | None:
    global chek
    global timeout
    data: bytes = await reader.read(100)
    message: str = data.decode()
    if 'keepalive' in message.lower():
        # logging.info(message)
        chek = False
        print(message)
        pass
    else:
        chek = True
        if not timeout:
            logging.info(message)
        print('Get message ', message)
        return message


async def handle_messeges(reader: asyncio.StreamReader, writer: asyncio) -> None:
    global cnt
    global chek
    global timeout
    global mess_list
    try:
        if chek == True:
            await send_message(writer)
        await asyncio.wait_for(get_message(reader), timeout=8)
        # await task_get
        timeout = False
    except asyncio.TimeoutError:
        logging.info(f'{mess_list[-1].rstrip()} (проигнорировано)')
        timeout = True
        chek = True
        mess_list = []
        # send_mess = await send_message(writer)
        # logging.info(f'{send_mess.rstrip()} server timeout\n')


async def server_client(host: str, port: int) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    print(f"connected to ({host}, {port})")
    while True:
        await handle_messeges(reader, writer)


if __name__ == '__main__':
    asyncio.run(server_client("127.0.0.1", 8888))
