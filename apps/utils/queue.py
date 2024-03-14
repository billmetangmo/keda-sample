from typing import Optional
from backoff import on_exception, expo
from decouple import config
from loguru import logger
from memphis import Memphis, MemphisConnectError, MemphisError

class QueueManager:
    def __init__(self):
        self.memphis: Optional[Memphis] = None

    async def initialize(self):
        await self._connect()

    @on_exception(expo, MemphisConnectError, max_tries=3, max_time=60)
    @logger.catch
    async def _connect(self):
        self.memphis = Memphis()
        await self.memphis.connect(
            host=config("HOST"),
            username=config("USERNAME"),
            password=config("PASSWORD"),
            account_id=1,
        )
        logger.info("Successfully connected to Memphis.")

    @logger.catch
    async def get_producer(self) -> Memphis:
        if not self.memphis:
            await self._connect()
        try:
            producer = await self.memphis.producer(
                station_name=config("QUEUE_NAME"),
                producer_name="producer",
            )
            return producer
        except MemphisError as e:
            logger.error("Failed to create a producer.")
            raise e

    @logger.catch
    async def get_consumer(self,name):
        if not self.memphis:
            await self._connect()
        consumer = await self.memphis.consumer(
            station_name=config("QUEUE_NAME"),
            consumer_name=name,
            consumer_group="consumers",
        )
        if consumer is None:
            raise Exception("Failed to get consumer")
        return consumer

    @logger.catch
    async def close(self):
        if self.memphis:
            await self.memphis.close()
            logger.info("Memphis connection closed.")
