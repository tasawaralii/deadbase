#! /usr/bin/env bash
set -e

# cron jobs run with a stripped-down environment (no compose env_file/environment
# vars). Debian's cron reads /etc/environment via pam_env, so dump the container's
# actual environment there before starting the daemon.
printenv | grep -v "no_proxy" > /etc/environment

exec cron -f
