from .sizes import *
from . import url


# class BetterDict(dict):
# 	def __init__(self, d):
# 		for key, value in d.items():
# 			self.__setattr__(key, value)

# 	def __getattr__(self, key):
# 		return (self[key] if key in self else None)

# 	def __setattr__(self, key, value):
# 		self[key] = (BetterDict(value) if type(value) is dict else value)

# 	def __delattr__(self, key):
# 		del self[key]


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

		path = url.decode(path)

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
	def __init__(self, headers={}, code=200, msg='OK', data=''):
		self.version = 'HTTP/1.1'
		self.code = code
		self.msg = msg

		if (x := 'Connection') not in headers: headers[x] = 'close'
		self.headers = {k: v for k,v in headers.items()}

		self.data = data

	@property
	def raw(self):
		b1 = f'{self.version} {self.code} {self.msg}'.encode()
		if (x := len(self.data)) > 0:
			self.headers['Content-Length'] = x
		b2 = '\r\n'.join([f'{k}: {v}' for k,v in self.headers.items()]).encode()
		b3 = (self.data.encode() if type(self.data) is str else self.data)
		return b'\r\n'.join([b1, b2, b'', b3])

	def send(self, user):
		user.send(self.raw)