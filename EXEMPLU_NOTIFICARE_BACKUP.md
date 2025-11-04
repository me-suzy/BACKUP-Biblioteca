# EXEMPLU NOTIFICARE BACKUP

## La ce ora vei primi notificarea?

**Fereastra de timp:** 23:00 - 02:00 (pe server Linux)
- Backup-ul incepe intre 23:00-00:00
- Backup-ul se termina intre 00:00-02:00
- Notificarea este trimisa dupa terminarea backup-ului

**NOTA:** Serverul este pe Linux, iar ora locala e posibil sa fie diferita.
In Romania, daca serverul foloseste UTC, vei primi notificarea cu 2-3 ore diferenta.

## Cum va arata notificarea?

### CASUL 1: Backup SUCCES (cod 00)

**Titlu/Topic:** `bariasi-5f07b8571f7c`

**Mesaj complet:**
```
BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup
```

**Detalii:**
- **BACKUP:** FULL - tipul backup-ului
- **DB:** ALEPH - Oracle SID
- **CODE:** 00 - succes (00 = success)
- **TIME:** 2025-10-28 01:23:45 - momentul EXACT al backup-ului
- **STATUS:** End FULL backup - mesaj complet

---

### CASUL 2: Backup CU EROARE (cod 01-14)

**Mesaj complet:**
```
BACKUP: FULL | DB: ALEPH | CODE: 01 | TIME: 2025-10-28 01:45:12 | STATUS: RMAN Error During Full Backup see /path/to/detail_log
```

**Detalii:**
- **CODE:** 01 - eroare (nu 00!)
- **TIME:** momentul EXACT al erorii
- **STATUS:** mesajul erorii

---

## Informatii unice din notificare

### 1. TIMESTAMP
```
TIME: 2025-10-28 01:23:45
```
- Este MEREU diferit
- Confirma ca backup-ul s-a terminat ACUM
- Nu poate fi "notificare falsa"

### 2. COD EROARE
- **00** = Success - backup completat cu succes
- **01** = RMAN Error During Full Backup
- **02** = RMAN Error During Set Config
- **03** = Database Shutdown Failed
- **04** = Database Startup Failed
- **05** = RMAN Error - Full Backup Script
- **06** = RMAN Error During Validate Backup
- **07** = RMAN Error During Delete Obsolete
- **08** = Hot backup can be done only when running in archive mode
- **09** = Oracle Software backup not successful
- etc.

### 3. TIP BACKUP
- FULL - backup complet
- INCREMENTAL - backup increment
- etc.

### 4. ORACLE SID
- ALEPH - baza de date backup-uita

---

## Exemplu: Evolutia notificarilor

### Luni 27 Oct 2025, 23:30
```
BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:30:15 | STATUS: End FULL backup
```

### Marti 28 Oct 2025, 23:30
```
BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-29 01:25:42 | STATUS: End FULL backup
```

### Miercuri 29 Oct 2025, 23:30
```
BACKUP: INCREMENTAL | DB: ALEPH | CODE: 00 | TIME: 2025-10-30 00:15:03 | STATUS: End INCREMENTAL backup
```

**OBSERVATIE:** Timestamp-ul este MEREU diferit!

---

## De ce este aceasta notificare SIGURA?

### 1. Timestamp unic
- Fiecare backup are timestamp diferit
- Confirma ca backup-ul s-a executat ACUM
- Nu poate fi notificare "stata"

### 2. Cod eroare specific
- 00 = succes
- Orice alt cod = eroare specifica
- Confirma rezultatul backup-ului

### 3. Se trimite DOAR dupa backup
- Notificarea este trimisa DUPA ce email-ul a fost trimis
- Linia 99 din backup_mailer (dupa mailx)
- Nu poate rula "fara backup"

### 4. Informatiile sunt din variabilele Linux
- ${BACKUP_TYPE} - din parametrul backup-ului
- ${ORACLE_SID} - din server
- ${ERROR_NUMBER} - din rezultatul backup-ului
- ${ERROR_MESSAGE} - din rezultatul backup-ului
- `/bin/date '+%Y-%m-%d %H:%M:%S'` - momentul EXACT

---

## Analiza: Timestamp-ul demonstreaza un backup real

### Notificare FALSA (nu va mai aparea):
```
Server notification
```
- Nu contine informatii specifice
- Nu are timestamp
- Nu are cod eroare
- Nu are tip backup

### Notificare REALA (ce vei primi):
```
BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup
```
- Contine TOATE informatiile specifice
- Are timestamp EXACT
- Are cod eroare (00 = success)
- Are tip backup (FULL)
- Are Oracle SID (ALEPH)
- Se trimite DOAR dupa backup real

---

## Concluzie

**VEI PRIMI:**
- O singura notificare dupa fiecare backup
- Timestamp diferit in fiecare noapte
- Cod eroare 00 = success, alt cod = error
- Toate informatiile specifice despre backup

**NU VE MAI PRIMI:**
- "Server notification" generice
- Notificari multiple
- Notificari fara informatii unice

**NOTIFICAREA VA FI SIGNIFICATIVA PENTRU:**
- Verifica daca backup-ul s-a terminat
- Verifica daca backup-ul a reusit (cod 00) sau a esuat
- Stie exact la ce ora s-a terminat backup-ul
- Verifica tipul backup-ului executat
