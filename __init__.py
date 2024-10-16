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
from .local.Data import Cluster
from .local.http import *
from .local import translator


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

	def user_listen(self, user, addr):
		cl = self.cl
		try:
			req = Request(user)
		except:
			return user.close()
			
		if path.startswith('/admin') and addr[0] != '::1':
			user.send(header(404, 'Connection: close', msg='File not found'))
			return user.close()

		# Accept: text/html,
		#					application/xhtml+xml,
		#					application/xml;q=0.9,
		#					image/avif,image/webp,
		#					image/apng,
		#					*/*;q=0.8,
		#					application/signed-exchange;v=b3;q=0.7

		# Accept-Encoding: gzip, deflate

		# Сервер
		# Content-Language: ru

		match method:
			case 'OPTIONS':
				user.send(header(204, 
					'Allow: GET, POST, OPTIONS',
					'Access-Control-Allow-Origin: *',
					'Access-Control-Allow-Methods: GET, POST, OPTIONS',
					'Access-Control-Allow-Headers: Content-Type',
					msg='No Content'))

			case 'GET':
				ct = 'Content-Type: '+headers['Accept'][0]
				if headers['Accept'][0] == 'text/html':
					if path[-1] == '/': path = path[:-1]
					if (x := path+'.html') in cl: path = x

				if path in cl:
					user.send(header(200, 'Connection: close', ct)+cl(path))
				elif (x := '/404.html' in cl):
					user.send(header(200, 'Connection: close', 'Content-Type: text/html')+cl(x))
				else:
					user.send(header(404))

			case 'POST':
				if (x := path+'.system.py') in cl: 
				# match path:
				# 	case '/shop/get':
				# 		names = []
				# 		for name in cl.dir.dir['shop'].dir.keys():
				# 			if not name.endswith('.json'): continue
				# 			names.append(name.split('.')[0])
				# 		user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(names).encode())

				# 	case '/translator':
				# 		try:
				# 			data = json.loads(data)
				# 			mode = data['mode']
				# 			text = data['text']
				# 		except:
				# 			user.send(header(400, 'Connection: close'))
				# 		else:
				# 			if mode == "1":
				# 				text = translator.to_sh(text)
				# 			elif mode == "2":
				# 				text = translator.from_sh(text)
				# 			user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps({'message':text}).encode())
					
				# 	case '/admin/ram':
				# 		data = [{'path':file.opath, 'size':Konvert(file.ram), 'cached':file.cached} for file in self.cl.paths.values()]
				# 		user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(data).encode())

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

			case other_method:
				user.send(header(400, 'Connection: close'))

		user.close()

	def accept_users(self):
		while self.running:
			user, addr = self.sock.accept()
			Thread(target=self.user_closer, args=(user,addr,), daemon=True).start()


if __name__ == '__main__':
	os.chdir(os.path.dirname(__file__))
	app = App()
	app.accept_users()