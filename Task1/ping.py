import csv
import subprocess


addresses = [
    "discordapp.com",
    "wikipedia.com",
    "microsoft.com",
    "example.com",
    "yandex.com",
    "google.com",
    "github.com",
    "apple.com",
    "gmail.com",
    "vk.com",
]

with open("ping.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(["address", "ping (ms)"])
    for address in addresses:
        result = subprocess.run(["ping", "-c", "1", address], capture_output=True)
        if result.returncode == 0:
            rtt = result.stdout.decode()
            writer.writerow([address, rtt[rtt.find("time=") + 5 : rtt.find("ms")]])
        else:
            writer.writerow([address, "no connection"])
