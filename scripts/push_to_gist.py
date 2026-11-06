import os
import urllib.request
import json

def push(val):
    GIST_ID = "a664e87ad6db06cc1eedd8f3c7ef15a3"
    TOKEN = os.environ.get("GITHUB_GEIGER_GIST_TOKEN")
    
    if not TOKEN:
        print("PUSH ERROR: Token is missing in this thread!", flush=True)
        return
        
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        clean_val = int(float(val))
        data = json.dumps({"files": {"geiger.txt": {"content": str(clean_val)}}}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
        
        print(f"PUSH START: Sending {clean_val} to GitHub...", flush=True)
        
        with urllib.request.urlopen(req) as response:
            print(f"PUSH SUCCESS: {response.status}", flush=True)
            
    except Exception as e:
        print(f"PUSH EXCEPTION: {e}", flush=True)

