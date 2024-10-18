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
from .local.http import Request, Response
from .local.sizes import *

def header(code, *x, msg='OK'):
	return ('\r\n'.join([f'HTTP/1.1 {code} {msg}'] + list(x) + ['']*2)).encode()


class Server:
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
		self.cl.ram_limit = 1*MB
		self.cl.init()

	def m_OPTIONS(self, user, req):

		# вариант 1
		# user.send(header(204, 
		# 	'Allow: GET, POST, OPTIONS',
		# 	'Access-Control-Allow-Origin: *',
		# 	'Access-Control-Allow-Methods: GET, POST, OPTIONS',
		# 	'Access-Control-Allow-Headers: Content-Type',
		# msg='No Content'))

		# вариант 2
		Response({
			'Allow': 'GET, POST, OPTIONS',
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
			'Access-Control-Allow-Headers': 'Content-Type',
		}, 204, 'No Content').send(user)

	def m_GET(self, user, req):
		cl = self.cl
		path = req.path
		headers = req.headers

		# print(path)

		if path.endswith('.sys.py'):
			# вариант 1
			# return user.send(header(403))
			# вариант 2
			return Response(code=403).send(user)

		ct = 'Content-Type: '+headers['Accept'][0]
		if headers['Accept'][0] == 'text/html':
			if (path[-1] == '/' and len(path) > 1): path = path[:-1]
			if (opath := path+'.html') in cl:
				# вариант 1
				# return user.send(header(200, 'Connection: close', ct)+cl(opath))
				# вариант 2
				return Response({'Content-Type': 'text/html'}, code=200, data=cl(opath)).send(user)

		if path in cl:
			# вариант 1
			# user.send(header(200, 'Connection: close', ct)+cl(path))
			# вариант 2
			Response(code=200, data=cl(path)).send(user)
		elif (x := '/404.html') in cl:
			user.send(header(200, 'Connection: close', 'Content-Type: text/html')+cl(x))
		else:
			user.send(header(404))

	def m_POST(self, user, req):
		cl = self.cl
		path = req.path
		headers = req.headers

		if (x := path+'.sys.py') in cl: path = x
		# вариант 1
		# else: return user.send(header(400))
		# вариант 2
		else: return Response(code=400).send(user)

		code = cl(path).decode('UTF8')
		run_code(code, req.path.rsplit('/', 1)[-1],
			user=user,
			req=req,
			header=header,
			cl=cl,
			__name__=__name__,
			__package__=__package__,
		)

	def user_listen(self, user, addr):
		cl = self.cl
		try: req = Request(user)
		except: return user.close()

		match req.method:
			case 'OPTIONS': self.m_OPTIONS(user, req)
			case 'GET': self.m_GET(user, req)
			case 'POST': self.m_POST(user, req)
			case other_method:
				# вариант 1
				# user.send(header(400, 'Connection: close'))
				# вариант 2
				Response(code=400).send(user)
		user.close()

	def accept_users(self):
		while self.running:
			user, addr = self.sock.accept()
			Thread(target=self.user_listen, args=(user,addr,), daemon=True).start()

	def run(self):
		self.accept_users()


if __name__ == '__main__':
	os.chdir(os.path.dirname(__file__))
	server = Server()
	server.run()