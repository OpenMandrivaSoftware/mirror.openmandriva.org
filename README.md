# mirror.openmandriva.org

Mirror management for OpenMandriva.

This is **not** a plain file mirror: it is a [mirrorbits](https://github.com/etix/mirrorbits)
**redirector** backed by a local *null-mirror*. Clients hitting
`mirror.openmandriva.org` are redirected (HTTP 302) to a real mirror chosen by
GeoIP/weight.

## Architecture

Everything runs from a **single** Docker Compose stack:
`mirrorbits/docker-compose.yml`. Services:

- **redis** - mirrorbits state store.
- **app** (mirrorbits) - scans the local repository tree and redirects clients to a
  real mirror. Listens on `:8080`.
- **geoipupdate** - keeps the MaxMind GeoIP databases up to date (credentials read
  from `mirrorbits/.env`, see below).
- **caddy** - terminates HTTP/HTTPS (Lets Encrypt) and reverse-proxies to `app:8080`.
  Replaces the former nginx-proxy setup.
- **cron** (null-rsync) - runs `null-rsync.py` every 2 minutes against
  `abf.openmandriva.org::openmandriva-full/`, recreating the full repository tree under
  `/opt/mirror/repo/openmandriva/` as **empty (zero-byte) files**. mirrorbits scans that
  tree; the actual file content always lives on the upstream/real mirrors.

The local repository tree is mounted into both `app` and `cron` at `/srv/repo`.

## GeoIP credentials

MaxMind credentials are **not** committed. Create `mirrorbits/.env` (gitignored):

```
GEOIPUPDATE_ACCOUNT_ID=<your-account-id>
GEOIPUPDATE_LICENSE_KEY=<your-license-key>
```

To rotate the key: generate a new license key at https://www.maxmind.com
(*My License Keys*), update `mirrorbits/.env`, delete the old key on MaxMind, then
`docker compose up -d geoipupdate`.

## Rebuild from scratch

1. Clone this repository into `/opt/mirror`.
2. Clone https://github.com/etix/mirrorbits/ into `mirrorbits/app`.
3. Replace `mirrorbits/app/Dockerfile` with `mirrorbits/app-sample/Dockerfile`.
4. Create `mirrorbits/.env` with the MaxMind credentials (see above).
5. Verify the repository path in `mirrorbits/docker-compose.yml` (the `/opt/mirror/repo`
   bind mounts) and the settings in `mirrorbits/mirrorbits.conf`.
6. Launch the stack:

   ```
   cd mirrorbits && docker compose up -d --build
   ```
