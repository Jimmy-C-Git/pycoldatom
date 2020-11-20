from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import zmq
import pickle

class ZeroMQSender(QThread):
	"""A listener receive sequence information from Cicero"""



	def __init__(self, ip = "127.0.0.1", port=6666, message = {}):
		super(ZeroMQSender, self).__init__()
		context = zmq.Context()
		self.socket = context.socket(zmq.REQ)
		self.ip = ip
		self.port = port
		self.socket.connect ("tcp://"+ip+":%d" % self.port)
		self.message = message
		self.state = 'clear'

	def run(self):
		self.state = 'sending'
		self.socket.send(pickle.dumps(self.message))
		message = self.socket.recv_string()
		print(message)
		self.state = 'fininshed'

if __name__ == '__main__':
	app = QApplication([])
	pub = ZeroMQSender(ip ="127.0.0.1", port=6666 ,message={"me":"image:hello world"})
	pub.start()

	app.exec_()

