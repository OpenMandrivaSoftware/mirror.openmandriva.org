FROM golang:alpine as build

LABEL maintainer="etix@l0cal.com"

ADD . /go/mirrorbits

RUN apk --update add \
    git pkgconf build-base zlib-dev protobuf libprotoc

#RUN go get -u github.com/maxmind/geoipupdate2/cmd/geoipupdate 
#RUN env GO111MODULE=on go get -u github.com/maxmind/geoipupdate/cmd/geoipupdate
#RUN go install -ldflags "-X main.defaultConfigFile=/etc/GeoIP.conf -X main.defaultDatabaseDirectory=/usr/share/GeoIP" github.com/maxmind/geoipupdate/cmd/geoipupdate

RUN cd /go/mirrorbits && \
    make install PREFIX=/usr

FROM alpine:latest

# Set your own GeoIP settings
#ENV GEOIP_ACCOUNT_ID 459014
#ENV GEOIP_LICENSE_KEY UV0HKxXs3SRVP7f2

RUN mkdir /usr/share/mirrorbits /var/log/mirrorbits /srv/repo

COPY --from=build /usr/bin/mirrorbits /usr/bin/mirrorbits
COPY --from=build /usr/share/mirrorbits/base.html /usr/share/mirrorbits/base.html
COPY --from=build /usr/share/mirrorbits/mirrorlist.html /usr/share/mirrorbits/mirrorlist.html
COPY --from=build /usr/share/mirrorbits/mirrorstats.html /usr/share/mirrorbits/mirrorstats.html
#COPY --from=build /go/bin/geoipupdate /usr/bin/geoipupdate
COPY --from=build /go/mirrorbits/contrib/docker/mirrorbits.conf /etc/mirrorbits.conf

RUN apk --update --no-cache add \
    rsync ca-certificates tzdata protobuf libprotoc vim

#RUN echo -e "AccountID ${GEOIP_ACCOUNT_ID}\nLicenseKey ${GEOIP_LICENSE_KEY}\nEditionIDs GeoLite2-City GeoLite2-Country GeoLite2-ASN" > /etc/GeoIP.conf && \
#    mkdir /usr/share/GeoIP && \
#    /usr/bin/geoipupdate

ENV EDITOR=/usr/bin/vim

ENTRYPOINT /usr/bin/mirrorbits daemon -config /etc/mirrorbits.conf

EXPOSE 8080
