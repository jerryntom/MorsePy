import requests
import json
import pyttsx3 as tts
import re
from ctypes import windll
from platform import system
from sys import argv, exit
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QWidget, QDialog
from PySide6.QtCore import QEvent
from playsound import playsound
from pydub import AudioSegment
import multiprocessing
from os import path

appVersion = '250720221'
githubAccess = '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'
language = 'English'
textReadingSpeed = 100
languagePackFile = 'englishLanguagePack.txt'
languageData = {}
readEngine = tts.init()
AudioSegment.converter = 'ffmpeg.exe'
AudioSegment.ffmpeg = 'ffmpeg.exe'

with open('resources\\data\\settings.txt', 'r') as settingsFile:
    for line in settingsFile.readlines():
        setting, settingValue = line.split()
        
        if setting == 'language':
            language = settingValue
        else:
            textReadingSpeed = int(settingValue)

if language == 'Polski':
    languagePackFile = 'polishLanguagePack.txt'

with open('resources\\data\\{}'.format(languagePackFile), 'r', encoding='UTF-8') as languagePackFile:
    for line in languagePackFile.readlines():
        line = line.split(';')
        languageData[line[0]] = line[1].strip()
    
if system() == 'Windows':
    appId = u'jerryntom.python.morseapp.220720221'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
else:
    pass

def checkRegex(data, stringPattern):
    pattern = re.compile(r''+stringPattern, re.IGNORECASE)
    return pattern.match(data)


def readText(textToRead, speed):
    """
    Reading text mechanism 
    
    Args:
        data (string): text to read
    
    Returns:
        None
    """
    voices = readEngine.getProperty('voices')
    readEngine.setProperty('rate', speed)
    readEngine.setProperty('voice', voices[int(languageData['voice'])].id)
    readEngine.say(textToRead)
    readEngine.runAndWait()
    readEngine.stop()


def saveTextSound(textToRead, speed):
    """
    Saves text reading to sound file 'text.mp3'

    Args:
        textToRead (str): text to read and save to file
    
    Returns:
        None
    """
    pathToSave = 'output\\text.mp3'

    voices = readEngine.getProperty('voices')
    readEngine.setProperty('rate', speed)
    readEngine.setProperty('voice', voices[int(languageData['voice'])].id)

    if path.exists('output\\') == False:
        pathToSave = 'text.mp3'

    readEngine.save_to_file(textToRead, pathToSave)
    readEngine.runAndWait()
    readEngine.stop()


def readMorse(morseCode):
    """
    Interprets morse code as sounds and reads it 

    Args:
        morseCode (str): morse code data
    
    Returns:
        None
    """
    for char in morseCode:
        if char == '.':
            playsound('resources\\sounds\\morseCodeShort.mp3')
        elif char == '-':
            playsound('resources\\sounds\\morseCodeLong.mp3')


def saveMorseCode(morseCode):
    """
    Interprets morse code as sounds and saves it to file

    Args:
        morseCode (str): morse code data

    Returns:
        None
    """
    pathToSave = 'output\\morseSequence.mp3'
    morseCodeLong = AudioSegment.from_file('resources\\sounds\\morseCodeLong.mp3', format='mp3')
    morseCodeShort = AudioSegment.from_file('resources\\sounds\\morseCodeShort.mp3', format='mp3')
    morseCodeSequence = None

    if path.exists('output\\') == False:
        pathToSave = 'morseSequence.mp3'

    for char in morseCode:
        if morseCodeSequence is None and char != ' ':
            if char == '.':
                morseCodeSequence = morseCodeShort
            elif char == '-':
                morseCodeSequence = morseCodeLong
        elif morseCodeSequence is not None:
            if char == '.':
                morseCodeSequence += morseCodeShort
            elif char == '-':
                morseCodeSequence += morseCodeLong

    morseCodeSequence.export(pathToSave, format='mp3')


def createIssue(title, body):
    headers = {'Authorization': 'token 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'}
    url = 'https://api.github.com/repos/jerryntom/morsepy/issues'
    dataPack = [{'title': title, 'body': body}]

    for data in dataPack:
        requests.post(url,data=json.dumps(data),headers=headers)
    

class MenuWindow(QWidget):
    """
    Template for menu window

    Args:
        QWidget (class): base class for interface objects
    """
    def __init__(self):
        """
        Initiation of variables for MenuWindow class 
        """
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('resources\\images\\icon.png'))
        self.setFixedSize(600, 300)
        self.__background = QtWidgets.QLabel(self)
        self.__menuWindowLayout()

    def __menuWindowLayout(self):        
        self.__background.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.__background.setPixmap(QtGui.QPixmap('resources/images/background.png'))
        self.__background.setObjectName('background')
        self.__background.setMouseTracking(True)


