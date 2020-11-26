FROM prom/prometheus

USER root
COPY ./prometheus.yml /etc/prometheus/prometheus.yml
RUN chown nobody:nogroup /etc/prometheus/prometheus.yml && \
    chmod 440 /etc/prometheus/prometheus.yml
USER nobody
