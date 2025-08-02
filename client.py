import asyncio
import random
import datetime
import logging
import sys


class Client:
    def __init__(self, client_id: int):
        self.client_id = client_id
        self.request_counter = 0
        self.log_file = f"client_{client_id}.log"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s;%(message)s',
            datefmt='%Y-%m-%d;%H:%M:%S.%f'
        )

    async def send_ping(self, writer: asyncio.StreamWriter):
        while True:
            await asyncio.sleep(random.uniform(0.3, 3.0))
            self.request_counter += 1
            request = f"[{self.request_counter}] PING"
            send_time = datetime.datetime.now()

            writer.write(f"{request}\n".encode())
            await writer.drain()

            log_entry = f"{send_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{request}"
            logging.info(f"{log_entry}")
            print(f"Client {self.client_id} sent: {request}")

    async def handle_responses(self, reader: asyncio.StreamReader):
        while True:
            data = await reader.readline()
            if not data:
                break

            response = data.decode().strip()
            receive_time = datetime.datetime.now()

            # Update last log entry (either for PONG or keepalive)
            if "PONG" in response:
                # Find the last PING log entry and update it
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()

                if lines:
                    last_line = lines[-1].strip()
                    if "PING" in last_line:
                        updated_line = f"{last_line};{receive_time.strftime('%H:%M:%S.%f')[:-3]};{response}"
                        with open(self.log_file, 'w') as f:
                            f.write('\n'.join(lines[:-1] + [updated_line]) + '\n')
            else:  # keepalive
                logging.info(
                    f"{receive_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};;;;{receive_time.strftime('%H:%M:%S.%f')[:-3]};{response}")

            print(f"Client {self.client_id} received: {response}")

    async def run(self, host: str = '127.0.0.1', port: int = 8888):
        reader, writer = await asyncio.open_connection(host, port)
        try:
            await asyncio.gather(
                self.send_ping(writer),
                self.handle_responses(reader)
            )
        except ConnectionError:
            print(f"Client {self.client_id} disconnected")
        finally:
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    client_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    client = Client(client_id)
    asyncio.run(client.run())