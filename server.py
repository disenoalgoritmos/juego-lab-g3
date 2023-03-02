import asyncio
import json

async def process_client_request(client_reader, client_writer):
    # Aquí se procesan las solicitudes entrantes del cliente
    data = await client_reader.read(100)
    message = json.loads(data.decode())
    addr = client_writer.get_extra_info('peername')

    print(f"Received {message['TYPE']!r} from {addr!r}")

    response={"TYPE": "RESPONSE", "MESSAGE":"OK"}
    
    print(f"Send: {response!r}")
    client_writer.write(json.dumps(response).encode())
    await client_writer.drain()

    #print("Close the connection")
    #client_writer.close()
    #await client_writer.wait_closed()
    pass

async def handle_client_connection(reader, writer):
    while True:
        data = await reader.read(1024)
        message = data.decode()
        if not data:
            break
        print(f"Received message: {message}")
        response={"TYPE": "RESPONSE", "MESSAGE":"OK"}
        writer.write(json.dumps(response).encode())
        await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_client_connection, 'localhost', 8888)

    async with server:
        await server.serve_forever()

asyncio.run(main())