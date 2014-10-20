#! /usr/bin/python
#
# parse_hyperion.py
# receive commands from the android hyperion app
#
# 2014 (c) juewei@fabfolk.com
# Apply GPLv2.0 or ask.
#

import socket, sys, json
HOST = ''   	# Symbolic name, meaning all available interfaces
PORT = 19444	# Hyperion port

def parse_hyperion(data):
  """
     expected json format:
     {"command":"color","priority":50,"color":[99,0,28],"duration":14400000}
  """
  try:
    d = json.loads(data)
    rgb = d['color']
    print "r=%d, g=%d, b=%d" % (rgb[0], rgb[1], rgb[2])
  except Exception as e:
    print >>sys.stderr, "%s: bad json: '%s'\n" % (e, data)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

s.listen(5)


# check if s or conn are redable without blocking:
# r = select.select([s, conn], [], [], 0)

while 1:
    #wait to accept a connection - blocking call
    print 'waiting...'
    conn, addr = s.accept()
    try:
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        while True:
            data = conn.recv(256)
	    # print >>sys.stderr, 'received "%s"' % data
	    if not data:
	        break
	    parse_hyperion(data)
	    conn.send("{\"success\": true}\n")
    finally:
        print 'Closing ' + addr[0] + ':' + str(addr[1])
        conn.close()

s.close()
