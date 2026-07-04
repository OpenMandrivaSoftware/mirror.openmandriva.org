FROM golang@sha256:3ad57304ad93bbec8548a0437ad9e06a455660655d9af011d58b993f6f615648 as build

LABEL maintainer="etix@l0cal.com"

ARG MIRRORBITS_REPO=https://github.com/OpenMandrivaSoftware/mirrorbits
ARG MIRRORBITS_REF=837c3b8bb2c4121956f5534201bbe564697c14f3

RUN apk --update add \
    git pkgconf build-base zlib-dev protobuf libprotoc

# Build from the OpenMandriva fork at a pinned commit.
# Full clone required: `make` uses `git describe` for the version string.
# Fetching upstream tags yields a readable version (vX.Y-<n>-g<sha>).
RUN git clone "$MIRRORBITS_REPO" /go/mirrorbits && \
    cd /go/mirrorbits && \
    git fetch --tags https://github.com/etix/mirrorbits && \
    git checkout --detach "$MIRRORBITS_REF"

RUN cd /go/mirrorbits && \
    make install PREFIX=/usr

FROM alpine@sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b

# GeoIP settings are provided at runtime by the geoipupdate sidecar (see docker-compose.yml).

RUN mkdir /usr/share/mirrorbits /var/log/mirrorbits /srv/repo

COPY --from=build /usr/bin/mirrorbits /usr/bin/mirrorbits
COPY --from=build /usr/share/mirrorbits/base.html /usr/share/mirrorbits/base.html
COPY --from=build /usr/share/mirrorbits/mirrorlist.html /usr/share/mirrorbits/mirrorlist.html
COPY --from=build /usr/share/mirrorbits/mirrorstats.html /usr/share/mirrorbits/mirrorstats.html
#COPY --from=build /go/bin/geoipupdate /usr/bin/geoipupdate
COPY --from=build /go/mirrorbits/contrib/docker/mirrorbits.conf /etc/mirrorbits.conf

RUN apk --update --no-cache add \
    rsync ca-certificates tzdata protobuf libprotoc vim

ENV EDITOR=/usr/bin/vim

ENTRYPOINT /usr/bin/mirrorbits daemon -config /etc/mirrorbits.conf

EXPOSE 8080
