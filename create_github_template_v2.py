#!/usr/bin/env python
"""
Creez template curatat pentru GitHub v2 - rezolvarea finala cu NTFY detaliat
"""

import os
import shutil

def main():
    # Creez folder
    folder = "github_template_2"
    
    if os.path.exists(folder):
        shutil.rmtree(folder)
    
    os.makedirs(folder)
    
    # Fisiere importante de azi
    files_to_copy = [
        "setup_ntfy_notifications.py",
        "integrate_ntfy_backup.py",
        "final_fix_ntfy_single.py",
        "verify_final_ntfy.py",
        "cleanup_old_test_scripts.py",
        "final_ntfy_test.py",
        "verify_ntfy_in_backup.py",
        "add_detailed_ntfy_to_backup.py",
        "read_backup_and_create_detailed_ntfy.py",
        "check_all_ntfy_scripts.py",
        "GUID_SETUP_NOTIFICARI.txt",
        "EXEMPLU_NOTIFICARE_BACKUP.md"
    ]
    
    # Adaug fisierele
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, folder)
            print(f"[OK] Adaugat: {file}")
        else:
            print(f"[WARN] Nu exista: {file}")
    
    # Creez README
    readme_content = """# Linux Backup NTFY Notifications

Set de scripturi Python pentru a configura notificari NTFY detaliate pentru backup-uri Linux.

## Problema Rezolvata

Configurarea notificari NTFY pentru backup-uri Oracle pe un server Linux vechi (RHEL 4), cu informatii unice care confirma ca backup-ul s-a executat cu succes.

## Caracteristici

- **O singura notificare** dupa fiecare backup
- **Informatii complete**: tip backup, Oracle SID, cod eroare, timestamp, status
- **Validare unica**: timestamp-ul confirma ca backup-ul s-a terminat ACUM
- **Fara duplicate**: eliminarea notificarilor multiple
- **Curatenie**: eliminarea notificarilor de test

## Structura

### Scripturi Principale

1. **setup_ntfy_notifications.py** - Configurare initiala NTFY pe server
2. **integrate_ntfy_backup.py** - Integrare NTFY in scriptul de backup
3. **final_fix_ntfy_single.py** - Corectare pentru o singura notificare
4. **verify_final_ntfy.py** - Verificare configuratie finala

### Verificare si Teste

- **cleanup_old_test_scripts.py** - Curatare fisiere de test
- **check_all_ntfy_scripts.py** - Verificare toate scripturile NTFY
- **final_ntfy_test.py** - Test notificare finala

## Notificare Finala

Mesajul trimis la fiecare backup:

```
BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup
```

**Informatii unice:**
- BACKUP: Tip backup (FULL, INCREMENTAL, etc.)
- DB: Oracle SID
- CODE: 00 = succes, 01-14 = erori
- TIME: Timestamp momentul EXACT
- STATUS: Mesaj detaliat

## Instalare

1. Conectare la server Linux
2. Configurare topic NTFY (`bariasi-<hash>`)
3. Ruleaza `setup_ntfy_notifications.py`
4. Integreaza in backup cu `final_fix_ntfy_single.py`
5. Verifica cu `verify_final_ntfy.py`

## Verificare

Dupa instalare, notificarea va aparea:
- La fiecare backup (23:00-02:00)
- O singura notificare
- Cu informatiile complete de mai sus

## Fisiere de Referinta

- `GUID_SETUP_NOTIFICARI.txt` - Ghid setup NTFY
- `EXEMPLU_NOTIFICARE_BACKUP.md` - Exemple notificari

## Licenta

MIT License
"""
    
    with open(f"{folder}/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"\n[OK] Template creat in: {folder}/")
    print(f"[OK] README.md creat")
    
    return 0

if __name__ == "__main__":
    main()
