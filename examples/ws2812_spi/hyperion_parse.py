#! /usr/bin/python
#
# parse_hyperion.py
# receive commands from the android hyperion app
#
# 2014 (c) juewei@fabfolk.com
# Apply GPLv2.0 or ask.
#

import socket, select, sys, time, json

HOST = ''   	# Symbolic name, meaning all available interfaces
PORT = 19444	# Hyperion port

def parse_hyperion(data):
  """
     expected json format:
     {"command":"color","priority":50,"color":[99,0,28],"duration":14400000}
  """
  try:
    d = json.loads(data)
  except Exception as e:
    print >>sys.stderr, "%s: bad json: '%s'\n" % (e, data)
    return

  if d:
    if d.has_key('color'):
      rgb = d['color']
      print "r=%d, g=%d, b=%d" % (rgb[0], rgb[1], rgb[2])
    else:
      print "unknown json command: %s" % data


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Bind socket to local host and port
try:
    server.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

server.listen(5)

ss = {}
ss[server.fileno()] = server


def poll_socks(ss):
    data = None
    r = select.select(ss.values(), [], [], 0)[0]
    for s in r:
        if s == server:
            conn, addr = s.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
	    ss[conn.fileno()] = conn
	else:
	    data = s.recv(256)
	    if not data:
	        del(ss[s.fileno()])
                print 'Closing fd=' + str(s.fileno())
		s.close()
	    else:
	    	s.send("{\"success\": true}\n")
    return data 


while 1:
    data = poll_socks(ss)
    if (data): parse_hyperion(data)
    time.sleep(0.2)
    print >> sys.stderr, ".",

server.close()
