import socket
import threading
import json
import time
import pygame

# 🔥 CHANGE THIS → SERVER IP
SERVER_IP = "10.30.201.137"   # ← REPLACE WITH SERVER SYSTEM IP
SERVER_PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(1)

player_id = int(input("Enter player ID (1 or 2): "))

x, y = 300, 300
seq = 0
players = {}

latency = 0
prev_latency = 0
jitter = 0

# RECEIVE THREAD
def receive():
    global players, latency, prev_latency, jitter

    while True:
        try:
            data, _ = client.recvfrom(1024)
            msg = json.loads(data.decode())

            players = msg["players"]

            recv_time = time.time()
            latency = recv_time - msg["time"]
            jitter = abs(latency - prev_latency)
            prev_latency = latency

            print("\n📥 Received:", msg)
            print(f"📊 Latency: {latency:.4f} | Jitter: {jitter:.4f}")

        except:
            continue

# Start thread
threading.Thread(target=receive, daemon=True).start()

# 🎮 PYGAME
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption(f"Player {player_id}")

font = pygame.font.Font(None, 30)
clock = pygame.time.Clock()

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        y -= 5
    if keys[pygame.K_s]:
        y += 5
    if keys[pygame.K_a]:
        x -= 5
    if keys[pygame.K_d]:
        x += 5

    seq += 1

    msg = {
        "player_id": player_id,
        "x": x,
        "y": y,
        "seq": seq,
        "time": time.time()
    }

    client.sendto(json.dumps(msg).encode(), (SERVER_IP, SERVER_PORT))
    print(f"\n📤 Sent: {msg}")

    # Draw players
    for pid, pos in players.items():
        px, py = pos
        color = (255, 0, 0) if int(pid) == player_id else (0, 0, 255)
        pygame.draw.circle(screen, color, (px, py), 10)

    # Show latency & jitter
    lat_text = font.render(f"Latency: {latency:.4f}", True, (255,255,255))
    jit_text = font.render(f"Jitter: {jitter:.4f}", True, (255,255,255))

    screen.blit(lat_text, (10, 10))
    screen.blit(jit_text, (10, 40))

    pygame.display.update()
    clock.tick(20)

pygame.quit()