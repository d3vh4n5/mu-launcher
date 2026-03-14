def log_message(message):
    with open("updater_log.txt", "a") as f:
        f.write(f"{message}\n")
    print(message)