import os
import time

from publisher import Publisher
from config import set_system_env_defaults

if __name__ == '__main__':
    set_system_env_defaults()
    key_cache = set()
    p = Publisher()
    # get only first level folders under path ta-IN/mahabharat/ - don't get subfolders or files under first level
    blobs = p.bucket.list_blobs(prefix='ta-IN/mahabharat/', delimiter='///')
    for blob in blobs:
        key_cache.add('/'.join(blob.name.split('/')[0:3]))

    for key in key_cache:
        try:
            p.process_video(key=key)
        except Exception as e:
            print(f"Error processing {key}: {e}")

        # sleep for 1 seconds to avoid rate limit
        time.sleep(5)

    print("All videos processed successfully!")
