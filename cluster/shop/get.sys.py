# exit, ret, print, req, user, header, cl
import json

names = []
for name in cl.dir.dir['shop'].dir.keys():
	if not name.endswith('.json'): continue
	names.append(name.split('.')[0])
user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(names).encode())