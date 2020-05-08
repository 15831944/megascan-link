
# Designer imports
import sd
import os
import time
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
import configparser
from queue import Queue 

import megascan_link
from megascan_link import sockets,config,utilities,dialogs,ui
from megascan_link import resourceImporter as resImporter
from megascan_link import icon as mIcon

import importlib
importlib.reload(megascan_link)
importlib.reload(sockets)
importlib.reload(utilities)
importlib.reload(resImporter)
importlib.reload(config)
importlib.reload(dialogs)
importlib.reload(ui)
importlib.reload(mIcon)
import ptvsd

class Data(object):
    socketThread = None
    toolbarAction = None
    toolbar = None
    settingDialog = None

def openSettings():
    uiMgr = utilities.getUiManager()  
    mainWindow = uiMgr.getMainWindow()
    Data.settingDialog = dialogs.SettingsDialog(Data.socketThread,parent=mainWindow)
    Data.settingDialog.show()

# Plugin entry points.
#
def initializeSDPlugin():
	# Debug Studd
    # ptvsd.enable_attach()
    # ptvsd.wait_for_attach()
    # ptvsd.break_into_debugger()

    # Set up initial config proprieties
    conf = config.ConfigSettings()
    initConfig = configparser.ConfigParser()
    initConfig["Socket"] = {"port": 24981,
                            "timeout": 5}
    conf.setUpInitialConfig(initConfig)

    uiMgr = utilities.getUiManager()  
    # Get the main window to set the thread parent of
    mainWindow = uiMgr.getMainWindow()
    toolbars = mainWindow.findChildren(QtWidgets.QToolBar)

    for toolbar in toolbars:
        if mainWindow.toolBarArea(toolbar) == Qt.ToolBarArea.TopToolBarArea:
            Data.toolbar = toolbar
            icon = QtGui.QIcon(mIcon.MegascanIcon.path)
            Data.toolbarAction = toolbar.addAction(icon, None)
            Data.toolbar = Data.toolbarAction.parentWidget()
            break
    Data.toolbarAction.triggered.connect(openSettings)

    Data.socketThread = sockets.SocketThread(parent=mainWindow)
    importer = resImporter.ResourceImporter()
    receiver = sockets.SocketReceiver(parent=mainWindow,importer=importer)
    print(Data.socketThread,receiver)
    Data.socketThread.onDataReceived.connect(receiver.onReceivedData, Qt.QueuedConnection)
    Data.socketThread.start()


def uninitializeSDPlugin():
    #stopping socket
    Data.socketThread.close()
    Data.toolbar.removeAction(Data.toolbarAction)
