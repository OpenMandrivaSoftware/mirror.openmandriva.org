# Outils portail — hôte `hodo`

Générateurs des pages annexes du portail miroir. **Ils tournent sur `hodo`**, pas
sur le serveur `mirror.openmandriva.org` : ils collectent leurs données par SSH
(`ashledombos@mirror.openmandriva.org`, `ashledombos@abf-downloads.openmandriva.org`)
puis publient le HTML sur le miroir via `sudo -u mirror tee …`. Ils sont versionnés
ici pour être reproductibles ; ils ne sont pas déployés automatiquement.

## Contenu

- `bin/omv-iso-downloads` — génère la page `/downloads` (ISO de `release_current`,
  taille, somme SHA256/SHA1, nombre de téléchargements Mirrorbits, lien miroir +
  Metalink `.meta4`). Élague les dossiers de sauvegarde `*.bak*`.
- `bin/omv-mirror-status` — génère la page `/status` (tableau de fiabilité des
  miroirs, score `dispo% × fraîcheur%`).
- `systemd/*` — units `oneshot` + timers `daily` (`User=raphael`), qui rafraîchissent
  chaque page une fois par jour.

## Installation sur hodo

```sh
sudo install -m755 -o root -g root bin/omv-iso-downloads bin/omv-mirror-status /usr/local/bin/
sudo install -m644 systemd/*.service systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now omv-iso-downloads.timer omv-mirror-status.timer
```

## Régénérer à la demande

```sh
/usr/local/bin/omv-iso-downloads            # publie /downloads
/usr/local/bin/omv-mirror-status            # publie /status
# --dry-run sur l'un ou l'autre imprime le HTML sans rien publier
```

## Prérequis

- Clé SSH de `raphael@hodo` autorisée sur `mirror` et `abf-downloads` (compte `ashledombos`).
- Sur `mirror`, `ashledombos` peut `sudo -u mirror` (publication) et interroger les
  conteneurs `redis`/`mirrorbits` via `docker exec`.
