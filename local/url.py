

x16 = '0123456789ABCDEF'
allow = 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '0123456789' + '_.-~'
other = {
	' ': '%20',
	'!': '%21',
	'"': '%22',
	# '#': '%23',
	'$': '%24',
	'%': '%25',
	# '&': '%26',
	"'": '%27',
	'*': '%2A',
	# '+': '%2B',
	',': '%2C',
	':': '%3A',
	';': '%3B',
	'<': '%3C',
	# '=': '%3D',
	'>': R'%3E',
	# '?': R'%3F',
	'[': '%5B',
	']': '%5D',
	'^': R'%5E',
	'`': '%60',
	'{': '%7B',
	'|': '%7C',
	'}': '%7D',
	# '': '%',
}


def encode(text):
	out = ''
	for s in text:
		if s in allow: out += s
		elif s in other: out += other[s]
		else:
			out += str(s.encode('UTF8'))[2:-1].replace('\\x', '%').upper()
	return out

def decode(text):
	i = 0
	out = ''
	while i < len(text):
		s = text[i]
		if s != '%':
			i += 1; out += s; continue
		s = text[i:i+3]
		if (s[-2] not in x16) or (s[-1] not in x16):
			i += 3; out += s; continue
		if s in other.values():
			i += 3; out += other.keys()[other.values().index(s)]; continue
		s = text[i:i+6]
		i += 6; out += bytes([int(x, 16) for x in s[1:].split('%')]).decode('UTF8')
	return out

# общая URL
# СХЕМА://Логин:Пароль@Хост:Порт/Путь?Параметры#Якорь
# серверная URL
# /Путь?Параметры#Якорь
