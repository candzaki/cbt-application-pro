import urllib.request
import os
os.makedirs("static/js", exist_ok=True)
url = "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js"
urllib.request.urlretrieve(url, "static/js/face-api.min.js")
print("Downloaded face-api.min.js")
