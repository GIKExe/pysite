

def run_code(text, name, **kwargs):
	class ExitException(Exception): ...	
	class ReturnException(Exception): ...	

	_out = {'args': None, 'kwargs': None}

	def out():
		if (x := _out['kwargs']):
			return x
		if (x := _out['args']):
			if len(x) > 1:
				return x
			return x[0]

	def _exit():
		raise ExitException

	def _return(*args, **kwargs):
		if args: _out['args'] = args
		if kwargs: _out['kwargs'] = kwargs
		raise ReturnException

	def _print(*args, **kwargs):
		return print(f'[{name}]:', *args, **kwargs)

	data = {'ret': _return, 'exit': _exit, 'print':_print}
	for k,v in kwargs.items(): data[k] = v
	try: exec(text, data)
	except ExitException: return
	except ReturnException: return out()
	except: raise


if __name__ == '__main__':
	text = '''
print(dir())
print('привет, мир!')
ret(13)
print('sas')
'''
	
	res = run_code(text, 'MAIN')
	print(res)