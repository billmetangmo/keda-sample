import asyncio
from utils.queue import QueueManager
from producer import Producer
from decouple import config

async def main():
    queue_manager = QueueManager()
    await queue_manager.initialize()
    
    producer = Producer(queue_manager,config("RATE", cast=float))
    await producer.run()

if __name__ == "__main__":
    asyncio.run(main())
