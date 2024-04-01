import re
import asyncio
import random
import logging

counter: int = 0
clients: dict = {}
cnt_req: int = 0

logging.basicConfig(level=logging.INFO,
                    filename="log\server.log",
                    filemode="w",
                    format="%(asctime)s  %(message)s")



async def chek_index(user: str) -> int:
    global clients
    for index, data in enumerate(clients.values()):
        if data == user:
            return index + 1


async def cancle(percent: int = 90) -> bool:
    return random.randrange(100) < percent


async def run_server(host: str, port: int) -> None:
    server = await asyncio.start_server(serve_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f'Server on {addr}')
    await server.serve_forever()


async def broadcast(writer: asyncio.StreamWriter) -> None:
    global cnt_req
    await asyncio.sleep(5)
    mesage = f"[{cnt_req}] keepalive\n"
    for client_writer in clients.keys():
        client_writer.write(mesage.encode())


# async def chek_clients(writer: asyncio.StreamWriter) -> None:
#     global cnt_req
#     mesage = f"[{cnt_req}] keepalive\n"
#     writer.write(mesage.encode())
#     #cnt_req+=1

async def serve_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    global counter
    global clients
    info: tuple = writer.get_extra_info('peername')
    clients[writer] = info
    cid: int = counter
    counter += 1
    print(f'Client #{cid} {info} connected')
    user_id: int = await chek_index(clients[writer])
    while True:
        request: bytearray | None = await read_request(reader)
        if request is None:
            print(f'Client #{cid} unexpectedly disconnected')
            del clients[writer]
            break
        else:
            response: bytes = await handle_request(request, user_id)
            # await write_response(writer, response, cid)
            await asyncio.gather(write_response(writer, response, cid), broadcast(writer), return_exceptions=True)


async def read_request(reader: asyncio.StreamReader, delimiter: bytes = b'\n') -> bytearray | None:
    global counter
    cid: int = counter
    request = bytearray()
    while True:
        chunk: bytes = await reader.read(100)
        if not chunk:
            print(f'Client #{cid} unexpectedly disconnected')
            break
        request += chunk
        if delimiter in request:
            return request
    return None


async def pars_message(message: bytes, user_id: int) -> bytes | None:
    global cnt_req
    message = message.decode()
    try:
        res = re.search(r'\d+', message).group(0)
        logging.info(message)
        result = f'[{cnt_req}/{res}] PONG ({user_id})\n'
        print(result)
        return result.encode()
    except:
        return None


async def handle_request(request: bytes, user_id: int) -> bytes | None:
    crash: int = await cancle(10)
    if crash:
        print('Server not make response')
        logging.info(request.decode().rstrip() + ' проигнорировано')
        return None
    await asyncio.sleep(round(random.uniform(0.1, 1.0), 1))
    data: bytes = await pars_message(request, user_id)
    return data


async def write_response(writer: asyncio.StreamWriter, response: bytes, cid: int) -> None:
    global cnt_req
    logging.info(response.decode())
    writer.write(response)
    await writer.drain()
    cnt_req += 1
    print(f'Client #{cid} has been served {response}')


if __name__ == '__main__':
    asyncio.run(run_server('127.0.0.1', 8888))
