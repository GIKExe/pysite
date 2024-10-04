# системные
from socket import socket as Socket, AF_INET, AF_INET6, SOCK_STREAM, timeout, IPPROTO_IPV6, IPV6_V6ONLY
from threading import Thread
from time import time, sleep
import os
import json

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
		self.cl.init()

	def user_closer(self, user, addr):
		self.user_listen(user, addr)
		user.close()

	def user_listen(self, user, addr):
		cl = self.cl
		try: raw = user.recv(10240)
		except: return
		if not raw: return

		try:
			headers, data = raw.split(b'\r\n\r\n', 1)
			headers = headers.decode()
			headers = headers.split('\r\n')
			line = headers.pop(0)
			headers = {k: v for k, v in [h.split(': ', 1) for h in headers]}
			method, path, version = line.split(' ')
		except:
			return

		if path == '/admin' and addr[0] != '::1':
			return user.send(header(404, 'Connection: close', msg='File not found'))
			
		if method == 'GET':
			# линковка страниц и объектов
			if path == '/':
				path+='.html'
			if path.endswith('/'):
				path = path[:-1] + '.html'

			# автоопределение типа
			if path.endswith('.html'):
				ct = 'Content-Type: text/html'
			elif path.endswith('.css'):
				ct = 'Content-Type: text/css'

			# поиск объекта в кластере
			if path in cl:
				user.send(header(200, 'Connection: close', ct)+cl(path))
			elif path.endswith('.html'):
				user.send(header(200, 'Connection: close', ct)+cl('/404.html'))
			else:
				user.send(header(404, 'Connection: close', msg='File not found'))

		elif method == 'POST':
			if path == '/translator':
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
			else:
				user.send(header(400, 'Connection: close'))

	def accept_users(self):
		while self.running:
			user, addr = self.sock.accept()
			Thread(target=self.user_closer, args=(user,addr,), daemon=True).start()


if __name__ == '__main__':
	app = App()
	app.accept_users()