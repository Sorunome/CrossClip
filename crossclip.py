#!/usr/bin/python3
## -*- coding: utf-8 -*-
import sys,os,json,pyperclip,socketserver,socket,threading
from gi.repository import Notify
Notify.init("Cross Clip")

class Config:
	def __init__(self):
		self.readFile()
	def readFile(self):
		f = open('config.json')
		lines = f.readlines()
		self.json = json.loads("\n".join(lines))
		f.close()
	def save(self):
		f = open('config.json','w')
		json.dump(self.json,f)
		f.close()
config = Config()

#gCn bridge
connectedClients = []
class ClientThread(socketserver.BaseRequestHandler):
	stopnow=False
	def stopThread(self):
		print('Giving signal to quit client...')
		self.stopnow = True
	def checkExit(self):
		if self.stopnow:
			print('exiting...')
	def handle(self):
		global config
		self.readbuffer = ''
		self.host = ''
		self.verified = 0
		self.quiet = False
		try:
			self.request.settimeout(10)
			connectedClients.append(self)
			while not self.stopnow:
				try:
					data = self.request.recv(1024)
				except socket.error as e:
					if isinstance(e.args):
						if e == errno.EPIPE:
							self.stopnow = True
				except Exception as inst:
					raise
				if data.decode('utf-8') == '':
					self.stopnow = True
				self.readbuffer += data.decode('utf-8')
				temp = self.readbuffer.split('\n')
				self.readbuffer = temp.pop()
				for line in temp:
					command = line.split(' ')[0]
					arg = ' '.join(line.split(' ')[1:])
					if command == 'verify' and arg == config.json['key']:
						self.verified = 1
					elif self.verified == 1 and command == 'host':
						self.host = arg
						self.verified = 2
					if self.verified == 2:
						if command == 'quiet':
							self.quiet = True
						elif command == 'setclipboard':
							clipcontent = str(arg)
							clipcontent = clipcontent.replace('\\n','\n')
							clipcontent = clipcontent.replace('\\\n','\\n')
							clipcontent = clipcontent.replace('\\\\','\\')
							pyperclip.copy(clipcontent)
							if not self.quiet:
								Notify.Notification.new('Cross Clip','%s has modified your clipboard content to <b>%s</b>' % (self.host,clipcontent)).show()
		except:
			self.stopnow = True
			raise
		connectedClients.remove(self)
		print('Thread done\n')
class ThreadedTCPServer(socketserver.ThreadingMixIn,socketserver.TCPServer):
	allow_reuse_address = True
	pass


class Client():
	def __init__(self,host):
		global config
		self.s = socket.socket()
		self.s.settimeout(0.5)
		self.s.connect((host,config.json['port']))
		self.send('verify %s' % config.json['key'])
		self.send('host %s' % socket.gethostname())
	def send(self,s):
		self.s.sendall(bytes('%s\n' % str(s),'utf-8'))
if __name__ == '__main__':
	args = {
		'server':False,
		'host':'',
		'quiet':False,
		'send':False
	}
	for arg in sys.argv:
		attr = '='.join(arg.split('=')[1:])
		arg = arg.lower().split('=')[0]
		if arg == 'server':
			args['server'] = True
		elif arg == 'host' or arg == 'h':
			print(attr)
			args['host'] = attr
		elif arg == 'quiet' or arg == 'q':
			args['quiet'] = True
		elif arg == 'send' or arg == 's':
			args['send'] = True
	
	if args['server']:
		server = ThreadedTCPServer(('',config.json['port']),ClientThread)
		try:
			server.serve_forever()
		except KeyboardInterrupt:
			print('Giving signal to quit')
			for i in connectedClients:
				i.stopThread()
			sys.exit()
		except Exception as inst:
			print(inst)
			pass
	else:
		client = Client(args['host'])
		if args['quiet']:
			client.send('quiet')
		if args['send']:
			clipcontent = pyperclip.paste()
			clipcontent = clipcontent.replace('\\','\\\\')
			clipcontent = clipcontent.replace('\n','\\n')
			print(clipcontent)
			if not args['quiet']:
				Notify.Notification.new('Cross Clip','Setting the clipboard of %s to <b>%s</b>' % (args['host'],clipcontent)).show()
			client.send('setclipboard %s' % clipcontent)