class SettingsWindow(MenuWindow):
    """
    Settings window where you can set some parameters for the app

    Args:
        MenuWindow (class): base class for menu window
    """
    def __init__(self):
        """
        Initiation of variables for SettingsWindow class 
        """
        super().__init__()

        self.__sliderStyle = """
        QSlider::groove:horizontal {
            border: 1px solid;
            height: 10px;
            margin: 0px;
        }

        QSlider::handle:horizontal {
            background-color: black;
            border: 1px solid;
            height: 2px;
            width: 5px;
        }"""

        self.__languageChoiceStyle = """
        QComboBox {
            border: 1px solid #333333;
            border-radius: 3px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #797979, 
            stop:0.48 #696969, stop:0.52 #5e5e5e, stop:1 #4f4f4f);
            padding: 1px 23px 1px 3px;
            min-width: 6em;
            color: #ffffff;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
 
        QComboBox QAbstractItemView{
            background-color: #4f4f4f;
            color: #999999;
            selection-background-color: #999999;
            selection-color: #4f4f4f;
        }"""

        self.__textReadingSpeedLabel = QtWidgets.QLabel(self)
        self.__languageLabel = QtWidgets.QLabel(self)
        self.__languageChangeLabel = QtWidgets.QLabel(self)
        self.__languageChoice = QtWidgets.QComboBox(self)
        self.__textReadingSpeedSliderLabel = QtWidgets.QLabel(self)
        self.__settingsFont = QtGui.QFont()
        self.__languageChoiceFont = self.__languageChoice.font()
        self.__languageChangeFont = self.__languageChangeLabel.font()
        self.__sliderFont = self.__textReadingSpeedSliderLabel.font()
        self._textReadingSpeedSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        
    def settingsWindowLayout(self):
        """
        Creates layout for SettingsWindow class 

        Returns:
            None
        """ 
        self.__settings = {}
    
        with open('resources\\data\\settings.txt', 'r') as settingsFile:
            for line in settingsFile.readlines():
                line = line.split()
                self.__settings[line[0]] = line[1] 

        if int(self.__settings['textReadingSpeed']) < 100:
            self.__settings['textReadingSpeed'] == 100
 
        textReadingSpeed = int(self.__settings['textReadingSpeed'])

        self.setWindowTitle(languageData['settingsWindowTitle'])

        self.__settingsFont.setPointSize(30)
        self.__settingsFont.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)

        self.__textReadingSpeedLabel.setText(languageData['settingsSpeedLabel'])
        self.__textReadingSpeedLabel.setGeometry(QtCore.QRect(50, 40, 50, 50))
        self.__textReadingSpeedLabel.setFont(self.__settingsFont)
        self.__textReadingSpeedLabel.adjustSize()

        self.__languageLabel.setText(languageData['settingsLanguageLabel'])
        self.__languageLabel.setGeometry(QtCore.QRect(50, 100, 50, 50))
        self.__languageLabel.setFont(self.__settingsFont)
        self.__languageLabel.adjustSize()
        
        self.__languageChoiceFont = self.__languageChoice.font()
        self.__languageChoiceFont.setBold(True)
        self.__languageChoiceFont.setPointSize(25)

        self.__languageChangeFont.setPointSize(20)
        self.__languageChangeFont.setBold(True)

        self.__languageChangeLabel.setText(languageData['languageChangeInfo'])
        self.__languageChangeLabel.setGeometry(QtCore.QRect(50, 170, 50, 50))
        self.__languageChangeLabel.setFont(self.__languageChangeFont)
        self.__languageChangeLabel.adjustSize()
        self.__languageChangeLabel.setHidden(True)
        
        self.__languageChoiceFont.setBold(True)
        self.__languageChoiceFont.setPointSize(25)

        if self.__languageChoice.count() != 2:
            self.__languageChoice.setGeometry(QtCore.QRect(250, 105, 50, 50))
            self.__languageChoice.setFont(self.__languageChoiceFont)
            self.__languageChoice.addItems(['English', 'Polski'])
            self.__languageChoice.setStyleSheet(self.__languageChoiceStyle)
            self.__languageChoice.adjustSize()
            self.__languageChoice.currentTextChanged.connect(self.__changeLanguage)

        if self.__languageChoice is not None:
            with open('resources\\data\\settings.txt', 'r') as settingsFile:
                for line in settingsFile.readlines():
                    setting, settingValue = line.split()

                    if setting == 'language':
                        languageIndex = self.__languageChoice.findText(settingValue)

            self.__languageChoice.setCurrentIndex(languageIndex)

        self._textReadingSpeedSlider.setGeometry(QtCore.QRect(400, 60, 100, 25))
        self._textReadingSpeedSlider.setMinimum(100)
        self._textReadingSpeedSlider.setMaximum(300)
        self._textReadingSpeedSlider.setSingleStep(1)
        self._textReadingSpeedSlider.setValue(textReadingSpeed)
        self._textReadingSpeedSlider.valueChanged.connect(self.__changeTextReadingSpeed)
        self._textReadingSpeedSlider.setStyleSheet(self.__sliderStyle)

        self.__sliderFont.setBold(True)
        self.__sliderFont.setPointSize(15)

        self.__textReadingSpeedSliderLabel.setText(str(self._textReadingSpeedSlider.value()))
        self.__textReadingSpeedSliderLabel.setGeometry(QtCore.QRect(430, 40, 0, 0))
        self.__textReadingSpeedSliderLabel.setFont(self.__sliderFont)
        self.__textReadingSpeedSliderLabel.adjustSize()

        if languageData['settingsLanguageLabel'] == 'Język':
            self._textReadingSpeedSlider.move(380, 60)
            self.__textReadingSpeedSliderLabel.move(410, 40)
            self.__languageChoice.move(160, 105)
        elif languageData['settingsLanguageLabel'] == 'Language':
            self._textReadingSpeedSlider.move(400, 60)
            self.__textReadingSpeedSliderLabel.move(430, 40)
            self.__languageChoice.move(230, 105)

    def __changeTextReadingSpeed(self):
        """
        Updates text reading speed basing on textReadingSpeedSlider

        Returns:
            None
        """
        self.__textReadingSpeed = self._textReadingSpeedSlider.value()
        self.__textReadingSpeedSliderLabel.setText(str(self.__textReadingSpeed))
        self.__updateSettings()

    def __changeLanguage(self):
        """
        Updates app language basing on languageChoice 

        Returns:
            None
        """
        language = self.__languageChoice.currentText()

        if language != self.__settings['language']:
            self.__languageChangeLabel.setHidden(False)

        self.__updateSettings()

    def __updateSettings(self):
        """
        Updates settings.txt file basing on values set in settings window

        Returns:
            None
        """
        if self._textReadingSpeedSlider.value() != 0:
            with open('resources\\data\\settings.txt', 'w') as settingsFile:
                settingsFile.write('textReadingSpeed' + ' ' + str(self._textReadingSpeedSlider.value()))
                settingsFile.write('\nlanguage' + ' ' + str(self.__languageChoice.currentText()))


