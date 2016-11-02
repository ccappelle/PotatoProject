#!/bin/sh

MAKEOPTS="-j2"

echo -n "Building simulator..." &&
make $MAKEOPTS > /tmp/pyrosimmake 2>&1 &&
echo "done"