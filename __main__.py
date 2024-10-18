# системные
from socket import socket as Socket, AF_INET, AF_INET6, SOCK_STREAM, timeout, IPPROTO_IPV6, IPV6_V6ONLY
from threading import Thread
from time import time, sleep
import os
import json
import base64
from uuid import uuid5, NAMESPACE_DNS

# глобальные

# локальные
from .local.script import run_code
from .local.data import Cluster
from .local.http import *


def header(code, *x, msg='OK'):
	return ('\r\n'.join([f'HTTP/1.1 {code} {msg}'] + list(x) + ['']*2)).encode()


class App:
	host = '::'
	port = 80
	addr = (host, port)
	running = True

	def __init__(self):
		self.sock = Socket(AF_INET6, SOCK_STREAM)
		self.sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
		self.sock.bind(self.addr)
		self.sock.listen()
		self.users = []
		self.cl = Cluster()
		self.cl.ram_limit = 64*MB
		self.cl.init()

	def user_closer(self, user, addr):
		self.user_listen(user, addr)
		user.close()

	def m_OPTIONS(self, user, req):
		user.send(header(204, 
			'Allow: GET, POST, OPTIONS',
			'Access-Control-Allow-Origin: *',
			'Access-Control-Allow-Methods: GET, POST, OPTIONS',
			'Access-Control-Allow-Headers: Content-Type',
		msg='No Content'))

	def m_GET(self, user, req):
		cl = self.cl
		path = req.path
		headers = req.headers

		if path.endswith('.system.py'):
			return user.send(header(403))

		ct = 'Content-Type: '+headers['Accept'][0]
		if headers['Accept'][0] == 'text/html':
			if (path[-1] == '/' and len(path) > 1): path = path[:-1]
			if (opath := path+'.html') in cl:
				return user.send(header(200, 'Connection: close', ct)+cl(opath))

		if path in cl:
			user.send(header(200, 'Connection: close', ct)+cl(path))
		elif (x := '/404.html') in cl:
			user.send(header(200, 'Connection: close', 'Content-Type: text/html')+cl(x))
		else:
			user.send(header(404))

	def m_POST(self, user, req):
		cl = self.cl
		path = req.path
		headers = req.headers

		if (x := path+'.system.py') in cl: path = x
		else: return user.send(header(400))

		code = cl(path).decode('UTF8') # запрашиваю скрипт из кластера
		# print(globals())
		run_code(code, req.path.rsplit('/', 1)[-1],
			user=user,
			req=req,
			header=header,
			cl=cl,
			__name__=__name__,
			__package__=__package__,
		) # выполняем локальный скрипт /*/*.system.py с user, cl, req, header

	def user_listen(self, user, addr):
		cl = self.cl
		try: req = Request(user)
		except: return user.close()
			
		if req.path.startswith('/admin') and addr[0] != '::1':
			return user.send(header(403)), user.close()

		match req.method:
			case 'OPTIONS': self.m_OPTIONS(user, req)
			case 'GET': self.m_GET(user, req)
			case 'POST': self.m_POST(user, req)
			case other_method:
				user.send(header(400, 'Connection: close'))
				# match path:
				# 	case '/shop/get':
				# 		names = []
				# 		for name in cl.dir.dir['shop'].dir.keys():
				# 			if not name.endswith('.json'): continue
				# 			names.append(name.split('.')[0])
				# 		user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(names).encode())
				
				# 	case '/admin/rem':
				# 		try:
				# 			data = json.loads(data)
				# 			uuid = data['uuid']

				# 			opath = f'/shop/{uuid}.json'
				# 			file = cl.paths[opath]
				# 			os.remove(file.path)
				# 			cl.remove(opath)
				# 			del file

				# 			opath = f'/shop/{uuid}.avif'
				# 			file = cl.paths[opath]
				# 			os.remove(file.path)
				# 			cl.remove(opath)
				# 			del file
							
				# 		except:
				# 			user.send(header(400, 'Connection: close'))
				# 			# raise
				# 		else:
				# 			user.send(header(200, 'Connection: close'))
					
				# 	case '/admin/add':
				# 		try:
				# 			data = json.loads(data)
				# 			title = data['title']
				# 			price = data['price']
				# 			description = data['description']
				# 			seller = data['seller']
				# 			photo = data['photo'].split(',', 1)[-1]
				# 			photo = base64.b64decode(photo)
				# 		except:
				# 			user.send(header(400, 'Connection: close'))
				# 			raise
				# 		else:
				# 			uuid = uuid5(NAMESPACE_DNS, title+seller)
				# 			# !обновить директорию/файл в кластере
				# 			with open(f'{cl.name}/shop/{uuid}.avif', 'wb') as file:
				# 				file.write(photo)
				# 			# !обновить директорию/файл в кластере
				# 			with open(f'{cl.name}/shop/{uuid}.json', 'w') as file:
				# 				file.write(json.dumps({'title':title, 'price':price, 'description':description, 'seller':seller}))
				# 			user.send(header(200, 'Connection: close'))
					
				# 	case other_path:
				# 		user.send(header(400, 'Connection: close'))

	def accept_users(self):
		while self.running:
			user, addr = self.sock.accept()
			Thread(target=self.user_closer, args=(user,addr,), daemon=True).start()


