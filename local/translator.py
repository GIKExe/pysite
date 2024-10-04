from random import randint

# АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ
# абвгдеёжзийклмнопрстуфхцчшщъыьэюя

__all__ = ['to_sh', 'from_sh']
sl = {v: k+1 for k, v in enumerate(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'))}
ls = {v: k for k, v in sl.items()}

def to_sh(text):
	res = ''
	for s in text:
		isLower = (s == s.lower())
		s = s.lower()
		if s not in sl:
			res += s
			continue
		i = sl[s]
		cb = []
		for s1, i1 in sl.items():
			for s2, i2 in sl.items():
				if (s not in 'ая') and (s in (s1, s2)): continue
				x = i1+i2
				if (x % 2 > 0): continue
				x //= 2
				if (x > 33): continue
				if (x != i): continue
				cb.append(s1 + s2)
		if len(cb) == 1:
			index = 0
		else:
			# print(cb)
			index = randint(0, len(cb)-1)
		sf = cb[index]
		res += sf if isLower else sf.upper()
	return res

def from_sh(text):
	res = ''
	buf = None
	for s in text:
		isLower = (s == s.lower())
		s = s.lower()
		if s not in sl:
			res += s
			continue
		elif (s in sl) and buf:
			index = (sl[s] + sl[buf]) // 2
			buf = None
			sf = ls[index]
			res += sf if isLower else sf.upper()
		else:
			buf = s
			continue
	return res


if __name__ == '__main__':
	x = to_sh('Привет, мир!')
	print(x)
	print(from_sh(x))
