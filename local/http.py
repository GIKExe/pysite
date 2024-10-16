from .sizes import *


class Request:
	def __init__(self, user, debug=False):
		# сырые данные
		raw = user.recv(1*KB)
		if debug: self.raw = raw


		# заголовок, начало данных
		head, data = raw.split(b'\r\n\r\n', 1)
		head = head.decode()
		headers = head.split('\r\n')
		line = headers.pop(0)
		headers = {k: v for k, v in [h.split(': ', 1) for h in headers]}
		self.headers = headers
		self.data = data


		# метод, путь, строка запроса, якорь, версия протокола
		method, path, version = line.split(' ', 2)
		method = method.upper()

		if (x := '#') in path:
			path, fragment = path.split(x, 1)
		else:
			fragment = ''

		if (x := '?') in path:
			path, query = path.split(x, 1)
		else:
			query = ''

		self.method = method
		self.path = path
		self.query = query
		self.fragment = fragment
		self.version = version


		# получение данных до конца
		if 'Content-Length' in headers:
			length = int(headers['Content-Length'])
			while True:
				if len(self.data) >= length: break
				self.data += user.recv(128*KB)


		# дополнительная обработка заголовков
		if (x := 'Accept') in self.headers:
			self.headers[x] = tuple(self.headers[x].split(',') if ',' in self.headers[x] else [self.headers[x],])


class Response:
	def __init__(self):
		...