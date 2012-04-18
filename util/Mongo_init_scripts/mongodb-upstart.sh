#!/bin/sh
# Ubuntu upstart file at /etc/init/mongodb.conf

pre-start script
    mkdir -p /var/lib/mongodb/
    mkdir -p /var/log/mongodb/
end script

start on runlevel [2345]
stop on runlevel [06]

script
  ENABLE_MONGODB="yes"
  if [ -f /etc/default/mongodb ]; then . /etc/default/mongodb; fi
  if [ "x$ENABLE_MONGODB" = "xyes" ]; then
        if [ -f /var/lib/mongodb/mongod.lock ]; then
                rm /var/lib/mongodb/mongod.lock
                sudo -u fccoelho $(which mongod) --config /etc/mongodb.conf --repair
        fi
        exec start-stop-daemon --start --quiet --chuid fccoelho --exec  $(which mongod) -- --rest --config /etc/mongodb.conf
  fi
end script