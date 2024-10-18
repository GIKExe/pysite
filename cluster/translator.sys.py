# exit, ret, print, req, user, header, cl

from .local import translator
import json

try:
	data = json.loads(req.data)
	mode = data['mode']
	text = data['text']
except:
	user.send(header(400, 'Connection: close'))
else:
	if mode == "1":
		text = translator.to_sh(text)
	elif mode == "2":
		text = translator.from_sh(text)
	user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps({'message':text}).encode())