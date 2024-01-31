import sys
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

appVersion = '300720222'
language = 'English'
textReadingSpeed = 100
languagePackFile = 'englishLanguagePack.txt'
languageData = {}
readEngine = tts.init()
AudioSegment.converter = 'ffmpeg.exe'
AudioSegment.ffmpeg = 'ffmpeg.exe'


def open_url(url):
    """
    Opens URL in web browser

    Args:
        url (str): website link

    Returns:
        None
    """
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


def validateAppDependencies():
    """
    Checks if every file is one its place and exits the app if not

    Returns:
        None
    """
    filePaths = {resource_path('ffmpeg.exe'): 1, resource_path('ffprobe.exe'): 1,
                 resource_path('resources\\data\\morseValues.txt'): 1,
                 resource_path('resources\\images\\background.png'): 1,
                 resource_path('resources\\images\\readButton.png'): 1,
                 resource_path('resources\\images\\saveSoundButton.png'): 1,
                 resource_path('resources\\images\\stopReadButton.png'): 1,
                 resource_path('resources\\sounds\\morseCodeLong.mp3'): 1,
                 resource_path('resources\\sounds\\morseCodeShort.mp3'): 1,
                 resource_path('resources\\images\\icon.png'): 1,
                 resource_path('resources\\data\\settings.txt'): 1,
                 resource_path('resources\\data\\englishLanguagePack.txt'): 1,
                 resource_path('resources\\data\\polishLanguagePack.txt'): 1}

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
        if not path.exists(key):
            filePaths[key] = 0
            missingFiles += key
            missingFiles += "\n"

    if missingFiles != missingFilesBegin:
        missingFiles += missingFileFindInfo1
        missingFiles += missingFileFindInfo2
        errorWindow = ErrorWindow(missingFilesErrorTitle, missingFiles)
        errorWindow.show_error_window()


def is_process_alive(process_name):
    """
    Checks is certain process is alive

    Args:
        process_name (str): process name

    Returns:
        boolean: True if process alive and False if not
    """
    for process in multiprocessing.active_children():
        if process.name == process_name:
            return True

    return False


def resource_path(relative_path):
    """
    Gets correct path to resource

    Args:
        relative_path (str): expected path
    """
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = path.abspath(".")

    return path.join(basePath, relative_path)


inputBoxStyle = """
    color: black;
    background-color: white;
    border: 2px solid black;
    border-radius: 18px;
    padding: 10px;"""

scrollBarStyle = """
    QScrollBar:vertical {
        border: none;
        background: none;
        height: 0;
        margin: 0 0 0 0;
    }
    
    QScrollBar::handle:vertical {
        background: none;
        min-width: 0;
    }
    
    QScrollBar::add-line:vertical {
        background: none;
        width: 0;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }"""

mainButtonStyle = """
        border: 2px solid black;
        border-radius: 18px;
        color: black;"""

with open(resource_path('resources\\data\\settings.txt'), 'r') as settingsFile:
    for setting_line in settingsFile.readlines():
        setting, settingValue = setting_line.split()

        if setting == 'language':
            language = settingValue
        else:
            textReadingSpeed = int(settingValue)

if language == 'Polski':
    languagePackFile = 'polishLanguagePack.txt'

with open(resource_path('resources\\data\\{}'.format(languagePackFile)), 'r', encoding='UTF-8') as languagePackFile:
    for line in languagePackFile.readlines():
        line = line.split(';')
        languageData[line[0]] = line[1].strip()

if system() == 'Windows':
    appId = u'jerryntom.python.morseapp.{}'.format(appVersion)
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
else:
    pass


def check_regex(data, string_pattern):
    """
    Checks if text matches the pattern

    Args:
        data (str): text data
        string_pattern (str): pattern

    Returns:
        bool: True whether text matches the pattern
    """
    pattern = re.compile(r'' + string_pattern, re.IGNORECASE)
    return pattern.match(data)


def read_text(text_to_read, speed):
    """
    Reading text mechanism 
    
    Args:
        speed: speed of reading
        text_to_read (string): text to read
    
    Returns:
        None
    """
    voices = readEngine.getProperty('voices')
    readEngine.setProperty('rate', speed)
    readEngine.setProperty('voice', voices[int(languageData['voice'])].id)
    print(languageData['voice'])
    readEngine.say(text_to_read)
    readEngine.runAndWait()
    readEngine.stop()


