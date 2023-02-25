#!/usr/bin/env sh

set -o errexit
set -o nounset

# Run python specific scripts:
python /opt/app/manage.py migrate --noinput
python /opt/app/manage.py collectstatic --noinput
python /opt/app/manage.py compilemessages

# Start gunicorn:
# Docs: http://docs.gunicorn.org/en/stable/settings.html
/usr/local/bin/gunicorn server.wsgi \
  --workers=4 `# Sync worker settings` \
  --max-requests=2000 \
  --max-requests-jitter=400 \
  --timeout 120 \
  --bind='0.0.0.0:8000'     `# Run Django on 8000 port` \
  --chdir='/opt/app/server' `# Locations` \
  --log-file=- \
  --worker-tmp-dir='/dev/shm'