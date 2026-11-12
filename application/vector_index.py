from pathlib import Path

from PIL import Image


class VectorIndex:
    """Small in-process index of 12-bin RGB histograms for catalog images."""

    def __init__(self, static_directory):
        self.static_directory = Path(static_directory)
        self._cache = {}

    @staticmethod
    def extract(image_path):
        with Image.open(image_path) as source:
            image = source.convert("RGB").resize((64, 64), Image.Resampling.BILINEAR)
            channels = image.split()
            values = []
            for channel in channels:
                histogram = channel.histogram()
                bins = [
                    sum(histogram[start : start + 64])
                    for start in range(0, 256, 64)
                ]
                total = sum(bins) or 1
                values.extend(count / total for count in bins)
            return values

    def product_vector(self, image_url):
        image_path = self.static_directory / image_url
        modified_at = image_path.stat().st_mtime_ns
        cache_key = str(image_path)
        cached = self._cache.get(cache_key)
        if cached and cached[0] == modified_at:
            return cached[1]
        vector = self.extract(image_path)
        self._cache[cache_key] = (modified_at, vector)
        return vector