def save_text_sound(text_to_read, speed):
    """
    Saves text reading to sound file 'text.mp3'

    Args:
        speed: speed of reading
        text_to_read (str): text to read and save to file
    
    Returns:
        None
    """
    pathToSave = 'output\\text.mp3'

    voices = readEngine.getProperty('voices')
    readEngine.setProperty('rate', speed)
    readEngine.setProperty('voice', voices[int(languageData['voice'])].id)

    if path.exists('output\\') is False:
        pathToSave = 'text.mp3'

    readEngine.save_to_file(text_to_read, pathToSave)
    readEngine.runAndWait()
    readEngine.stop()


def read_morse(morse_code):
    """
    Interprets morse code as sounds and reads it 

    Args:
        morse_code (str): morse code data
    
    Returns:
        None
    """
    for char in morse_code:
        if char == '.':
            playsound(resource_path('resources\\sounds\\morseCodeShort.mp3'))
        elif char == '-':
            playsound(resource_path('resources\\sounds\\morseCodeLong.mp3'))


def save_morse_code(morse_code):
    """
    Interprets morse code as sounds and saves it to file

    Args:
        morse_code (str): morse code data

    Returns:
        None
    """
    pathToSave = 'output\\morseSequence.mp3'
    morseCodeLong = AudioSegment.from_file(resource_path('resources\\sounds\\morseCodeLong.mp3'), format='mp3')
    morseCodeShort = AudioSegment.from_file(resource_path('resources\\sounds\\morseCodeShort.mp3'), format='mp3')
    morseCodeSequence = None

    if path.exists('output\\') is False:
        pathToSave = 'morseSequence.mp3'

    for char in morse_code:
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
    """
    Takes data and creates issue, then sends it to GitHub repository

    Args:
        title (str): issue title
        body (str): issue description
    """
    headers = {'Authorization': 'token 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'}
    url = 'https://api.github.com/repos/jerryntom/morsepy/issues'
    dataPack = [{'title': title, 'body': body}]

    for data in dataPack:
        requests.post(url, data=json.dumps(data), headers=headers)


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
        self.setWindowIcon(QtGui.QIcon(resource_path('resources\\images\\icon.png')))
        self.setFixedSize(600, 300)
        self.__background = QtWidgets.QLabel(self)
        self.__menuWindowLayout()

    def __menuWindowLayout(self):
        self.__background.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.__background.setPixmap(QtGui.QPixmap(resource_path('resources/images/background.png')))
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

        self.settings = None
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
        self.textReadingSpeedSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)

    def settingsWindowLayout(self):
        """
        Creates layout for SettingsWindow class 

        Returns:
            None
        """
        self.settings = {}

        with open(resource_path('resources\\data\\settings.txt'), 'r') as file:
            for setting_line in file.readlines():
                setting_line = setting_line.split()
                self.settings[setting_line[0]] = setting_line[1]

        if int(self.settings['textReadingSpeed']) < 100:
            self.settings['textReadingSpeed'] = 100

        new_text_reading_speed = int(self.settings['textReadingSpeed'])

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
            with open(resource_path('resources\\data\\settings.txt'), 'r') as file:
                for settings_line in file.readlines():
                    setting_option, setting_value = settings_line.split()

                    if setting_option == 'language':
                        languageIndex = self.__languageChoice.findText(setting_value)

            self.__languageChoice.setCurrentIndex(languageIndex)

        self.textReadingSpeedSlider.setGeometry(QtCore.QRect(400, 60, 100, 25))
        self.textReadingSpeedSlider.setMinimum(100)
        self.textReadingSpeedSlider.setMaximum(300)
        self.textReadingSpeedSlider.setSingleStep(1)
        self.textReadingSpeedSlider.setValue(new_text_reading_speed)
        self.textReadingSpeedSlider.valueChanged.connect(self.__changeTextReadingSpeed)
        self.textReadingSpeedSlider.setStyleSheet(self.__sliderStyle)

        self.__sliderFont.setBold(True)
        self.__sliderFont.setPointSize(15)

        self.__textReadingSpeedSliderLabel.setText(str(self.textReadingSpeedSlider.value()))
        self.__textReadingSpeedSliderLabel.setGeometry(QtCore.QRect(430, 40, 0, 0))
        self.__textReadingSpeedSliderLabel.setFont(self.__sliderFont)
        self.__textReadingSpeedSliderLabel.adjustSize()

        if languageData['settingsLanguageLabel'] == 'Język':
            self.textReadingSpeedSlider.move(380, 60)
            self.__textReadingSpeedSliderLabel.move(410, 40)
            self.__languageChoice.move(160, 105)
        elif languageData['settingsLanguageLabel'] == 'Language':
            self.textReadingSpeedSlider.move(400, 60)
            self.__textReadingSpeedSliderLabel.move(430, 40)
            self.__languageChoice.move(230, 105)

    def __changeTextReadingSpeed(self):
        """
        Updates text reading speed basing on textReadingSpeedSlider

        Returns:
            None
        """
        self.__textReadingSpeed = self.textReadingSpeedSlider.value()
        self.__textReadingSpeedSliderLabel.setText(str(self.__textReadingSpeed))
        self.__updateSettings()

    def __changeLanguage(self):
        """
        Updates app language basing on languageChoice 

        Returns:
            None
        """
        new_language = self.__languageChoice.currentText()

        if new_language != self.settings['language']:
            self.__languageChangeLabel.setHidden(False)

        self.__updateSettings()

    def __updateSettings(self):
        """
        Updates settings.txt file basing on values set in settings window

        Returns:
            None
        """
        if self.textReadingSpeedSlider.value() != 0:
            with open(resource_path('resources\\data\\settings.txt'), 'w') as file:
                file.write('textReadingSpeed' + ' ' + str(self.textReadingSpeedSlider.value()))
                file.write('\nlanguage' + ' ' + str(self.__languageChoice.currentText()))


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
        """
        Creates layout for AboutWindow class 

        Returns:
            None
        """
        self.__aboutWindowFont.setPointSize(20)

        self.__contributionLabel.setGeometry(50, 30, 50, 50)
        self.__contributionLabel.setText('MorsePy {}\n{}'.format(appVersion, languageData['contributionLabel']))
        self.__contributionLabel.setFont(self.__aboutWindowFont)
        self.__contributionLabel.adjustSize()

        self.__contributionImageLabel.setGeometry(80, 70, 256, 256)
        self.__contributionImageLabel.setPixmap(QtGui.QPixmap(
            resource_path('resources\\images\\contribution.png')).scaled(
            180, 180, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation))

        self.__aboutWindowFont.setPointSize(15)

        self.__repositoryInfoLabel.setGeometry(300, 150, 50, 50)
        self.__repositoryInfoLabel.setText(languageData['repositoryInfoLabel'])
        self.__repositoryInfoLabel.setFont(self.__aboutWindowFont)
        self.__repositoryInfoLabel.adjustSize()

        self.__repositoryLinkLabel.setGeometry(300, 180, 50, 50)
        self.__repositoryLinkLabel.setText('<a href="https://github.com/jerryntom/morsepy">\
            morsepy {}</a>'.format(languageData['repositoryLinkLabel']))
        self.__repositoryLinkLabel.linkActivated.connect(open_url)
        self.__repositoryLinkLabel.setFont(self.__aboutWindowFont)
        self.__repositoryLinkLabel.adjustSize()

        self.__creatorInfoLabel.setGeometry(300, 210, 50, 50)
        self.__creatorInfoLabel.setText(languageData['creatorInfoLabel'])
        self.__creatorInfoLabel.setFont(self.__aboutWindowFont)
        self.__creatorInfoLabel.adjustSize()

        self.__creatorInfoLinkLabel.setGeometry(300, 240, 50, 50)
        self.__creatorInfoLinkLabel.setText('<a href="https://github.com/jerryntom">\
            jerryntom {}</a>'.format(languageData['creatorInfoLinkLabel']))
        self.__creatorInfoLinkLabel.linkActivated.connect(open_url)
        self.__creatorInfoLinkLabel.setFont(self.__aboutWindowFont)
        self.__creatorInfoLinkLabel.adjustSize()


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
        self.__sendIssueDataProcess = None
        self.setWindowTitle(languageData['reportWindowTitle'])
        self.__reportWindowFont = QtGui.QFont()
        self.__reportTipLabel = QtWidgets.QLabel(self)
        self.__issueTitleInput = self.input_box_handler(10, 50, 400, 70, 'issue title input')
        self.__issueDescriptionInput = self.input_box_handler(10, 140, 400, 100, 'issue description input')
        self.__createIssueButton = QtWidgets.QPushButton(self)
        self.__createIssueButton.installEventFilter(self)
        self.__issueCreatedLabel = QtWidgets.QLabel(self)
        self.__hideIssueCreatedLabelTimer = QtCore.QTimer(self)

    def reportWindowLayout(self):
        """
        Creates layout for ReportWindow class 

        Returns:
            None
        """
        self.__reportWindowFont.setPointSize(15)

        self.__reportTipLabel.setGeometry(10, 10, 50, 50)
        self.__reportTipLabel.setText(languageData['reportTipLabel'])
        self.__reportTipLabel.setFont(self.__reportWindowFont)
        self.__reportTipLabel.adjustSize()

        self.__issueTitleInput.setPlaceholderText(languageData['issueTitleInputPlaceholder'])
        self.__issueDescriptionInput.setPlaceholderText(languageData['issueDescriptionInputPlaceholder'])

        self.__createIssueButton.setGeometry(QtCore.QRect(10, 260, 100, 30))
        self.__createIssueButton.setFont(self.__reportWindowFont)
        self.__createIssueButton.setStyleSheet(mainButtonStyle)
        self.__createIssueButton.setFlat(False)
        self.__createIssueButton.setObjectName('changeTranslationType')
        self.__createIssueButton.setText(languageData['createIssueButtonText'])
        self.__createIssueButton.clicked[bool].connect(self.send_issue_data)

        self.__issueCreatedLabel.setGeometry(130, 260, 50, 50)
        self.__issueCreatedLabel.setText(languageData['issueCreated'])
        self.__issueCreatedLabel.setFont(self.__reportWindowFont)
        self.__issueCreatedLabel.adjustSize()
        self.__issueCreatedLabel.setHidden(True)

        self.__hideIssueCreatedLabelTimer.timeout.connect(lambda: self.__issueCreatedLabel.setHidden(True))

    def input_box_handler(self, pos_x, pos_y, width, height, name):
        """
        Template for main input boxes 

        Args:
            pos_x (int): x cordinate of object position
            pos_y (int): y -//-
            width (int): width of the object
            height (int): height -//-
            name (string): name of the object

        Returns:
            self.inputBox (object): ready to use input box
        """
        self.__reportWindowFont.setPointSize(15)
        inputBox = QtWidgets.QTextEdit(self)
        inputBox.setGeometry(QtCore.QRect(pos_x, pos_y, width, height))
        inputBox.setFont(self.__reportWindowFont)
        inputBox.setStyleSheet(inputBoxStyle)
        inputBox.setObjectName(name)
        inputBox.verticalScrollBar().setStyleSheet(scrollBarStyle)
        inputBox.horizontalScrollBar().setEnabled(False)
        inputBox.setAcceptRichText(False)

        return inputBox

    def send_issue_data(self):
        """
        Issue sending handler

        Returns:
            None
        """
        if self.__issueTitleInput.toPlainText() != '' and self.__issueDescriptionInput.toPlainText() != '':
            self.__sendIssueDataProcess = multiprocessing.Process(target=createIssue,
                                                                  args=(self.__issueTitleInput.toPlainText(),
                                                                        self.__issueDescriptionInput.toPlainText(),),
                                                                  daemon=True, name='sending issue to Github')
            self.__sendIssueDataProcess.start()

            self.__issueCreatedLabel.setHidden(False)
            self.__hideIssueCreatedLabelTimer.start(2000)

            self.__issueTitleInput.setText('')
            self.__issueDescriptionInput.setText('')

    def eventFilter(self, obj, event):
        """
        Handler of the events happening within the app

        Args:
            obj (object): object e.g. input box 
            event (type): type of event occuring

        Returns:
            reference to eventFilter, method of QEvent class
        """
        if obj is self.__createIssueButton:
            if event.type() == QEvent.Type.MouseButtonPress:
                new_button_style = """
                border: 2px solid grey;
                border-radius: 20px;
                color: white;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.__createIssueButton.setStyleSheet(new_button_style)
            elif event.type() == QEvent.Type.HoverEnter:
                new_button_style = """
                border: 2px solid grey;
                border-radius: 20px;
                color: black;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.__createIssueButton.setStyleSheet(new_button_style)
            elif event.type() == QEvent.Type.HoverLeave:
                new_button_style = """
                border: 2px solid black;
                border-radius: 18px;
                color: black;"""
                self.__createIssueButton.setStyleSheet(new_button_style)

        return super().eventFilter(obj, event)


