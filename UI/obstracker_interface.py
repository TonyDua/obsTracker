# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect,QFileDialog
from qfluentwidgets import FluentIcon, setFont, InfoBarIcon,InfoBar,InfoBarPosition,InfoBarManager

from UI.Ui_ObsTracker import Ui_obstracker
#from Func.main import obstracker
import simpleobsws
import asyncio
from PyQt5.QtCore import Qt,QPoint
import random
@InfoBarManager.register('Custom')
class CustomInfoBarManager(InfoBarManager):
    """ Custom info bar manager """

    def _pos(self, infoBar: InfoBar, parentSize=None):
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        # the position of first info bar
        x = (parentSize.width() - infoBar.width()) // 2
        y = (parentSize.height() - infoBar.height()) // 2

        # get the position of current info bar
        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar):
        pos = self._pos(infoBar)
        return QPoint(pos.x(), pos.y() - 16)
    
class pyqtSignal:
    def __init__(self, *types, name: str = ...) -> None: ...

class ObsTrackerInterface(Ui_obstracker, QWidget):


    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.initUI()
        self.connectUI()
        self.ws = None
        self.isConnect = False
        self.InfoBar = None
        self.isRecord = False
        self.isAllwaysOnTop = False
        # 定义信号，信号有两个参数，两个参数的类型分别为str,str，信号名称为dataChanged
        # self.allwayOnTop = pyqtSignal(bool, name="allwaysOnTop")

    def initUI(self):
        # set the icon of button
        self.stillOnFrontBTN.setIcon(FluentIcon.PIN)
        self.connectBTN.setIcon(FluentIcon.CONNECT)
        self.settingBTN.setIcon(FluentIcon.SEND)
        self.recordBTN.setIcon(FluentIcon.CAMERA)
        self.takeSpinBox.setValue(1)
        self.takeSpinBox.setRange(1, 99)
        self.takeSpinBox.setPrefix("0")
        self.shotText.setText("SCTShot01")
        self.connectBTN.setToolTip("Connect to OBS")
        self.connectBTN.setChecked(False)
        self.settingBTN.setToolTip("Settings")
        self.settingBTN.setEnabled(True)
        
        # self.moreButton.setIcon(FluentIcon.MORE)
        # self.startFocusButton.setIcon(FluentIcon.POWER_BUTTON)
        # self.editButton.setIcon(FluentIcon.EDIT)
        # self.addTaskButton.setIcon(FluentIcon.ADD)
        # self.moreTaskButton.setIcon(FluentIcon.MORE)
        # self.taskIcon1.setIcon(InfoBarIcon.SUCCESS)
        # self.taskIcon2.setIcon(InfoBarIcon.WARNING)
        # self.taskIcon3.setIcon(InfoBarIcon.WARNING)
        # # add shadow effect to card
        # self.setShadowEffect(self.focusCard)
        # self.setShadowEffect(self.progressCard)
        # self.setShadowEffect(self.taskCard)
        pass
    # def setShadowEffect(self, card: QWidget):
    #     shadowEffect = QGraphicsDropShadowEffect(self)
    #     shadowEffect.setColor(QColor(0, 0, 0, 15))
    #     shadowEffect.setBlurRadius(10)
    #     shadowEffect.setOffset(0, 0)
    #     card.setGraphicsEffect(shadowEffect)

  
    def connectUI(self):
        self.connectBTN.clicked.connect(self.connectBTN_clicked)
        self.settingBTN.clicked.connect(self.settingBTN_clicked)
        self.recordBTN.clicked.connect(self.recordBTN_clicked)
       # self.stillOnFrontBTN.clicked.connect(self.stillOnFrontBTN_clicked)
        self.takeSpinBox.valueChanged.connect(self.takeSpinBox_valueChanged)
        self.SelectOutputDir.clicked.connect(self.selectOutputDirBTN_clicked)

        pass
    
    def connectBTN_clicked(self):
        # 实现按钮反转操作（类似于Flipflop）
        self.isConnect = not self.isConnect
        # 获取 连接信息

        host = self.hostText.text()
        port = self.portText.text()
        password = self.passwordText.text()

        print(self.isConnect,host,port,password)
        
        loop = None

        if  self.isConnect == True:
            loop = asyncio.get_event_loop()
            self.ws = simpleobsws.obsws(host,port,password,loop=loop)
            #ConnectionFailure = simpleobsws.ConnectionFailure()
            loop.run_until_complete(self.ws.connect())
            obsRecordingFolder = loop.run_until_complete(self.ws.call("GetRecordingFolder"))["rec-folder"]
            self.outputdirText.setText(obsRecordingFolder)
            print("Connected")
            self.createInfoInfoBar(InfoBarIcon.SUCCESS,"连接状态","Connected",3000)
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.ws.disconnect())

            print("Disconnected")
            self.createInfoInfoBar(InfoBarIcon.WARNING,"连接状态","Disconnected",3000)

           
    def createInfoInfoBar(self,baricon:InfoBarIcon =InfoBarIcon.INFORMATION,title:str = "title",content:str = "content",duration = 1000):
        self.InfoBar = InfoBar(
                                icon=baricon,
                                title=title,
                                content=content,
                                orient=Qt.Horizontal,   
                                isClosable=True,
                                position=InfoBarPosition.TOP_RIGHT,
                                duration=duration,
                                parent=self
                             )
        self.InfoBar.show()      
        

    def settingBTN_clicked(self):
        print("settingBTN_clicked")
        
    def recordBTN_clicked(self):
        self.isRecord = not self.isRecord
        print("recordBTN_clicked:recordBTN_State:" + str(self.isRecord))
        loop = None
        async def onRecodring(eventData):
            print("Now Recording")
            print('Now Recording :"{}".'.format(eventData['rec-timecode']))
        self.ws.register(onRecodring,"RecordingStarted")
        

        if self.isRecord and self.ws != None:
            loop = asyncio.get_event_loop()
            
            loop.run_until_complete(self.passSetting())
            loop.run_until_complete(self.ws.call("StartRecording"))
            

            self.createInfoInfoBar(InfoBarIcon.SUCCESS,"录制开始","StartRecordSueess",3000)
        elif self.isRecord == False and self.ws != None:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.ws.call("StopRecording"))
            #loop.run_until_complete(self.ws.register(self.getTimecode(),"GetRecordingStatus"))
            self.createInfoInfoBar(InfoBarIcon.SUCCESS,"录制结束","StopRecordSucess",3000)
            self.currentTake = self.takeSpinBox.value() + 1
            self.takeSpinBox.setValue(self.currentTake)
            if  self.takeSpinBox.value() <= 9:
                self.takeSpinBox.setPrefix("0")
            else:
                pass
        elif self.ws == None:
            print("请先连接！")
            self.createInfoInfoBar(InfoBarIcon.ERROR,"录制失败","请先连接OBS！！！",4000)

    async def passSetting(self):
            shot_name = self.shotText.text()
            take_name = self.takeSpinBox.text()
            output_name = shot_name + "_" + "take" + take_name

            output_folder = self.outputdirText.text()

            output_name_dict = {"filename-formatting":"None"}
            output_name_dict["filename-formatting"]= output_name
            print(output_name_dict)

            output_folder_dict = {"rec-folder":output_folder}
            print(output_folder_dict)
            
            if self.ws !=None:
                await self.ws.call("SetFilenameFormatting",output_name_dict)
                await self.ws.call("SetRecordingFolder",output_folder_dict)
            else:
                print("请先连接！")
                self.createInfoInfoBar(InfoBarIcon.ERROR,"录制状态","请先连接！！！",4000)


    # def stillOnFrontBTN_clicked(self):
    #     print("stillOnFrontBTN_clicked")
    #     self.isAllwaysOnTop = not self.isAllwaysOnTop
    
    def takeSpinBox_valueChanged(self):

        print("takeSpinBox_valueChanged")
        now_take = self.takeSpinBox.value()
        if now_take >= 10:
            self.takeSpinBox.setPrefix("")
        else:
            pass
    
    def selectOutputDirBTN_clicked(self):
        startdir = self.outputdirText.text()
        if startdir != None:
            
            outputfolder = QFileDialog.getExistingDirectory(
                            self,  # 父窗口对象
                            "选择存储路径",  # 标题
                            startdir # 起始目录
                            )
        else:
            outputfolder = QFileDialog.getExistingDirectory(
                            self,  # 父窗口对象
                            "选择存储路径",  # 标题
                            r"c:\\"  # 起始目录
                            )

        print(outputfolder)

        if outputfolder == "":
            pass
        else:
            self.outputdirText.setText(outputfolder)
        
