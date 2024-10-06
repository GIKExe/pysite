# системные
from socket import socket as Socket, AF_INET, AF_INET6, SOCK_STREAM, timeout, IPPROTO_IPV6, IPV6_V6ONLY
from threading import Thread
from time import time, sleep
import os
import json
import base64
import uuid

# глобальные
# локальные
from local.Data import Cluster
from local.sizes import *
from local import translator


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
			raw = user.recv(1*KB)
			headers, data = raw.split(b'\r\n\r\n', 1)
			headers = headers.decode()
			headers = headers.split('\r\n')
			line = headers.pop(0)
			method, path, version = line.split(' ')
			if '?' in path:
				path, lq = path.split('?', 1)
			else:
				lq = ''
			headers = {k: v for k, v in [h.split(': ', 1) for h in headers]}
		except:
			return user.close()

		if 'Accept' in headers:
			headers['Accept'] = (headers['Accept'].split(',') if ',' in headers['Accept'] else [headers['Accept'],])
		else:
			headers['Accept'] = ['*/*']

		

		if 'Content-Length' in headers:
			Content_Length = int(headers['Content-Length'])
			while True:
				if len(data) >= Content_Length: break
				data += user.recv(128*KB)
	
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

		if method == 'GET':
			match headers['Accept'][0]:
				case 'text/html':
					if path.endswith('/'):
						if path != '/': path = path[:-1]
						path += '.html'
					ct = 'Content-Type: text/html'
				case other:
					ct = 'Content-Type: '+other

			if path in cl:
				user.send(header(200, 'Connection: close', ct)+cl(path))
			else:
				user.send(header(200, 'Connection: close', 'Content-Type: text/html')+cl('/404.html'))

		elif method == 'POST':
			match path:
				
				case '/shop/get':
					names = []
					for name in cl.dir.dir['shop'].dir.keys():
						if not name.endswith('.json'): continue
						names.append(name.split('.')[0])
					user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(names).encode())

				case '/translator':
					try:
						data = json.loads(data)
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
				
				case '/admin/ram':
					data = [{'path':file.opath, 'size':Konvert(file.ram), 'cached':file.cached} for file in self.cl.paths.values()]
					user.send(header(200, 'Content-Type: application/json', 'Connection: close')+json.dumps(data).encode())
				
				case '/admin/add':
					try:
						data = json.loads(data)
						title = data['title']
						price = data['price']
						description = data['description']
						seller = data['seller']
						photo = data['photo'].split(',', 1)[-1]
						photo = base64.b64decode(photo)
					except Exception as e:
						print(e)
						user.send(header(400, 'Connection: close'))
					else:
						text_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, title+seller)
						with open(f'{cl.name}/shop/{text_uuid}.avif', 'wb') as file:
							file.write(photo)
						with open(f'{cl.name}/shop/{text_uuid}.json', 'w') as file:
							file.write(json.dumps({'title':title, 'price':price, 'description':description, 'seller':seller}))
						user.send(header(200, 'Connection: close'))
				
				case other:
					user.send(header(400, 'Connection: close'))
		user.close()

	def accept_users(self):
		while self.running:
			user, addr = self.sock.accept()
			Thread(target=self.user_closer, args=(user,addr,), daemon=True).start()


if __name__ == '__main__':
	app = App()
	app.accept_users()