from logging import getLogger
from pathlib import Path

import pandas as pd
from pandas import DataFrame
from requests_cache import CachedSession

class GeekBenchParser:
    def __init__(self):
        self.LOG = getLogger(__name__)
        self.CACHE_PATH = Path.home() / ".cache" / "geekbench_browser" / "cache.sqlite"
        self.GEEKBENCH_URL = "https://browser.geekbench.com"

    def get_cpus(self):
        rating = 'processor'
        GEEKBENCH_URL = f"{self.GEEKBENCH_URL}/{rating.lower()}-benchmarks.json"
        with CachedSession(
                self.CACHE_PATH.as_posix(), backend="sqlite", expire_after=86400
        ) as session:
            resp = session.get(GEEKBENCH_URL)
            self.LOG.info(
                f"Last retrieved: {resp.created_at}, Cache expires: {resp.expires}, "
                f"Cache path: {self.CACHE_PATH}"
            )

            json_data = session.get(GEEKBENCH_URL).json()
            try:
                df = DataFrame(json_data["devices"])
            except Exception as e:
                raise RuntimeError("Failed to parse json data") from e
            df.set_index("name", inplace=True, drop=False)
            df.index.name = None
            df["frequency"] = (
                df["description"]
                .str.extract(r"(\d+\.?\d+) [MG]Hz")
                .astype(float, errors="ignore")
            )
            df.loc[df["description"].str.contains("MHz"), "frequency"] *= 1e-3
            df["cores"] = (
                df["description"].str.extract(r"(\d+) cores").astype(int, errors="ignore")
            )
            df = df.rename(columns={"score": "single", "multicore_score": "multi"})
            return df

    def get_gpus(self):
        GEEKBENCH_OPENCL_URL = f"{self.GEEKBENCH_URL}/opencl-benchmarks.json"
        GEEKBENCH_VULKAN_URL = f"{self.GEEKBENCH_URL}/vulkan-benchmarks.json"
        GEEKBENCH_METAL_URL = f"{self.GEEKBENCH_URL}/metal-benchmarks.json"

        with CachedSession(
                self.CACHE_PATH.as_posix(), backend="sqlite", expire_after=86400
        ) as session:
            resp_opencl = session.get(GEEKBENCH_OPENCL_URL)
            resp_vulkan = session.get(GEEKBENCH_VULKAN_URL)
            resp_metal = session.get(GEEKBENCH_METAL_URL)
            self.LOG.info(
                f"Last retrieved: {resp_opencl.created_at}, Cache expires: {resp_opencl.expires}, "
                f"Cache path: {self.CACHE_PATH}"
            )
            self.LOG.info(
                f"Last retrieved: {resp_vulkan.created_at}, Cache expires: {resp_vulkan.expires}, "
                f"Cache path: {self.CACHE_PATH}"
            )
            self.LOG.info(
                f"Last retrieved: {resp_metal.created_at}, Cache expires: {resp_metal.expires}, "
                f"Cache path: {self.CACHE_PATH}"
            )

            json_opencl = session.get(GEEKBENCH_OPENCL_URL).json()
            json_vulkan = session.get(GEEKBENCH_VULKAN_URL).json()
            json_metal = session.get(GEEKBENCH_METAL_URL).json()

            try:
                df_opencl = DataFrame(json_opencl["devices"])
                df_vulkan = DataFrame(json_vulkan["devices"]).loc[:,["name","score"]]
                df_metal = DataFrame(json_metal["devices"]).loc[:,["name","score"]]
            except Exception as e:
                raise RuntimeError("Failed to parse json data") from e

            df_vulkan = df_vulkan.rename(columns={"score": "vulkan"})
            df_metal = df_metal.rename(columns={"score": "metal"})

            df_opencl = df_opencl.drop(columns=["multicore_score", "description", "compute_api", "samples"])
            df_opencl = df_opencl.rename(columns={"score": "opencl"})

            df_out = pd.merge(df_opencl, df_vulkan, how='outer')
            df_out = pd.merge(df_out, df_metal, how='outer')
            return df_out

parser = GeekBenchParser()
gpus = parser.get_gpus()
cpus = parser.get_cpus()
print(0)