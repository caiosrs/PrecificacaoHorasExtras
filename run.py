import os
import socket
from pathlib import Path

def get_local_ip():
    # Tenta se conectar a um servidor DNS público para obter o IP local
    # O IP real da máquina será obtido, mesmo que sem conexão real
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não precisa de conexão real, apenas usa um IP externo
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Fallback para localhost se houver algum problema
    finally:
        s.close()
    return ip

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horas_extras.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Tem certeza de que ele está instalado e "
            "disponível na sua variável de ambiente PYTHONPATH? Você "
            "esqueceu de ativar um ambiente virtual?"
        ) from exc

    # Obtém o IP local da máquina
    local_ip = get_local_ip()

    try:
        # Usa o IP dinâmico obtido
        execute_from_command_line(['manage.py', 'runserver', f'{local_ip}:8001', '--noreload'])
    except KeyboardInterrupt:
        print("\nServidor interrompido. Fechando...")

if __name__ == '__main__':
    main()