class InfoWindow(QDialog):
    """
    Window for showing info about processes happening in the background

    Args:
        QDialog (class): base class for info window
    """

    def __init__(self, info_title, info_message, parent=None):
        """
        Initiation of variables for InfoWindow class

        Args:
            info_title (str): window title
            info_message (str): info message
        """
        super().__init__(parent)

        self.setWindowTitle(info_title)
        self.setWindowIcon(QtGui.QIcon(resource_path('resources\\images\\icon.png')))
        self.__infoButton = QtWidgets.QDialogButtonBox.StandardButton.Ok
        self.__buttonBox = QtWidgets.QDialogButtonBox(self.__infoButton)
        self.__verticalBoxLayout = QtWidgets.QVBoxLayout()
        self.__message = QtWidgets.QLabel(info_message)

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

    def __init__(self, error_title, error_message, parent=None):
        """
        Initiation of variables for InfoWindow class

        Args:
            error_title (str): window title
            error_message (str): error message
        """
        super().__init__(parent)

        self.setWindowTitle(error_title)
        self.setWindowIcon(QtGui.QIcon(resource_path('resources\\images\\icon.png')))

        self.__infoButton = QtWidgets.QDialogButtonBox.StandardButton.Ok
        self.__buttonBox = QtWidgets.QDialogButtonBox(self.__infoButton)
        self.__verticalBoxLayout = QtWidgets.QVBoxLayout()
        self.__message = QtWidgets.QLabel(error_message)

    def error_window_layout(self):
        """
        Creates layout for ErrorWindow class 

        Returns:
            None
        """
        self.__buttonBox.accepted.connect(self.accept)
        self.__verticalBoxLayout.addWidget(self.__message)
        self.__verticalBoxLayout.addWidget(self.__buttonBox)
        self.setLayout(self.__verticalBoxLayout)

    def show_error_window(self):
        """
        Shows error window and closes the app when ok button is clicked

        Returns:
            None
        """
        self.error_window_layout()
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

        self.main_window = None
        self.readingTextProcess = None
        self.readingMorseProcess = None
        self.textData = None
        self.textReadingSpeed = None
        self.morseCodeData = None
        self.saveMorseCodeToSoundProcess = None
        self.infoWindow = None
        self.saveTextToSoundProcess = None
        self.chars = dict()
        self.morseCode = dict()
        validateAppDependencies()

        with open(resource_path('resources\\data\\morseValues.txt'), 'r', encoding='UTF-8') as file:
            for morse_line in file.readlines():
                char, value = morse_line.split()

                self.chars[char] = value
                value = value.replace('•', '.')
                char = char.lower()
                self.morseCode[value] = char

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

        self.__inputBoxData = ''
        self.main_font = QtGui.QFont()
        self.main_widget = QtWidgets.QWidget(MainWindow)
        self.background = QtWidgets.QLabel(self.main_widget)
        self.change_translation_button = QtWidgets.QPushButton(self.main_widget)
        self.text_input_box = self.input_box_handler(60, 40, 490, 180, 'field1')
        self.text_input_box.installEventFilter(self)
        self.morse_input_box = self.input_box_handler(60, 370, 490, 180, 'field2')
        self.morse_input_box.installEventFilter(self)
        self.__textReadButton = self.__sideButtonHandler(552, 62, 45, 45, 'readButton.png', 'read text')
        self.__textReadButton.installEventFilter(self)
        self.__stopTextReadButton = self.__sideButtonHandler(552, 109, 45, 45, 'stopReadButton.png',
                                                             'stop text reading')
        self.__stopTextReadButton.installEventFilter(self)
        self.__saveTextToSoundButton = self.__sideButtonHandler(552, 156, 45, 45, 'saveSoundButton.png',
                                                                'save text to sound')
        self.__saveTextToSoundButton.installEventFilter(self)
        self.__readMorseButton = self.__sideButtonHandler(552, 393, 45, 45, 'readButton.png', 'read morse')
        self.__readMorseButton.installEventFilter(self)
        self.__stopReadMorseButton = self.__sideButtonHandler(552, 440, 45, 45, 'stopReadButton.png', 'stop reading')
        self.__stopReadMorseButton.installEventFilter(self)
        self.__saveMorseToSoundButton = self.__sideButtonHandler(552, 487, 45, 45, 'saveSoundButton.png',
                                                                 'save to sound')
        self.__saveMorseToSoundButton.installEventFilter(self)
        self.change_translation_button.installEventFilter(self)
        self.background.installEventFilter(self)
        self.__textReadButton.installEventFilter(self)
        self.__readMorseButton.installEventFilter(self)
        self.__stopTextReadButton.installEventFilter(self)
        self.__stopReadMorseButton.installEventFilter(self)
        self.__saveTextToSoundButton.installEventFilter(self)
        self.__saveMorseToSoundButton.installEventFilter(self)
        self.__morsePatternCheck = ''
        self.top_menu = QMenuBar()
        self.settingsWindow = None
        self.__aboutWindow = None
        self.__reportWindow = None
        self._language = 'Polski'

    def layout(self, main_window):
        """
        Layout and object setup 

        Args:
            main_window (object): main window of the app  
        """
        self.main_window = main_window
        self.main_window.setObjectName('MainWindow')
        self.main_window.setEnabled(True)
        self.main_window.setFixedSize(600, 600)

        self.main_widget.setObjectName('centralwidget')

        self.background.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.background.setPixmap(QtGui.QPixmap(resource_path('resources/images/background.png')))
        self.background.setObjectName('background')
        self.background.setMouseTracking(True)

        self.top_menu.setStyleSheet('background: url(resources/images/background.png);')
        self.top_menu.addAction(languageData['settingsMenuBar'], lambda: self.show_settings_window())
        self.top_menu.addAction(languageData['aboutMenuBar'], lambda: self.show_about_window())
        self.top_menu.addAction(languageData['reportMenuBar'], lambda: self.show_report_window())

        self.main_window.setMenuBar(self.top_menu)

        self.main_font.setPointSize(25)
        self.main_font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)

        self.change_translation_button.setGeometry(QtCore.QRect(210, 260, 200, 70))
        self.change_translation_button.setFont(self.main_font)
        self.change_translation_button.setStyleSheet(mainButtonStyle)
        self.change_translation_button.setFlat(False)
        self.change_translation_button.setObjectName('changeTranslationType')
        self.change_translation_button.setText(languageData['buttonModeChangeText'])
        self.change_translation_button.clicked[bool].connect(self.change_translation_type)

        self.main_font.setPointSize(20)

        self.text_input_box.setPlaceholderText(languageData['textInputPlaceholder'])
        self.morse_input_box.setReadOnly(True)
        main_window.setCentralWidget(self.main_widget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def input_box_handler(self, pos_x, pos_y, width, height, name):
        """
        Template for main input boxes 

        Args:
            pos_x (int): x cordinate of object position
            pos_y (int): y -//-
            width (int): width of the object
            height (int): height -//-
            name (string): name of the object

        Returns:
            self.inputBox (object): ready to use input box
        """
        self.main_font.setPointSize(20)
        inputBox = QtWidgets.QTextEdit(self.main_widget)
        inputBox.setGeometry(QtCore.QRect(pos_x, pos_y, width, height))
        inputBox.setFont(self.main_font)
        inputBox.setStyleSheet(inputBoxStyle)
        inputBox.setObjectName(name)
        inputBox.verticalScrollBar().setStyleSheet(scrollBarStyle)
        inputBox.horizontalScrollBar().setEnabled(False)
        inputBox.setAcceptRichText(False)

        return inputBox

    def __sideButtonHandler(self, position_x, position_y, width, height, image, tool_tip):
        """
        Template for side buttons 

        Args:
            position_x (int): x cordinate of object position
            position_y (int): y -//-
            width (int): width of the object
            height (int): height -//-
            image (string): name of the file with button image 

        Returns:
            self.sideButton (object): ready to use side button
        """
        sideButton = QtWidgets.QPushButton(self.main_widget)
        sideButton.setGeometry(position_x, position_y, width, height)
        sideButton.setStyleSheet(self.__sideButtonStyle)
        sideButton.setIcon(QtGui.QIcon(resource_path('resources\\images\\{}').format(image)))
        sideButton.setIconSize(QtCore.QSize(25, 25))
        sideButton.setToolTip(tool_tip)

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
        if obj is self.text_input_box:
            if event.type() == QEvent.Type.KeyRelease:
                self.speech_to_morse()
        elif obj is self.change_translation_button:
            if event.type() == QEvent.Type.MouseButtonPress:
                new_button_style = """
                border: 2px solid grey;
                border-radius: 20px;
                color: white;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.change_translation_button.setStyleSheet(new_button_style)
            elif event.type() == QEvent.Type.HoverEnter:
                new_button_style = """
                border: 2px solid grey;
                border-radius: 20px;
                color: black;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.change_translation_button.setStyleSheet(new_button_style)
            elif event.type() == QEvent.Type.HoverLeave:
                new_button_style = """
                border: 2px solid black;
                border-radius: 18px;
                color: black;"""
                self.change_translation_button.setStyleSheet(new_button_style)
        elif obj is self.morse_input_box:
            if event.type() == QEvent.Type.KeyRelease:
                self.morse_to_speech()
        elif obj is self.__textReadButton and self.text_input_box.toPlainText() != '' \
                and self.text_input_box.toPlainText() != languageData['morseCodeTranslateError'] + ' ':
            self.textData = self.text_input_box.toPlainText()
            self.textReadingSpeed = setting

            if self.settingsWindow is not None:
                self.textReadingSpeed = self.settingsWindow.textReadingSpeedSlider.value()

            if event.type() == QEvent.Type.MouseButtonPress and is_process_alive('reading text') is False:
                self.readingTextProcess = multiprocessing.Process(target=read_text, args=(self.textData,
                                                                                          self.textReadingSpeed,),
                                                                  daemon=True, name='reading text')
                self.readingTextProcess.start()
            elif event.type() == QEvent.Type.MouseButtonPress and is_process_alive('reading text') is True:
                self.readingTextProcess.terminate()
                self.readingTextProcess = multiprocessing.Process(target=read_text, args=(self.textData,
                                                                                          self.textReadingSpeed,),
                                                                  daemon=True, name='reading text')
                self.readingTextProcess.start()
        elif obj is self.__readMorseButton and self.morse_input_box.toPlainText() != '' \
                and self.morse_input_box.toPlainText() != languageData['textTranslateError']:
            self.morseCodeData = self.morse_input_box.toPlainText()

            if event.type() == QEvent.Type.MouseButtonPress and is_process_alive('reading morse') is False:
                self.readingMorseProcess = multiprocessing.Process(target=read_morse, args=(self.morseCodeData,),
                                                                   daemon=True, name='reading morse')
                self.readingMorseProcess.start()
            elif event.type() == QEvent.Type.MouseButtonPress and is_process_alive('reading morse') is True:
                self.readingMorseProcess.terminate()
                self.readingMorseProcess = multiprocessing.Process(target=read_morse, args=(self.morseCodeData,),
                                                                   daemon=True, name='reading morse')
                self.readingMorseProcess.start()
        elif obj is self.__stopTextReadButton and is_process_alive('reading text') is True:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.readingTextProcess.terminate()
        elif obj is self.__stopReadMorseButton and is_process_alive('reading morse') is True:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.readingMorseProcess.terminate()
        elif obj is self.__saveTextToSoundButton and self.text_input_box.toPlainText() != \
                languageData['morseCodeTranslateError'] + ' ':
            self.textData = self.text_input_box.toPlainText()
            self.textReadingSpeed = textReadingSpeed

            if self.settingsWindow is not None:
                self.textReadingSpeed = self.settingsWindow.textReadingSpeedSlider.value()

            if event.type() == QEvent.Type.MouseButtonPress and self.textData != '':
                self.saveTextToSoundProcess = multiprocessing.Process(
                    target=save_text_sound, args=(self.textData, self.textReadingSpeed,),
                    daemon=True, name='saving text to sound')
                self.infoWindow = InfoWindow(languageData['textReadingProcessInfoTitle'],
                                             languageData['textReadingProcessInfoMessage'])
                self.infoWindow.showInfoWindow()
                self.saveTextToSoundProcess.start()
        elif obj is self.__saveMorseToSoundButton and self.morse_input_box.toPlainText() \
                != languageData['textTranslateError']:
            if event.type() == QEvent.Type.MouseButtonPress and self.morse_input_box.toPlainText() != '':
                self.morseCodeData = self.morse_input_box.toPlainText()
                self.saveMorseCodeToSoundProcess = multiprocessing.Process(target=save_morse_code,
                                                                           args=(self.morseCodeData,), daemon=True,
                                                                           name='saving morse code to sound')
                self.infoWindow = InfoWindow(languageData['morseReadingProcessInfoTitle'],
                                             languageData['morseReadingProcessInfoMessage'])
                self.infoWindow.showInfoWindow()
                self.saveMorseCodeToSoundProcess.start()

        return super().eventFilter(obj, event)

    def show_settings_window(self):
        """
        Settings window position functioning

        Returns:
            None
        """
        if self.settingsWindow is None:
            self.settingsWindow = SettingsWindow()

        self.settingsWindow.show()
        self.settingsWindow.settingsWindowLayout()
        self.settingsWindow.activateWindow()

    def show_about_window(self):
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

    def show_report_window(self):
        """
        Report window position functioning
        
        Returns:
            None
        """
        if self.__reportWindow is None:
            self.__reportWindow = ReportWindow()

        self.__reportWindow.show()
        self.__reportWindow.reportWindowLayout()
        self.__reportWindow.activateWindow()

    def change_translation_type(self):
        """
        Handler of translation change, switches between main input boxes

        Returns:
            None
        """
        if self.text_input_box.placeholderText() != '':
            self.text_input_box.setPlaceholderText('')
            self.text_input_box.setReadOnly(True)

            self.morse_input_box.setReadOnly(False)
            self.morse_input_box.setPlaceholderText(languageData['morseInputPlaceholder'])
        else:
            self.text_input_box.setPlaceholderText(languageData['textInputPlaceholder'])
            self.text_input_box.setReadOnly(False)

            self.morse_input_box.setPlaceholderText('')
            self.morse_input_box.setReadOnly(True)

        self.morse_input_box.setText('')
        self.text_input_box.setText('')

    def speech_to_morse(self):
        """
        Polish to morse translation mechanism 

        Returns:
            None
        """
        textTranslation = ''
        self.__inputBoxData = self.text_input_box.toPlainText().upper()

        for char in self.__inputBoxData:
            if char == ' ':
                textTranslation += ' | '
            elif char not in self.chars.keys():
                textTranslation = languageData['textTranslateError']
                break
            elif char != ' ':
                textTranslation += self.chars[char] + ' '

        self.text_input_box.verticalScrollBar().setValue(self.text_input_box.verticalScrollBar().maximum())
        self.morse_input_box.setText(textTranslation)

    def morse_to_speech(self):
        """
        Morse to speech translation mechanism

        Returns:
            None
        """
        morseTransalation = ''
        words = self.morse_input_box.toPlainText().split(' | ')
        wordsChars = []
        self.__morsePatternCheck = True
        self.text_input_box.setText('')

        if self.morse_input_box.toPlainText() != '':
            for i in range(0, len(words)):
                words[i] = words[i].strip()
                wordsChars.append(words[i].split(' '))

            for word in wordsChars:
                if not self.__morsePatternCheck:
                    break
                else:
                    for char in word:
                        self.__morsePatternCheck = check_regex(char, '^[.-]{1,7}$')

                        if self.__morsePatternCheck and char in self.morseCode.keys():
                            morseTransalation += self.morseCode[char]
                        elif not self.__morsePatternCheck or char not in self.morseCode.keys():
                            morseTransalation = languageData['morseCodeTranslateError']
                            break

                    morseTransalation += ' '

            self.text_input_box.setText(morseTransalation)
            self.morse_input_box.verticalScrollBar().setValue(self.morse_input_box.verticalScrollBar().maximum())


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowTitle('MorsePy')
    MainWindow.setWindowIcon(QtGui.QIcon(resource_path('resources\\images\\icon.png')))
    userInterface = MorseApp()
    userInterface.layout(MainWindow)
    MainWindow.show()
    exit(app.exec())
