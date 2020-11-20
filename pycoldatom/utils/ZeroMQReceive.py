from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import zmq
import pickle

class ZeroMQReceiver(QThread):
	"""A listener receive sequence information from Cicero"""

	messageOut = pyqtSignal(dict)

	def __init__(self,port=6666):
		super(ZeroMQReceiver, self).__init__()
		
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)

		self.port = port

		self.keep_running = False

		self.commands = {}

	def run(self):
		
		self.socket.bind("tcp://*:%d" % self.port)
		while(self.keep_running):
			message = self.socket.recv()
			self.message=pickle.loads(message)
			command = self.message
			self.messageOut.emit(command)
			self.socket.send_string("Have Received Image")

if __name__ == '__main__':
	app = QApplication([])

	listener = ZeroMQReceiver(port = 6666)
	def print_sig(command):
		print(listener.message)

	listener.messageOut.connect(print_sig)

	listener.keep_running = True
	listener.start()

	app.exec_()

