from loguru import logger
from utils.queue import QueueManager
import asyncio
import signal

class Producer:
    def __init__(self, queue_manager: QueueManager, rate: float):
        self.queue_manager = queue_manager
        self.rate = rate
        self.should_stop = False  # Flag to control execution
        self.loop = asyncio.get_running_loop()
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, self.graceful_shutdown)

    def graceful_shutdown(self):
        logger.info("Shutdown signal received, initiating graceful shutdown...")
        self.should_stop = True  # Update the flag to stop execution
        asyncio.ensure_future(self.queue_manager.close())

    async def generate_messages(self):
        """Generates messages at a defined rate."""
        i = 0
        while True and not self.should_stop:  # Check the flag before continuing
            message = f"Message #{i}: Hello world sent at rate {self.rate}"
            yield message
            i += 1
            await asyncio.sleep(self.rate)

    async def run(self):
        """Executes the producer logic to send messages"""
        try:
            producer = await self.queue_manager.get_producer()
            async for message in self.generate_messages():
                await producer.produce(message)
                logger.info(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"An error occurred in Producer: {e}")
