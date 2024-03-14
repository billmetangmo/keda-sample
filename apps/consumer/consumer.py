from __future__ import annotations

import asyncio
from loguru import logger
from utils.queue import QueueManager
from datetime import datetime
import signal

class Consumer:
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self.name = f'consumer-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:23]}'
        self.logger = logger.bind(consumer_name=self.name)
        self.loop = asyncio.get_running_loop()
        self.shutdown_event = asyncio.Event()
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, lambda: asyncio.ensure_future(self.graceful_shutdown()))

    @logger.catch
    async def start_consuming(self) -> None:
        """Starts consuming messages from the queue."""
        async def msg_handler(msgs, error, context):
            for msg in msgs:
                self.log_info(f"Message received: {msg.get_data()}")
                await msg.ack()
                if error:
                    self.log_error(f"Error processing message: {error}")

        try:
            consumer = await self.queue_manager.get_consumer(self.name)
            consumer.consume(msg_handler)
            self.log_info("Consumer started successfully.")
            await self.shutdown_event.wait()
        except Exception as e:
            self.log_error(f"Failed to start consumer: {e}")

    async def graceful_shutdown(self):
        """Initiates graceful shutdown."""
        self.log_info("Shutdown signal received, initiating graceful shutdown...")
        await self.queue_manager.close()
        self.shutdown_event.set()

    def log_info(self, message: str) -> None:
        """Logs an informational message with consumer name prepended."""
        logger.info(f"{self.name} {message}")

    def log_error(self, message: str) -> None:
        """Logs an error message with consumer name prepended."""
        logger.error(f"{self.name} {message}")

    
    



