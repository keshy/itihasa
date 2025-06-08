import os
import json

if __name__ == '__main__':
    for f in os.listdir("/tmp"):
        if f.endswith('-details.json'):
            with open(f'/tmp/{f}', 'r') as file:
                data = json.load(file)
                print(f"Title: {data['title']}")
                print(f"Description: {data['description']}")
                print(f"Tags: {', '.join(data['tags'])}")
                print(f"Video file: {data['video_file']}")
                print('****************************************************************')
