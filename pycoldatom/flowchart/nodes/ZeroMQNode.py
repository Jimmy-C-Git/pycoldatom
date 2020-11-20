from pyqtgraph.flowchart import Node
from pyqtgraph.parametertree import Parameter, ParameterTree

from ...widgets.fileBrowser import FileBrowser

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os

from scipy.io import loadmat, savemat

from ...utils.autosave import getAutosaveFileName
from ...utils.ZeroMQSend import ZeroMQSender
from ...utils.ZeroMQReceive import ZeroMQReceiver

class ZeroMQNode(Node):
	"""Node for loading a .mat file of MATLAB.
	Files are selected in a simple explorer

	Output terminals:
	- title: file name
	- data: return of scipy.loadmat
	"""

	nodeName = 'ZeroMQNode'
	nodePaths = [('File',)]

	def __init__(self, name):
		super().__init__(name, terminals={'tosend':{'io':'in'}, 'received': {'io': 'out'}})
		
		paras_property = [
			{'name': 'changeMode', 'type': 'action'},
			{'name': 'mode', 'type': 'str','value':'close', 'readonly':True},
	#		{'name': 'residual', 'type': 'float', 'readonly': True},
#			{'name': 'trunc', 'type': 'float'},
		#	{'name': 'send or receive', 'type': 'bool'},
			{'name': 'ip', 'type': 'str'},
			{'name': 'port', 'type': 'int'}
		]

		self.paras = Parameter.create(name='params', type='group', children=paras_property)
		self.paratree = ParameterTree()
		self.paratree.setParameters(self.paras, showTop=False)
		self.send = ZeroMQSender(ip= "127.0.0.1", port =6666)
		self.receive = ZeroMQReceiver(port= 6666)
		self.receive.keep_running = True
		self.paras.param('changeMode').sigActivated.connect(self.onChangeMode)
		self.receive.messageOut.connect(self.handleWithReceivedMessage)

	def handleWithReceivedMessage(self ,message):
		print("Received image")
		self.setOutput(received=message)

	def ctrlWidget(self):
		return self.paratree

	def onChangeMode(self):
		if self.paras['mode'] == 'send':
			self.receive.keep_running =True
			self.receive.start()
			self.paras['mode'] = 'receive'

		elif self.paras['mode'] == 'receive':
			self.paras['mode'] = 'close'
			self.receive.keep_running =False
			self.receive.quit()
			self.receive.wait()
			self.send.quit()
			self.send.wait()
		else :
			self.paras['mode'] = 'send'
			self.receive.keep_running =False
			self.receive.quit()
			self.receive.wait()



	def process(self, tosend, display=True):
		if self.paras['mode'] == 'send':
			print(self.send.state)
			if self.send.state ==  'sending':
				self.send.quit()
				self.send.wait()
			self.send.message = tosend
			self.send.start()
			return {}
		if self.paras['mode'] == 'receive':
			print("Received2")
			return {'received':self.receive.message}

	def manageThread(self):
		pass

	def saveState(self):
		state = super().saveState()
		return state

	def restoreState(self, state):
		super().restoreState(state)

	def close(self):
		self.send.keep_running = False
		self.send.terminate()
	#	self.send.wait()
		self.receive.terminate()
	#	self.receive.quit()
	#	self.receive.wait()
		super().close()


nodelist = [ZeroMQNode]

