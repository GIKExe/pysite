B = 1
KB = B * 1024
MB = KB * 1024
GB = MB * 1024

kB = B * 1000
mB = kB * 1000
gB = mB * 1000

def Konvert(x):
	if x >= GB:
		return f'{x/GB:.2f}GB'
	if x >= MB:
		return f'{x/MB:.2f}MB'
	if x >= KB:
		return f'{x/KB:.2f}KB'
	return f'{x}B'