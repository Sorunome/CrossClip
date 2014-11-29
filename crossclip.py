#!/usr/bin/python3
## -*- coding: utf-8 -*-
import sys,os,json,pyperclip
class Config:
	def __init__(self):
		self.readFile()
	def readFile(self):
		f = open(PROGDIR+'config.json')
		lines = f.readlines()
		self.json = json.loads("\n".join(lines))
		f.close()
	def save(self):
		f = open(PROGDIR+'config.json','w')
		json.dump(self.json,f)
		f.close()
config = Config()
print(config.json)
if __name__ == '__main__':
	args = {
		'server':False
	}
	for arg in sys.argv:
		arg = arg.lower()
		if arg == 'server':
			args['server'] = True
	print(args)