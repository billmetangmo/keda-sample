import asyncio
from utils.queue import QueueManager
from consumer import Consumer

async def main():
    queue = QueueManager()
    consumer = Consumer(queue)
    await consumer.start_consuming()

if __name__ == "__main__":
    asyncio.run(main())
