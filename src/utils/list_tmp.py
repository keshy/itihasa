import json
import os
from .temp_utils import get_temp_dir

def list_temp_files():
    """List all JSON files in the temporary directory."""
    temp_dir = get_temp_dir()
    for f in os.listdir(temp_dir):
        if f.endswith('-details.json'):
            file_path = os.path.join(temp_dir, f)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    print(f"Title: {data['title']}")
                    print(f"Description: {data['description']}")
                    print(f"Tags: {', '.join(data['tags'])}")
                    print(f"Video file: {data['video_file']}")
                    print('****************************************************************')
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading {file_path}: {e}")

if __name__ == '__main__':
    list_temp_files()
