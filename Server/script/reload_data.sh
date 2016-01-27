#!/bin/bash

prefix="/opt/RootZoneExchangeServer"

mv -f $1 $prefix/ZoneExchangeData.in

python $prefix/ReloadExchangeServer.py -k

sudo service named restart
