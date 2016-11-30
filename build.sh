#!/bin/sh

MAKEOPTS="-j2"

#echo -n "Downloading ode-0.12..." &&
#wget https://sourceforge.net/projects/opende/files/ODE/0.12/ode-0.12.tar.bz2 > /tmp/odewget 2>&1 &&
#echo "done" &&

echo -n "Unpacking ode-0.12.tar.bz2..." &&
tar -xjf ode-0.12.tar.bz2 &&
echo "done" &&

mkdir -p ~/ode_temp
touch ~/ode_temp/odeconfigure
touch ~/ode_temp/odemake
touch ~/ode_temp/pyrosimmake
echo -n "Building ode-0.12..." &&
cd ode-0.12 &&
#./configure --enable-double-precision > /tmp/odeconfigure 2>&1 &&
#make $MAKEOPTS > /tmp/odemake 2>&1 &&
./configure --enable-double-precision > ~/ode_temp/odeconfigure 2>&1 &&
make $MAKEOPTS > ~/ode_temp/odemake 2>&1 &&
cd .. &&
echo "done" &&

echo -n "Building simulator..." &&
#make $MAKEOPTS > /tmp/pyrosimmake 2>&1 &&
make $MAKEOPTS > ~/ode_temp/pyrosimmake 2>&1 &&
rm -rf ~/ode_temp/
echo "done"
