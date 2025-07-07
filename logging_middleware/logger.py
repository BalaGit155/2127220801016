import requests

def log(stack, level, package, message):
    url = "http://20.244.56.144/evaluation-service/logs"
    log_data = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }
    try:
        requests.post(url, json=log_data)
    except Exception as e:
        print(f"Logging failed: {e}")
