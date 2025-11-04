#!/usr/bin/env python
"""
Creeaza script de notificare prin Telegram pentru serverul Linux
"""

import sys

def main():
    print("=" * 70)
    print("   SETUP TELEGRAM BOT PENTRU NOTIFICARI SERVER")
    print("=" * 70)
    print()
    
    print(">> PASI SIMPLI PENTRU SETUP TELEGRAM BOT:")
    print()
    print("   1. DESCHIDE TELEGRAM pe telefon/PC")
    print()
    print("   2. CAUTA: @BotFather in Telegram")
    print()
    print("   3. TRIMITE comanda: /newbot")
    print()
    print("   4. DA UN NUME botului:")
    print("      Exemplu: Bariasi Academy Notifications")
    print()
    print("   5. DA UN USERNAME botului:")
    print("      Exemplu: bariasi_academy_bot")
    print()
    print("   6. BOTFATHER VA DA UN TOKEN:")
    print("      Exemplu: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    print()
    print("   7. SUNT GRATIS SI IL VOM FOLOSI INAINTE SA FINALIZAM MESAJUL")
    print()
    print("   8. IA TELEGRAM BOT TOKEN:")
    print("      Trebuie sa iei token-ul de la BotFather dupa /newbot")
    print()
    print(">> DETALII IMPORTANTE:")
    print("   - Telegram Bot este GRATIS")
    print("   - Nu are limitari de mesaje")
    print("   - Notificari instant")
    print("   - Poate trimite la orice chat")
    print()
    
    print("=" * 70)
    print("Dupa ce ai token-ul de la BotFather, spune-mi si")
    print("configuram instant notificarea pe serverul Linux!")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)

