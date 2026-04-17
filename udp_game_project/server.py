import socket
import json
import random

# Bind to all networks (IMPORTANT for 2 systems)
SERVER_IP = "0.0.0.0"
SERVER_PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))

clients = set()
players = {}
last_seq = {}

print(f"🚀 Server started on {SERVER_IP}:{SERVER_PORT}\n")

while True:
    try:
        data, addr = server.recvfrom(1024)
        message = json.loads(data.decode())

    except Exception:
        continue

    clients.add(addr)

    player_id = message["player_id"]
    seq = message["seq"]

    print(f"\n📩 Received from Player {player_id}: {message}")

    # Ignore old packets
    if player_id not in last_seq or seq > last_seq[player_id]:
        last_seq[player_id] = seq
        players[player_id] = (message["x"], message["y"])
        print(f"✅ Updated Player {player_id} → {players[player_id]}")
    else:
        print("⚠️ Old packet ignored")

    print(f"🧠 Game State: {players}")

    # Send state to all clients
    state = json.dumps({
        "players": players,
        "time": message["time"]
    }).encode()

    for client in clients:
        try:
            # 20% packet loss simulation
            if random.random() > 0.2:
                server.sendto(state, client)
                print(f"📤 Sent to {client}")
            else:
                print(f"❌ Packet DROPPED for {client}")
        except:
            continue