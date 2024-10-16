# import string


# class url:

# 	characters = (
# 		string.ascii_letters +  # A-Z, a-z
# 		string.digits +         # 0-9
# 		'-._~'                  # специальные символы
# 	)

# 	characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-.'

# 	@staticmethod
# 	def decode(encoded_string):
# 		decoded_string = ""
# 		i = 0

# 		while i < len(encoded_string):
# 			if encoded_string[i] == '%':
# 				# Проверка, есть ли достаточно символов после '%'
# 				if i + 2 < len(encoded_string):
# 					hex_value = encoded_string[i + 1:i + 3]  # Получаем два символа после '%'
# 					try:
# 						# Преобразуем шестнадцатеричное значение в десятичное
# 						decoded_char = chr(int(hex_value, 16))
# 						decoded_string += decoded_char
# 						i += 3  # Пропускаем '%XX'
# 					except ValueError:
# 						# Если невалидное значение, добавляем '%' и продолжаем
# 						decoded_string += '%'
# 						i += 1
# 				else:
# 					# Если '%' в конце строки без двух символов после
# 					decoded_string += '%'
# 					i += 1
# 			else:
# 				decoded_string += encoded_string[i]
# 				i += 1

# 		return decoded_string


# 	@staticmethod
# 	def encode(input_string):
# 		encoded_string = ""
		
# 		for char in input_string:
# 			if char in url.characters:
# 				encoded_string += char
# 			else:
# 				print(ord(char), 'vs', char.encode('UTF8'))
# 				encoded_string += '%' + format(ord(char), '02X')

# 		return encoded_string


# # def unquote(string, encoding='utf-8', errors='replace'):
# # 	"""Replace %xx escapes by their single-character equivalent. The optional
# # 	encoding and errors parameters specify how to decode percent-encoded
# # 	sequences into Unicode characters, as accepted by the bytes.decode()
# # 	method.
# # 	By default, percent-encoded sequences are decoded with UTF-8, and invalid
# # 	sequences are replaced by a placeholder character.

# # 	unquote('abc%20def') -> 'abc def'.
# # 	"""
# # 	if '%' not in string: return string
# # 	bits = _asciire.split(string)
# # 	res = [bits[0]]
# # 	append = res.append
# # 	for i in range(1, len(bits), 2):
# # 		append(unquote_to_bytes(bits[i]).decode(encoding, errors))
# # 		append(bits[i + 1])
# # 	return ''.join(res)

if __name__ == '__main__':
	from parse import urlsplit as __encode
	from parse import unquote as __decode
else:
	from .parse import urlsplit as __encode
	from .parse import unquote as __decode

# def encode(*args, **kwargs):
# 	scheme = __encode(*args, **kwargs)
# 	return 

if __name__ == '__main__':
	print(__encode("привет мир! #123"))
	# print(decode("xxx"))