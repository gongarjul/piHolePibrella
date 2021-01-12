#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import pibrella
import logging
from time import sleep
from logging.handlers import RotatingFileHandler

#preparamos el fichero de log
logger = logging.getLogger("piholepibrella-core")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('/home/pi/piholepibrella.log', maxBytes=1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

#establecemos conexión con el servidor
connection = sqlite3.connect('/etc/pihole/pihole-FTL.db')
c = connection.cursor()

#probamos si esta el fichero de configuración y leemos el ultimo id leido
#si no vamos al minimo id de la tabla
try:

    conf = open('/home/pi/piholepibrella.conf','r')
    lastId = int(conf.readline())
    conf.close()
    logger.info("LastId read from file: %d" % (lastId))

except (IOError, ValueError) as e:

    logger.error(str(e))

    c.execute('SELECT min(id) FROM queries')
    r = c.fetchone()
    lastId = r[0]
    logger.info("LastId read from database: %d" % (lastId))

while True:

    try:
        c.execute('SELECT id, status FROM queries WHERE id > :lastId ORDER BY timestamp;', {"lastId": lastId})
        for querie in c.fetchall():

            pibrella.light.off()
            sleep(0.1)

            status = querie[1]
            if status == 1 or status >= 4:
                pibrella.light.red.on();
            elif status == 2:
                pibrella.light.green.on();
            elif status == 3:
                pibrella.light.yellow.on();

            sleep(0.3);
            lastId = querie[0]
        #una vez analizados los registros almacenamos el lastId
        logger.info("LastId read from query: %d" % (lastId))
        conf = open('/home/pi/piholepibrella.conf','w')
        conf.write(str(lastId))
        conf.close()
        
    except (sqlite3.OperationalError, IOError) as e:

        logger.error(str(e))
    
    pibrella.light.off()
    sleep(60)
