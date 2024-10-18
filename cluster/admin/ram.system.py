# exit, ret, print, req, user, header, cl

from .local.sizes import Konvert
import json

data = [{'path':file.opath, 'size':Konvert(file.ram), 'cached':file.cached} for file in cl.paths.values()]
user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(data).encode())