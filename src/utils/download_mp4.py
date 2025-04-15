import os

from config import set_system_env_defaults
from publisher import Publisher

if __name__ == '__main__':
    set_system_env_defaults()
    key_cache = set()
    p = Publisher()
    # get only first level folders under path ta-IN/mahabharat/ - don't get subfolders or files under first level
    blobs = p.bucket.list_blobs(prefix='hi-IN/mahabharat/', delimiter='///')
    for blob in blobs:
        if blob.name.endswith('.mp4'):
            key_cache.add(blob.name)

    # for each key download the mp4 file into local folder downloads/channel
    for key in key_cache:
        try:
            blob = p.bucket.blob(key)
            file_name = os.path.join('../publish/hindi_mahabharat', key.split('/')[-2] + '.mp4')
            # create dirs if missing in file_name
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            blob.download_to_filename(file_name)
            print(f"Downloaded {key} to {file_name}")
        except Exception as e:
            print(f"Error downloading {key}: {e}")
