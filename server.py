import asyncio
import random
import datetime
import logging
from typing import Dict


class Server:
    def __init__(self):
        self.clients: Dict[asyncio.StreamWriter, int] = {}
        self.response_counter = 0
        self.log_file = "server.log"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s;%(message)s',
            datefmt='%Y-%m-%d;%H:%M:%S.%f'
        )

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client_id = len(self.clients) + 1
        self.clients[writer] = client_id
        peername = writer.get_extra_info('peername')
        print(f"New client connected: {peername}, ID: {client_id}")

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                request = data.decode().strip()
                receive_time = datetime.datetime.now()

                # Log request
                log_entry = f"{receive_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{request}"

                # 10% chance to ignore
                if random.random() < 0.1:
                    logging.info(f"{log_entry};(проигнорировано)")
                    print(f"Ignored request from client {client_id}: {request}")
                    continue

                # Process request
                await asyncio.sleep(random.uniform(0.1, 1.0))
                self.response_counter += 1
                response = f"[{self.response_counter}/{request[1:request.index(']')]}] PONG ({client_id})"
                send_time = datetime.datetime.now()

                writer.write(f"{response}\n".encode())
                await writer.drain()

                # Log response
                logging.info(f"{log_entry};{send_time.strftime('%H:%M:%S.%f')[:-3]};{response}")
                print(f"Sent response to client {client_id}: {response}")

        except ConnectionError:
            print(f"Client {client_id} disconnected")
        finally:
            del self.clients[writer]
            writer.close()
            await writer.wait_closed()

    async def send_keepalive(self):
        while True:
            await asyncio.sleep(5)
            if not self.clients:
                continue

            self.response_counter += 1
            response = f"[{self.response_counter}] keepalive"
            send_time = datetime.datetime.now()

            for writer in self.clients.keys():
                try:
                    writer.write(f"{response}\n".encode())
                    await writer.drain()
                    logging.info(
                        f"{send_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};;;{send_time.strftime('%H:%M:%S.%f')[:-3]};{response}")
                    print(f"Sent keepalive to all clients: {response}")
                except ConnectionError:
                    continue

    async def run(self, host: str = '127.0.0.1', port: int = 8888):
        server = await asyncio.start_server(self.handle_client, host, port)
        async with server:
            asyncio.create_task(self.send_keepalive())
            await server.serve_forever()


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run())