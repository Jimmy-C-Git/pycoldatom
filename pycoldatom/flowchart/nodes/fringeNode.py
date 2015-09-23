from pyqtgraph.flowchart import Node
import numpy as np
from ...functions.fringe import FringeRemove

from pyqtgraph.parametertree import Parameter, ParameterTree
from PyQt5.QtWidgets import QFileDialog, QProgressDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication
from scipy.io import loadmat

class FringeRemoveNode(Node):
	"""Node for removing fringes"""

	nodeName = 'FringeRemove'
	nodePaths = [('Analysis',)]

	def __init__(self, name):
		terminals = {
			'sig':{'io':'in'},
			'ref':{'io':'in'},
			'sigMask': {'io':'in'},
			'ref1':{'io':'out', 'bypass': 'ref'}
		}
		super().__init__(name, terminals=terminals)

		paras_property = [
			{'name': 'import', 'type': 'action'},
			{'name': 'ref label', 'type': 'str'},
			{'name': 'bkg label', 'type': 'str'},
			{'name': 'rank', 'type': 'int', 'readonly': True},
			{'name': 'rankLimit', 'type': 'int', 'value': 100},
			{'name': 'residual', 'type': 'float', 'readonly': True},
			{'name': 'trunc', 'type': 'float'},
			{'name': 'updateLib', 'type': 'bool'},
			{'name': 'reset', 'type': 'action'}
		]

		self.paras = Parameter.create(name='params', type='group', children=paras_property)
		self.paratree = ParameterTree()
		self.paratree.setParameters(self.paras, showTop=False)
		self.remover = FringeRemove()

		self.paras.param('reset').sigActivated.connect(self.remover.reset)
		self.paras.param('import').sigActivated.connect(self.onImport)
	
	def onImport(self):
		filenames = QFileDialog.getOpenFileNames(None, 'Import', None, "MATLAB files (*.mat)")[0]
		if not filenames:
			return

		reflabel = self.paras['ref label']
		bkglabel = self.paras['bkg label']
		self.remover.setTrunc(self.paras['trunc'])
		print('trunc', self.paras['trunc'])
		n_imported = 0
		try:
			progress = QProgressDialog("Importing...", "Abort", 0, len(filenames)-1, self.flowchart.win)
			for i, f in enumerate(filenames):
				if progress.wasCanceled():
					break
				data = loadmat(f)
				if reflabel not in data:
					continue
				ref = data[reflabel]
				if bkglabel in data:
					ref = ref - data[bkglabel]
				if self.paras['rank'] <= self.paras['rankLimit']:
					self.remover.updateLibrary(ref)
					self.paras['rank'] = self.remover.rank
					self.paras['residual'] = self.remover.residual
					n_imported += 1
				else:
					break
				progress.setValue(i)
				QCoreApplication.processEvents()
			QMessageBox.information(self.flowchart.win, 'Import', '%d files imported' % n_imported)
		except MemoryError:
			QMessageBox.critical(self.flowchart.win, 'Import', 'Memory Error! Try using a large trunc or less files')

	def onReset(self):
		self.remover.reset()
		self.paras['rank'].setValue(0)

	def ctrlWidget(self):
		return self.paratree

	def process(self, sig, ref, sigMask, display=True):
		self.remover.setTrunc(self.paras['trunc'])
		if self.paras['updateLib'] and self.paras['rank'] <= self.paras['rankLimit']:
			self.remover.updateLibrary(ref)
			self.paras['rank'] = self.remover.rank
			self.paras['residual'] = self.remover.residual
		coef, ref = self.remover.reconstruct(np.ma.array(sig, mask=sigMask))
		ref = ref.reshape(512, 512)
		return {'ref1': ref}

	def saveState(self):
		state = super().saveState()
		state['paras'] = self.paras.saveState()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.paras.restoreState(state['paras'])

nodelist = [FringeRemoveNode]