class AboutWindow(MenuWindow):
    """
    Information about project and author

    Args:
        MenuWindow (class): base class for menu window
    """
    def __init__(self):
        """
        Initiation of variables for AboutWindow class 
        """
        super().__init__()
        self.setWindowTitle(languageData['aboutWindowTitle'])
        self.__aboutWindowFont = QtGui.QFont()
        self.__contributionLabel = QtWidgets.QLabel(self)
        self.__contributionImageLabel = QtWidgets.QLabel(self)
        self.__repositoryInfoLabel = QtWidgets.QLabel(self)
        self.__repositoryLinkLabel = QtWidgets.QLabel(self)
        self.__creatorInfoLabel = QtWidgets.QLabel(self)
        self.__creatorInfoLinkLabel = QtWidgets.QLabel(self)

    def aboutWindowLayout(self):
        self.__aboutWindowFont.setPointSize(20)

        self.__contributionLabel.setGeometry(50, 30, 50, 50)
        self.__contributionLabel.setText('MorsePy {}\n{}'.format(appVersion, languageData['contributionLabel']))
        self.__contributionLabel.setFont(self.__aboutWindowFont)
        self.__contributionLabel.adjustSize()

        self.__contributionImageLabel.setGeometry(80, 70, 256, 256)
        self.__contributionImageLabel.setPixmap(QtGui.QPixmap('resources\\images\\contribution.png').scaled(180, 180, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation))

        self.__aboutWindowFont.setPointSize(15)

        self.__repositoryInfoLabel.setGeometry(300, 150, 50, 50)
        self.__repositoryInfoLabel.setText(languageData['repositoryInfoLabel'])
        self.__repositoryInfoLabel.setFont(self.__aboutWindowFont)
        self.__repositoryInfoLabel.adjustSize()

        self.__repositoryLinkLabel.setGeometry(300, 180, 50, 50)
        self.__repositoryLinkLabel.setText('<a href="https://github.com/jerryntom/morsepy">\
            morsepy {}</a>'.format(languageData['repositoryLinkLabel']))
        self.__repositoryLinkLabel.linkActivated.connect(self.__openURL)
        self.__repositoryLinkLabel.setFont(self.__aboutWindowFont)
        self.__repositoryLinkLabel.adjustSize()

        self.__creatorInfoLabel.setGeometry(300, 210, 50, 50)
        self.__creatorInfoLabel.setText(languageData['creatorInfoLabel'])
        self.__creatorInfoLabel.setFont(self.__aboutWindowFont)
        self.__creatorInfoLabel.adjustSize()

        self.__creatorInfoLinkLabel.setGeometry(300, 240, 50, 50)
        self.__creatorInfoLinkLabel.setText('<a href="https://github.com/jerryntom">\
            jerryntom {}</a>'.format(languageData['creatorInfoLinkLabel']))
        self.__creatorInfoLinkLabel.linkActivated.connect(self.__openURL)
        self.__creatorInfoLinkLabel.setFont(self.__aboutWindowFont)
        self.__creatorInfoLinkLabel.adjustSize()

    def __openURL(self, URL):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(URL))


