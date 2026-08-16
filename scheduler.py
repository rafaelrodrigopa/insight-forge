import time
from datetime import datetime
import subprocess
import sys

HORA_ALVO = "08:00"  # Ajuste para o horário desejado (formato HH:MM)

print(f"[*] Agendador nativo iniciado às {datetime.now().strftime('%H:%M:%S')}.")
print(f"[*] Tarefa programada para: {HORA_ALVO}")

executado_hoje = False

while True:
    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")

    if hora_atual == HORA_ALVO and not executado_hoje:
        print(f"\n[+] [{agora.strftime('%H:%M:%S')}] Disparando pipeline...")
        subprocess.run([sys.executable, "main.py", "--linkedin", "--publish"])
        executado_hoje = True
        print(f"[+] Concluído. Aguardando próximo ciclo...")

    # Reseta a trava quando virar o minuto
    if hora_atual != HORA_ALVO:
        executado_hoje = False

    time.sleep(1)