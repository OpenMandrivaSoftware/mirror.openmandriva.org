FROM frolvlad/alpine-python2

#============
# Following command for ifever upstream is missing
#FROM alpine:3.15
# Downgraded to Alpine 3.15 as newer versions of Alpine don't have python2 anymore


# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
#ENV PYTHONUNBUFFERED=1

#RUN apk add --no-cache python2 && \
#    python -m ensurepip && \
#    rm -r /usr/lib/python*/ensurepip && \
#    pip install --upgrade pip setuptools && \
#    rm -r /root/.cache
#============

RUN apk --update --no-cache add \
    rsync

# Copy mirrorbrain null-rsync to the container
COPY null-rsync.py /.

# Create repo directory
RUN mkdir -p /srv/repo

# Copy cron file to the container
COPY cron /etc/cron.d/cron

# Give the permission
RUN chmod 0644 /etc/cron.d/cron
 
# Add the cron job
RUN crontab /etc/cron.d/cron
 
# Link cron log file to stdout
RUN ln -s /dev/stdout /var/log/cron
 
# Run the cron service in the foreground
CMD [ "crond", "-l", "2", "-f" ]