class ReportWindow(MenuWindow):
    """
    Window for reporting bugs and features concerning the app

    Args:
        MenuWindow (class): base class for menu window
    """
    def __init__(self):
        """
        Initiation of variables for ReportWindow class 
        """
        super().__init__()
        self.setWindowTitle(languageData['reportWindowTitle'])


class InfoWindow(QDialog):
    """
    Window for showing info about processes happening in the background

    Args:
        QDialog (class): base class for info window
    """
    def __init__(self, infoTitle, infoMessage, parent=None):
        """
        Initiation of variables for InfoWindow class

        Args:
            infoTitle (str): window title
            infoMessage (str): info message
        """
        super().__init__(parent)

        self.setWindowTitle(infoTitle)
        self.setWindowIcon(QtGui.QIcon('resources\\images\\icon.png'))
        self.__infoButton = QtWidgets.QDialogButtonBox.StandardButton.Ok
        self.__buttonBox = QtWidgets.QDialogButtonBox(self.__infoButton)
        self.__verticalBoxLayout = QtWidgets.QVBoxLayout()
        self.__message = QtWidgets.QLabel(infoMessage)

    def __infoWindowLayout(self):
        """
        Creates layout for InfoWindow class 

        Returns:
            None
        """ 
        self.__buttonBox.accepted.connect(self.accept)
        self.__verticalBoxLayout.addWidget(self.__message)
        self.__verticalBoxLayout.addWidget(self.__buttonBox)
        self.setLayout(self.__verticalBoxLayout)

    def showInfoWindow(self):
        """
        Shows info window and closes it after 1 second

        Returns:
            None
        """
        self.__infoWindowLayout()
        self.show()
        self.activateWindow()
        QtCore.QTimer.singleShot(1000, self.__closeInfoWindow)

    def __closeInfoWindow(self):
        """
        Closes window after procedures in showInfoWindow method

        Returns:
            None
        """
        self.close()

class ErrorWindow(QDialog):
    """
    Window for showing info about occuring errors

    Args:
        QDialog (class): base class for info window
    """
    def __init__(self, errorTitle, errorMessage, parent=None):
        """
        Initiation of variables for InfoWindow class

        Args:
            errorTitle (str): window title
            errorMessage (str): error message
        """
        super().__init__(parent)

        self.setWindowTitle(errorTitle)
        self.setWindowIcon(QtGui.QIcon('resources\\images\\icon.png'))

        self.__infoButton = QtWidgets.QDialogButtonBox.StandardButton.Ok
        self.__buttonBox = QtWidgets.QDialogButtonBox(self.__infoButton)
        self.__verticalBoxLayout = QtWidgets.QVBoxLayout()
        self.__message = QtWidgets.QLabel(errorMessage)

    def __errorWindowLayout(self):
        """
        Creates layout for ErrorWindow class 

        Returns:
            None
        """ 
        self.__buttonBox.accepted.connect(self.accept)
        self.__verticalBoxLayout.addWidget(self.__message)
        self.__verticalBoxLayout.addWidget(self.__buttonBox)
        self.setLayout(self.__verticalBoxLayout)

    def showErrorWindow(self):
        """
        Shows error window and closes the app when ok button is clicked

        Returns:
            None
        """
        self.__errorWindowLayout()
        self.show()
        self.activateWindow()
        self.exec()
        exit(-1)

