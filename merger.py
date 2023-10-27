import os
import json
from datetime import datetime

folder_path = "/root/Cert-FR/data/"

combined_data = []

for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        with open(os.path.join(folder_path, filename)) as f:
            data = json.load(f)
            combined_data.extend(data)
            os.remove(os.path.join(folder_path, filename))

with open(f'/root/Cert-FR/data/cert_fr_data.json', 'w') as f:
    json.dump(combined_data, f)