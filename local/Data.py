
from time import time
from os import listdir, sep
from os.path import exists, isfile, isdir, getsize, join, getctime, getmtime

from .sizes import *

# __all__ = ['File', 'Dir', 'Cluster']


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


class File:
	def check(self):
		if not exists(self.path):
			raise Exception(f'Путь не существует: {self.path}')
		if not isfile(self.path):
			raise Exception(f'Путь не является файлом: {self.path}')

	def __init__(self, path, cl, cached=False):
		self.path = path
		self.check()
		self.t = 0
		self.mt = 0
		self.ut = 15
		self.raw = b''
		# self.old_size = 0
		self.size = getsize(path)
		self.cached = cached
		self.opath = None
		self.cl = cl

	@property
	def ram(self):
		if self.cached:
			return self.size
		return 0

	@property
	def data(self):
		if self.cached:
			self.update()
			return self.raw
		return self.read()

	def read(self):
		with open(self.path, 'rb') as file:
			return file.read()

	def update(self):
		if (time() - self.t < self.ut): return
		if not exists(self.path):
			return self.cl.remove(self.opath)

		mt = getmtime(self.path)
		if (self.mt == mt): return
		size = getsize(self.path)
		if not self.cl.change(self, self.opath, size, self.size):
			self.cached = False
			self.raw = b''
		self.raw = self.read()
		self.size = size
		self.t = time()
		self.mt = mt
		self.cl.update()


class Dir:
	def check(self):
		if not exists(self.path):
			raise Exception(f'Путь не существует: {self.path}')
		if not isdir(self.path):
			raise Exception(f'Путь не является директорией: {self.path}')

	def __init__(self, path, cl):
		self.path = path
		self.check()
		self.cl = cl
		self.t = 0
		self.ut = 15
		self.dir = {}

	def __iter__(self):
		return iter(self.dir)

	def __contains__(self, value):
		return value in self.dir

	def items(self):
		return self.dir.items()

	def update(self):
		if time() - self.t < self.ut: return
		names = list(self.dir.keys())
		for name in listdir(self.path):
			if name in self.dir:
				names.pop(names.index(name))
				if type(self.dir[name]) is Dir:
					self.dir[name].update()
				continue
			path = join(self.path, name)
			if isdir(path):
				self.dir[name] = Dir(path, self.cl)
			elif isfile(path):
				self.dir[name] = File(path, self.cl)
				self.cl.add(self.dir[name])
		for name in names:
			del self.dir[name]


class Cluster:
	def __init__(self, path='cluster'):
		self.dir = Dir(path, self)
		self.ram_limit = 1*MB
		self.path = path
		self.paths = {}
		if sep in path:
			self.name = path.rsplit(sep, 1)[-1]
		else:
			self.name = path

	def create_opath(self, path):
		return path.split(self.name)[-1].replace('\\', '/')

	@property
	def ram(self):
		return sum([file.ram for file in self.paths.values()])

	def __contains__(self, value):
		return value in self.paths

	def __call__(self, opath):
		return self.paths[opath].data
			
	def init(self):
		print(f'Загрузка кластера: "{self.name}"')
		self.update()
		self.print_ram()

	def update(self):
		self.dir.update()

	def add(self, file):
		file.opath = self.create_opath(file.path)
		self.paths[file.opath] = file
		if self.ram + file.size > self.ram_limit:
			return print(f'ADD 0 {file.opath}')
		file.cached = True
		print(f'ADD 1 {file.opath}')

	def change(self, file, opath, size, old_size, log=True):
		ram = self.ram
		if ram - old_size + size <= self.ram_limit:
			difference = size - old_size
			text = ('-' if difference < 0 else '+')+Konvert(abs(difference))
			print(f'MOD 1 {opath} {text}')
			return True
		print(f'MOD 0 {opath} {text}')
		return False
		
	def remove(self, opath):
		del self.paths[opath]
		print(f'REM - {opath}')

	def print_ram(self):
		ram = self.ram
		print(f'{Konvert(ram)}/{Konvert(self.ram_limit)}, {ram/self.ram_limit*100:.2f}%')


# class Request:
# 	def __init__(self, raw):
# 		self.raw = raw
# 		self.headers, self.data = raw.split(b'\r\n\r\n', 1)
# 		self.headers = self.headers.decode()
# 		self.headers = self.headers.split('\r\n')
# 		self.method, self.path, self.version = self.headers.pop(0).split(' ', 2)


# class Response:
# 	def __init__(self):
# 		...

# 	@property
# 	def raw(self):
# 		return b''