import asyncio
import subprocess
import os



async def run_server():
    # Запускаем сервер в отдельном процессе
    server_process = subprocess.Popen(["python", "server.py"])
    # Даём серверу время на запуск
    await asyncio.sleep(1)
    return server_process


async def run_clients(count: int = 2):
    clients = []
    for i in range(1, count + 1):
        # Запускаем клиентов с задержкой между ними
        await asyncio.sleep(0.5)
        client_process = subprocess.Popen(["python", "client.py", str(i)])
        clients.append(client_process)
    return clients


async def main():
    # Cleanup old log files
    for f in ["server.log", "client_1.log", "client_2.log"]:
        if os.path.exists(f):
            os.remove(f)

    # Сначала запускаем сервер
    server = await run_server()

    try:
        # Затем запускаем клиентов
        clients = await run_clients(2)

        try:
            # Run for 5 minutes
            await asyncio.sleep(300)
        finally:
            # Terminate all client processes
            for client in clients:
                client.terminate()
                client.wait()
    finally:
        # Terminate server process
        server.terminate()
        server.wait()

    print("All processes terminated")


if __name__ == "__main__":
    asyncio.run(main())