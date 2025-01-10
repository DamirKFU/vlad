import psutil
import time
import json
from datetime import datetime
from elasticsearch import Elasticsearch

# Подключение к Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=("elastic", "WZNXKNqpcaQtrCigSno9"),
    verify_certs=False
)

def get_metrics():
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count()
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }

def main():
    while True:
        metrics = get_metrics()
        print(metrics)

if __name__ == "__main__":
    main()