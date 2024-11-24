### Prérequis
1. Assurez-vous que le vidéoprojecteur est connecté au même réseau que l'ordinateur.
2. Notez l'adresse IP du vidéoprojecteur et le port utilisé pour les commandes (par défaut, souvent **3629**).
3. Installez Python 3.x et le module `socket`.

---

### Exemple de code : Allumer ou éteindre un vidéoprojecteur Epson

```python
import socket

# Configuration
IP = "192.168.1.100"  # Remplacez par l'adresse IP de votre vidéoprojecteur
PORT = 3629           # Port par défaut pour ESC/VP21
TIMEOUT = 5           # Délai d'attente pour la réponse

# Commandes ESC/VP21
COMMAND_POWER_ON = "PWR ON\r"
COMMAND_POWER_OFF = "PWR OFF\r"
COMMAND_STATUS = "PWR?\r"  # Vérifier l'état du vidéoprojecteur

def send_command(command):
    """Envoie une commande ESC/VP21 au vidéoprojecteur."""
    try:
        # Création de la connexion socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((IP, PORT))
            sock.sendall(command.encode('ascii'))
            response = sock.recv(1024).decode('ascii')
            return response.strip()
    except socket.timeout:
        return "Aucune réponse (délai d'attente dépassé)."
    except Exception as e:
        return f"Erreur : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    print("Allumage du vidéoprojecteur...")
    response = send_command(COMMAND_POWER_ON)
    print(f"Réponse : {response}")

    print("\nVérification de l'état du vidéoprojecteur...")
    status = send_command(COMMAND_STATUS)
    print(f"État : {status}")
```

---

### Fonctionnalités ajoutées
1. **Extinction** : Remplacez `COMMAND_POWER_ON` par `COMMAND_POWER_OFF` pour éteindre le vidéoprojecteur.
2. **Vérification de l'état** : Utilisez la commande `COMMAND_STATUS` pour savoir si l'appareil est allumé ou éteint.

---

### Dépannage
1. **Pas de réponse ?** Vérifiez que le port de communication (par défaut 3629) est ouvert dans le réseau.
2. **Protocole RS232 ?** Si vous utilisez un câble série, vous devrez utiliser une bibliothèque comme `pyserial`.
