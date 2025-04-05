import cv2
from concurrent.futures import ThreadPoolExecutor
from numpy.typing import NDArray
from typing import Tuple, AsyncGenerator, Optional
import base64
from collections import deque
import time
import asyncio


class Webcam:

    FPS = 20
    CACHE_DURATION_IN_SECS = 30

    def __init__(self, is_cache_enabled: bool = True):
        self.is_cache_enabled = is_cache_enabled
        self.cache = deque()
        self.delay = 1 / self.FPS

    def start(self) -> None:
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Unable to initialize camera")
        self.cache.clear()
        self.thread_executor = ThreadPoolExecutor(max_workers=3)

    def encode(self, buffer) -> str:
        return base64.b64encode(buffer).decode("utf-8")

    def get_encoded_rgb_feed(self, frame: NDArray) -> str:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode(".jpg", rgb_frame)
        return self.encode(buffer)

    def get_encoded_gray_feed(self, frame: NDArray) -> str:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, buffer = cv2.imencode(".jpg", gray)
        return self.encode(buffer)

    def get_encoded_blue_feed(self, frame: NDArray) -> str:
        blue_channel = frame.copy()
        blue_channel[:, :, 1] = 0  # remove Green channel
        blue_channel[:, :, 2] = 0  # remove Red channel
        _, buffer = cv2.imencode(".jpg", blue_channel)
        return self.encode(buffer)

    def get_raw_feed(self) -> Optional[NDArray]:
        ret, frame = self.cap.read()
        return frame if ret else None

    def store_in_cache(self, frame: Tuple) -> None:
        if self.is_cache_enabled:
            current_time = time.time()
            self.cache.append((current_time, frame[0], frame[1], frame[2]))
            while self.cache:
                first_frame_time = self.cache[0][0]
                if current_time - first_frame_time > self.CACHE_DURATION_IN_SECS:
                    self.cache.popleft()
                else:
                    break

    def get_encoded_feeds(self) -> Tuple:
        frame = self.get_raw_feed()
        future_rgb = self.thread_executor.submit(self.get_encoded_rgb_feed, frame)
        future_gray = self.thread_executor.submit(self.get_encoded_gray_feed, frame)
        future_blue = self.thread_executor.submit(self.get_encoded_blue_feed, frame)

        rgb_encoded = future_rgb.result()
        gray_encoded = future_gray.result()
        blue_encoded = future_blue.result()

        self.store_in_cache((rgb_encoded, gray_encoded, blue_encoded))
        print(len(self.cache))
        return rgb_encoded, gray_encoded, blue_encoded

    def stop(self) -> None:
        if not self.cap:
            return
        self.cap.release()
        self.thread_executor.shutdown()

    async def process_live_feed(self) -> AsyncGenerator:
        self.start()
        while self.cap.isOpened():
            rgb_encoded, gray_encoded, blue_encoded = self.get_encoded_feeds()
            yield (rgb_encoded, gray_encoded, blue_encoded)
            await asyncio.sleep(self.delay)

    async def process_cache_feed(self) -> AsyncGenerator:
        if not self.cache:
            raise Exception("Cache is empty")
        for frame in self.cache:
            yield frame
            await asyncio.sleep(self.delay)
