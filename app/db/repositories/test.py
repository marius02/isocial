import requests

url = "http://localhost:8000/chat/continue"

headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MzgxYmE2ZS1jM2I5LTQ0NmMtOWNkOS05ODY0NzExZGYwOGEiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTcwNDkwNzgxNn0.88bbIYCF308zlnCNziEU2tEVa7OuxBAMexrCgM3BhfM',
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
}

data = {
    "chat_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
    "question": "Extract positive comments"
}

with requests.post(url, headers=headers, json=data, stream=True) as r:
    for chunk in r.iter_content(1024):
        print(chunk)
        
        
        