if __name__ == '__main__':
	os.chdir(os.path.dirname(__file__))
	app = App()
	app.accept_users()



# {
# 	'__name__': '__main__', 
# 	'__doc__': None, 
# 	'__package__': 'pysite', 
# 	'__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x000002098E5F1CD0>, 
# 	'__spec__': ModuleSpec(name='pysite.__main__', 
# 	  loader=<_frozen_importlib_external.SourceFileLoader object at 0x000002098E5F1CD0>, 
# 	  origin='D:\\User\\Desktop\\pysite\\__main__.py'), 
# 	'__annotations__': {}, 
# 	'__builtins__': <module 'builtins' (built-in)>, 
# 	'__file__': 'D:\\User\\Desktop\\pysite\\__main__.py', 
# 	'__cached__': 'D:\\User\\Desktop\\pysite\\__pycache__\\__main__.cpython-312.pyc', 
# 	'Socket': <class 'socket.socket'>, 
# 	'AF_INET': <AddressFamily.AF_INET: 2>, 
# 	'AF_INET6': <AddressFamily.AF_INET6: 23>, 
# 	'SOCK_STREAM': <SocketKind.SOCK_STREAM: 1>, 
# 	'timeout': <class 'TimeoutError'>, 
# 	'IPPROTO_IPV6': 41, 
# 	'IPV6_V6ONLY': 27, 
# 	'Thread': <class 'threading.Thread'>, 
# 	'time': <built-in function time>, 
# 	'sleep': <built-in function sleep>, 
# 	'os': <module 'os' (frozen)>, 
# 	'json': <module 'json' from 'D:\\Python\\312\\Lib\\json\\__init__.py'>, 'base64': <module 'base64' from 'D:\\Python\\312\\Lib\\base64.py'>, 'uuid5': <function uuid5 at 0x000002098E8DE340>, 'NAMESPACE_DNS': UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'), 'run_code': <function run_code at 0x000002098E8DC400>, 'Cluster': <class 'pysite.local.data.Cluster'>, 'B': 1, 'KB': 1024, 'MB': 1048576, 'GB': 1073741824, 'kB': 1000, 'mB': 1000000, 'gB': 1000000000, 'Konvert': <function Konvert at 0x000002098E8DE840>, 'Request': <class 'pysite.local.http.Request'>, 'Response': <class 'pysite.local.http.Response'>, 'translator': <module 'pysite.local.translator' from 'D:\\User\\Desktop\\pysite\\local\\translator.py'>, 'header': <function header at 0x000002098E5B6840>, 'App': <class '__main__.App'>, 'app': <__main__.App object at 0x000002098E5D1AC0>}