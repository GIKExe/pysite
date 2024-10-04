
from local.Data import BetterDict

if __name__ == '__main__':
	test = BetterDict({'r1': {}})
	test.r1.r2 = {'r3': 'hello'}
	print(test.items())