class MorseApp(QMainWindow):
    """
    Main window/user interface of the app

    Args:
        QMainWindow (class): main app window
    """
    def __init__(self):
        """
        Initiation of variables for MorseApp class 
        """
        super().__init__()

        self.chars = dict()
        self.morseCode = dict()
        self.__validateAppDependencies()

        with open('resources\\data\\morseValues.txt', 'r', encoding='UTF-8') as file:
            for line in file.readlines():
                char, value = line.split()

                self.chars[char] = value
                value = value.replace('•', '.')
                char = char.lower()
                self.morseCode[value] = char

        self.__inputBoxStyle = """
        color: black;
        background-color: white;
        border: 2px solid black;
        border-radius: 18px;
        padding: 10px;"""

        self.__changeTranslationButtonStyle = """
        border: 2px solid black;
        border-radius: 18px;
        color: black;"""

        self.__sideButtonStyle = """
        QPushButton {
            background-color: transparent;
            border-radius: 22px;
        }
            
        QToolTip {
            color: #ffffff; 
            background-color: #000000;
            border: 0px;
        }"""

        self.__scrollBarStyle = """
        QScrollBar:vertical {
            border: none;
            background: none;
            height: 0;
            margin: 0 0 0 0;
        }

        QScrollBar::handle:vertical  {
            background: none;
            min-width: 0;
        }

        QScrollBar::add-line:vertical  {
            background: none;
            width: 0;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }"""

        self.__inputBoxData = ''
        self.__mainFont = QtGui.QFont()
        self.__mainWidget = QtWidgets.QWidget(MainWindow)
        self.__background = QtWidgets.QLabel(self.__mainWidget)
        self.__changeTranslationButton = QtWidgets.QPushButton(self.__mainWidget)
        self.__textInputBox = self.__inputBoxHandler(60, 40, 490, 180, 'field1')
        self.__textInputBox.installEventFilter(self)
        self.__morseInputBox = self.__inputBoxHandler(60, 370, 490, 180, 'field2')
        self.__morseInputBox.installEventFilter(self)
        self.__textReadButton = self.__sideButtonHandler(552, 62, 45, 45, 'readButton.png', 'read text')
        self.__textReadButton.installEventFilter(self)
        self.__stopTextReadButton = self.__sideButtonHandler(552, 109, 45, 45, 'stopReadButton.png', 'stop text reading')
        self.__stopTextReadButton.installEventFilter(self)
        self.__saveTextToSoundButton = self.__sideButtonHandler(552, 156, 45, 45, 'saveSoundButton.png', 'save text to sound')
        self.__saveTextToSoundButton.installEventFilter(self)
        self.__readMorseButton = self.__sideButtonHandler(552, 393, 45, 45, 'readButton.png', 'read morse')
        self.__readMorseButton.installEventFilter(self)
        self.__stopReadMorseButton = self.__sideButtonHandler(552, 440, 45, 45, 'stopReadButton.png', 'stop reading')
        self.__stopReadMorseButton.installEventFilter(self)
        self.__saveMorseToSoundButton = self.__sideButtonHandler(552, 487, 45, 45, 'saveSoundButton.png', 'save to sound')
        self.__saveMorseToSoundButton.installEventFilter(self)
        self.__changeTranslationButton.installEventFilter(self)
        self.__background.installEventFilter(self)
        self.__textReadButton.installEventFilter(self)
        self.__readMorseButton.installEventFilter(self)
        self.__stopTextReadButton.installEventFilter(self)
        self.__stopReadMorseButton.installEventFilter(self)
        self.__saveTextToSoundButton.installEventFilter(self)
        self.__saveMorseToSoundButton.installEventFilter(self)
        self.__morsePatternCheck = ''
        self.__topMenu = QMenuBar()
        self.__settingsWindow = None
        self.__aboutWindow = None
        self.__reportWindow = None
        self._language = 'Polski'

    def __validateAppDependencies(self):
        """
        Checks if every file is one its place and exits the app if not

        Returns:
            None
        """
        filePaths = {'ffmpeg.exe': 1, 'ffprobe.exe': 1, 
        'resources\\data\\morseValues.txt': 1, 'resources\\images\\background.png': 1,
        'resources\\images\\readButton.png': 1, 'resources\\images\\saveSoundButton.png': 1, 
        'resources\\images\\stopReadButton.png': 1, 'resources\\sounds\\morseCodeLong.mp3': 1, 
        'resources\\sounds\\morseCodeShort.mp3': 1, 'resources\\images\\icon.png': 1,
        'resources\\data\\settings.txt': 1, 'resources\\data\englishLanguagePack.txt': 1,
        'resources\\data\polishLanguagePack.txt': 1}

        missingFilesBegin = 'Some files are missing\n\n'
        missingFileFindInfo1 = '\nYou can find them in project repository'
        missingFileFindInfo2 = '\nhttps//github.com/jerryntom/morsepy'
        missingFilesErrorTitle = 'Missing files error'

        if language == 'Polski':
            missingFilesBegin = 'Brakuje pewnych plików\n\n'
            missingFileFindInfo1 = '\nMożesz je znaleźć w repozytorium projektu'
            missingFileFindInfo2 = '\nhttps//github.com/jerryntom/morsepy'
            missingFilesErrorTitle = 'Błąd - nie znaleziono zasobów'

        missingFiles = missingFilesBegin
    
        for key in filePaths.keys():
            if path.exists(key) == False:
                filePaths[key] = 0
                missingFiles += key
                missingFiles += "\n"
        
        if missingFiles != missingFilesBegin:
            missingFiles += missingFileFindInfo1
            missingFiles += missingFileFindInfo2
            errorWindow = ErrorWindow(missingFilesErrorTitle, missingFiles)
            errorWindow.showErrorWindow()

    def layout(self, mainWindow):
        """
        Layout and object setup 

        Args:
            mainWindow (object): main window of the app  
        """
        mainWindow.setObjectName('MainWindow')
        mainWindow.setEnabled(True)
        mainWindow.setFixedSize(600, 600)

        self.__mainWidget.setObjectName('centralwidget')

        self.__background.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.__background.setPixmap(QtGui.QPixmap('resources/images/background.png'))
        self.__background.setObjectName('background')
        self.__background.setMouseTracking(True)

        self.__topMenu.setStyleSheet('background: url(resources/images/background.png);')
        self.__topMenu.addAction(languageData['settingsMenuBar'], lambda: self.__showSettingsWindow())
        self.__topMenu.addAction(languageData['aboutMenuBar'], lambda: self.__showAboutWindow())
        self.__topMenu.addAction(languageData['reportMenuBar'], lambda: self.__showReportWindow())

        mainWindow.setMenuBar(self.__topMenu)

        self.__mainFont.setPointSize(25)
        self.__mainFont.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)

        self.__changeTranslationButton.setGeometry(QtCore.QRect(210, 260, 200, 70))
        self.__changeTranslationButton.setFont(self.__mainFont)
        self.__changeTranslationButton.setStyleSheet(self.__changeTranslationButtonStyle)
        self.__changeTranslationButton.setFlat(False)
        self.__changeTranslationButton.setObjectName('changeTranslationType')
        self.__changeTranslationButton.setText(languageData['buttonModeChangeText'])
        self.__changeTranslationButton.clicked[bool].connect(self.__changeTranslationType)

        self.__mainFont.setPointSize(20)

        self.__textInputBox.setPlaceholderText(languageData['textInputPlaceholder'])
        self.__morseInputBox.setReadOnly(True)
        MainWindow.setCentralWidget(self.__mainWidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def __inputBoxHandler(self, positionX, positionY, width, height, name):
        """
        Template for main input boxes 

        Args:
            positionX (int): x cordinate of object position
            positionY (int): y -//- 
            width (int): width of the object
            height (int): height -//-
            name (string): name of the object

        Returns:
            self.inputBox (object): ready to use input box
        """
        self.__mainFont.setPointSize(20)
        inputBox = QtWidgets.QTextEdit(self.__mainWidget)
        inputBox.setGeometry(QtCore.QRect(positionX, positionY, width, height))
        inputBox.setFont(self.__mainFont)
        inputBox.setStyleSheet(self.__inputBoxStyle)
        inputBox.setObjectName(name)
        inputBox.verticalScrollBar().setStyleSheet(self.__scrollBarStyle)
        inputBox.horizontalScrollBar().setEnabled(False)
        inputBox.setAcceptRichText(False)
        
        return inputBox

    def __sideButtonHandler(self, positionX, positionY, width, height, image, toolTip):
        """
        Template for side buttons 

        Args:
            positionX (int): x cordinate of object position
            positionY (int): y -//- 
            width (int): width of the object
            height (int): height -//-
            image (string): name of the file with button image 

        Returns:
            self.sideButton (object): ready to use side button
        """
        sideButton = QtWidgets.QPushButton(self.__mainWidget)
        sideButton.setGeometry(positionX, positionY, width, height)
        sideButton.setStyleSheet(self.__sideButtonStyle)
        sideButton.setIcon(QtGui.QIcon('resources\\images\\{}'.format(image)))
        sideButton.setIconSize(QtCore.QSize(25, 25))
        sideButton.setToolTip(toolTip)

        return sideButton

    def eventFilter(self, obj, event):
        """
        Handler of the events happening within the app

        Args:
            obj (object): object e.g. input box 
            event (type): type of event occuring

        Returns:
            reference to eventFilter, method of QEvent class
        """
        if obj is self.__textInputBox:
            if event.type() == QEvent.Type.KeyRelease:
                self.__polishToMorse()
        elif obj is self.__changeTranslationButton:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.__changeTranslationButtonStyle = """
                border: 2px solid grey;
                border-radius: 20px;
                color: white;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.__changeTranslationButton.setStyleSheet(self.__changeTranslationButtonStyle)
            elif event.type() == QEvent.Type.HoverEnter:
                self.__changeTranslationButtonStyle = """
                border: 2px solid grey;
                border-radius: 20px;
                color: black;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.__changeTranslationButton.setStyleSheet(self.__changeTranslationButtonStyle)
            elif event.type() == QEvent.Type.HoverLeave:
                self.__changeTranslationButtonStyle = """
                border: 2px solid black;
                border-radius: 18px;
                color: black;"""
                self.__changeTranslationButton.setStyleSheet(self.__changeTranslationButtonStyle)
        elif obj is self.__morseInputBox:
            if event.type() == QEvent.Type.KeyRelease:
                self.__morseToPolish()
        elif obj is self.__textReadButton and self.__textInputBox.toPlainText() != '' \
        and self.__textInputBox.toPlainText() != languageData['morseCodeTranslateError'] + ' ':
            self.textData = self.__textInputBox.toPlainText()
            self.textReadingSpeed = setting

            if self.__settingsWindow is not None:
                self.textReadingSpeed = self.__settingsWindow._textReadingSpeedSlider.value()
            
            if event.type() == QEvent.Type.MouseButtonPress and self.__isProcessAlive('reading text') == False:
                self.readingTextProcess = multiprocessing.Process(target=readText, args=(self.textData, 
                self.textReadingSpeed,), daemon=True, name='reading text')
                self.readingTextProcess.start()
            elif event.type() == QEvent.Type.MouseButtonPress and self.__isProcessAlive('reading text') == True:
                self.readingTextProcess.terminate()
                self.readingTextProcess = multiprocessing.Process(target=readText, args=(self.textData, 
                self.textReadingSpeed,), daemon=True, name='reading text')
                self.readingTextProcess.start()
        elif obj is self.__readMorseButton and self.__morseInputBox.toPlainText() != '' \
        and self.__morseInputBox.toPlainText() != languageData['textTranslateError']:
            self.morseCodeData = self.__morseInputBox.toPlainText()

            if event.type() == QEvent.Type.MouseButtonPress and self.__isProcessAlive('reading morse') == False:
                self.readingMorseProcess = multiprocessing.Process(target=readMorse, args=(self.morseCodeData,), 
                daemon=True, name='reading morse')
                self.readingMorseProcess.start()
            elif event.type() == QEvent.Type.MouseButtonPress and self.__isProcessAlive('reading morse') == True:
                self.readingMorseProcess.terminate()
                self.readingMorseProcess = multiprocessing.Process(target=readMorse, args=(self.morseCodeData,), 
                daemon=True, name='reading morse')
                self.readingMorseProcess.start()
        elif obj is self.__stopTextReadButton and self.__isProcessAlive('reading text') == True:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.readingTextProcess.terminate()
        elif obj is self.__stopReadMorseButton and self.__isProcessAlive('reading morse') == True:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.readingMorseProcess.terminate()
        elif obj is self.__saveTextToSoundButton and self.__textInputBox.toPlainText() != \
        languageData['morseCodeTranslateError'] + ' ':
            self.textData = self.__textInputBox.toPlainText()
            self.textReadingSpeed = textReadingSpeed

            if self.__settingsWindow is not None:
                self.textReadingSpeed = self.__settingsWindow._textReadingSpeedSlider.value()

            if event.type() == QEvent.Type.MouseButtonPress and self.textData != '':
                self.saveTextToSoundProcess = multiprocessing.Process(target=saveTextSound, args=(self.textData, 
                self.textReadingSpeed,), daemon=True, name='saving text to sound')
                self.infoWindow = InfoWindow(languageData['textReadingProcessInfoTitle'], 
                languageData['textReadingProcessInfoMessage'])
                self.infoWindow.showInfoWindow()
                self.saveTextToSoundProcess.start()
        elif obj is self.__saveMorseToSoundButton and self.__morseInputBox.toPlainText() != languageData['textTranslateError']:
            if event.type() == QEvent.Type.MouseButtonPress and self.__morseInputBox.toPlainText() != '':
                self.morseCodeData = self.__morseInputBox.toPlainText()
                self.saveMorseCodeToSoundProcess = multiprocessing.Process(target=saveMorseCode, 
                args=(self.morseCodeData,), daemon=True, name='saving morse code to sound')
                self.infoWindow = InfoWindow(languageData['morseReadingProcessInfoTitle'], 
                languageData['morseReadingProcessInfoMessage'])
                self.infoWindow.showInfoWindow()
                self.saveMorseCodeToSoundProcess.start()

        return super().eventFilter(obj, event)

    def __showSettingsWindow(self):
        """
        Settings window position functioning

        Returns:
            None
        """
        if self.__settingsWindow is None:
            self.__settingsWindow = SettingsWindow()
        
        self.__settingsWindow.show()
        self.__settingsWindow.settingsWindowLayout()
        self.__settingsWindow.activateWindow()

    def __showAboutWindow(self):
        """
        About window position functioning
        
        Returns:
            None
        """
        if self.__aboutWindow is None:
            self.__aboutWindow = AboutWindow()

        self.__aboutWindow.show()
        self.__aboutWindow.aboutWindowLayout()
        self.__aboutWindow.activateWindow()

    def __showReportWindow(self):
        """
        Report window position functioning
        
        Returns:
            None
        """
        if self.__reportWindow is None:
            self.__reportWindow = ReportWindow()

        self.__reportWindow.show()
        self.__reportWindow.activateWindow()

    def __changeTranslationType(self):
        """
        Handler of translation change, switches between main input boxes

        Returns:
            None
        """
        if self.__textInputBox.placeholderText() != '':
            self.__textInputBox.setPlaceholderText('')
            self.__textInputBox.setReadOnly(True)

            self.__morseInputBox.setReadOnly(False)
            self.__morseInputBox.setPlaceholderText(languageData['morseInputPlaceholder'])
        else:
            self.__textInputBox.setPlaceholderText(languageData['textInputPlaceholder'])
            self.__textInputBox.setReadOnly(False)

            self.__morseInputBox.setPlaceholderText('')
            self.__morseInputBox.setReadOnly(True)

        self.__morseInputBox.setText('')
        self.__textInputBox.setText('')

    def __polishToMorse(self):
        """
        Polish to morse translation mechanism 

        Returns:
            None
        """
        textTranslation = ''
        self.__inputBoxData = self.__textInputBox.toPlainText().upper()

        for char in self.__inputBoxData:
            if char == ' ':
                textTranslation += ' | '
            elif char not in self.chars.keys():
                textTranslation = languageData['textTranslateError']
                break
            elif char != ' ':
                textTranslation += self.chars[char] + ' '

        self.__textInputBox.verticalScrollBar().setValue(self.__textInputBox.verticalScrollBar().maximum())
        self.__morseInputBox.setText(textTranslation)
        
    def __morseToPolish(self):
        """
        Morse to polish translation mechanism

        Returns:
            None
        """
        morseTransalation = ''
        words = self.__morseInputBox.toPlainText().split(' | ')
        wordsChars = []
        self.__morsePatternCheck = True
        self.__textInputBox.setText('')

        if self.__morseInputBox.toPlainText() != '':
            for i in range(0, len(words)):
                words[i] = words[i].strip()
                wordsChars.append(words[i].split(' '))

            for word in wordsChars:
                if not self.__morsePatternCheck:
                    break
                else:
                    for char in word:
                        self.__morsePatternCheck = checkRegex(char, '^[.-]{1,7}$')

                        if self.__morsePatternCheck and char in self.morseCode.keys():
                            morseTransalation += self.morseCode[char]
                        elif not self.__morsePatternCheck or char not in self.morseCode.keys():
                            morseTransalation = languageData['morseCodeTranslateError']
                            break

                    morseTransalation += ' '

            self.__textInputBox.setText(morseTransalation)
            self.__morseInputBox.verticalScrollBar().setValue(self.__morseInputBox.verticalScrollBar().maximum())

    def __isProcessAlive(self, processName):
        """
        Checks is certain process is alive

        Args:
            processName (str): process name

        Returns:
            boolean: True if process alive and False if not
        """
        for process in multiprocessing.active_children():
            if process.name == processName:
                return True

        return False 


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowTitle('MorsePy')
    MainWindow.setWindowIcon(QtGui.QIcon('resources\\images\\icon.png'))
    userInterface = MorseApp()
    userInterface.layout(MainWindow)
    MainWindow.show()
    exit(app.exec())
