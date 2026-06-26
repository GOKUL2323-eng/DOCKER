import requests
import json
import sys
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "http://localhost:8000/api/chat/message"
payload = {"message": "வணக்கம்"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers, stream=True)
    print(f"Status: {response.status_code}")
    full_text = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data: '):
                try:
                    data = json.loads(decoded_line[6:])
                    if 'chunk' in data:
                        full_text += data['chunk']
                    elif 'done' in data:
                        pass
                except Exception as json_err:
                    print(f"JSON Parse Error: {json_err} on line: {decoded_line}")
    print(f"Response: {full_text}")
except Exception as e:
    print(f"Error: {e}")
