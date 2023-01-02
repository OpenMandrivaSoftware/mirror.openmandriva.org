# mirror.openmandriva.org
Mirror management for OpenMandriva

It contains 3 docker compose stack (v 2.1)

In case rebuild is needed
- clone the three directories
- clone https://github.com/etix/mirrorbits/ in ./mirrorbits/app
- replace ./mirrorbits/app/Dockerfile with ./mirrorbits/app-sample/Dockerfile
- Verify settings in the three docker-compose.yml (especially the repository path, both for mirrorbits stack and null-rsync)
- launch the docker stanck,
