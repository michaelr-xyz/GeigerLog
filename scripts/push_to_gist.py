import os
import urllib.request
import json

def push(val):
    GIST_ID = "a664e87ad6db06cc1eedd8f3c7ef15a3"
    TOKEN = os.environ.get("GITHUB_GEIGER_GIST_TOKEN")
    
    if not TOKEN:
        print("ERROR: GITHUB_GEIGER_GIST_TOKEN not set in environment.")
        return val
        
    # Filter out the 32768 overflow spikes
    if val >= 20000:
        val = -1
        
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = json.dumps({"files": {"geiger.txt": {"content": str(val)}}}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"Gist update failed: {e}")
        
    return val

