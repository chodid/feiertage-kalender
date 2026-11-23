# feiertage-kalender – Hinweise für Claude

- Sprache im Repo: Deutsch. Aufbau, Datenformat und Pflege stehen in der [README](README.md).
- Änderungen nur per Pull Request; gemergt wird ausschließlich vom Inhaber des Repos. Die Werkzeuge zum Mergen und
  der Push nach `main` sind in `.claude/settings.json` gesperrt – nicht umgehen.
- Commits, PR-Texte und Issues ohne die Zeile „Claude-Session“ und ohne Links auf claude.ai.
- Das Repo ist öffentlich: keine Namen von Personen, keine privaten Adressen, keine Angaben zu anderen Systemen.
- Vor jedem Push: `python3 erzeugen.py pruefen` und `python3 -m unittest discover -s tests`. Der Workflow „Kalender“
  muss grün sein.
- Dateinamen der Kalender, Kennungen (`uid`) und das JSON-Format (`format: 1`) sind fest – Abos und Programme hängen
  daran. Änderungen nur abwärtskompatibel, sonst neue Format-Nummer und neue Dateinamen.
- Fremde Actions nur mit festem Commit. Die Erzeugung nutzt nur die Python-Standardbibliothek.
