
import urllib.request
import os

FILES = {
    "react.development.js": "https://unpkg.com/react@18/umd/react.development.js",
    "react-dom.development.js": "https://unpkg.com/react-dom@18/umd/react-dom.development.js",
    "babel.min.js": "https://unpkg.com/@babel/standalone/babel.min.js"
}

TARGET_DIR = os.path.join("static", "js", "vendor")
os.makedirs(TARGET_DIR, exist_ok=True)

for filename, url in FILES.items():
    save_path = os.path.join(TARGET_DIR, filename)
    print(f"Downloading {filename}...")
    try:
        with urllib.request.urlopen(url) as response, open(save_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Saved to {save_path}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
