import os

from config import set_system_env_defaults
from publisher.youtube import YouTubePublisher

if __name__ == '__main__':
    start_offset = 46
    set_system_env_defaults()
    key_cache = []
    ytp = YouTubePublisher(local_lang="Tamil")
    # get only first level folders under path ta-IN/mahabharat/ - don't get subfolders or files under first level
    # ensure listing supports getting from specific file
    blobs = ytp.bucket.list_blobs(prefix='ta-IN/mahabharat/', delimiter='///')
    for blob in blobs:
        if blob.name.endswith('.mp4'):
            key_cache.append(blob.name)

    key_cache.sort(key=lambda x: (x.rsplit('-', 1)[0], int(x.rsplit('-', 1)[1].rsplit('/', 1)[0])))

    for key in key_cache[start_offset:]:
        # remove last part of key
        # key = '/'.join(key.split('/')[:-1])
        ytp.publish(key='/'.join(key.split('/')[:-1]),
                    tags=['#tamil', '#spirituality', '#santana', '#mahabharat', '#history', '#accuracy', '#mythology',
                          '#indianhistoryandculture'])

# # for each key download the mp4 file into local folder downloads/channel
# for key in key_cache:
#     try:
#         blob = p.bucket.blob(key)
#         file_name = os.path.join('../publish/hindi_mahabharat', key.split('/')[-2] + '.mp4')
#         # create dirs if missing in file_name
#         os.makedirs(os.path.dirname(file_name), exist_ok=True)
#         blob.download_to_filename(file_name)
#         print(f"Downloaded {key} to {file_name}")
#     except Exception as e:
#         print(f"Error downloading {key}: {e}")
