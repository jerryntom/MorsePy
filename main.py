import pyttsx3 as tts
from re import match
from ctypes import windll
from platform import system
from sys import argv, exit
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QWidget, QDialog
from PySide6.QtCore import QEvent
from playsound import playsound
from pydub import AudioSegment
import multiprocessing

readEngine = tts.init()
AudioSegment.converter = "ffmpeg.exe"
AudioSegment.ffmpeg = "ffmpeg.exe"

if system() == "Windows":
    appId = u'jerryntom.python.morseapp.120720221'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
else:
    pass


def readText(textToRead):
    """
    Reading text mechanism 
    
    Args:
        data (string): text to read
    
    Returns:
        None
    """
    voices = readEngine.getProperty('voices')
    readEngine.setProperty('rate', 150)
    readEngine.setProperty('voice', voices[1].id)
    readEngine.say(textToRead)
    readEngine.runAndWait()
    readEngine.stop()


def saveTextSound(textToRead):
    voices = readEngine.getProperty('voices')
    readEngine.setProperty('rate', 150)
    readEngine.setProperty('voice', voices[1].id)
    readEngine.save_to_file(textToRead, 'output\\text.mp3')
    readEngine.runAndWait()
    readEngine.stop()


def readMorse(morseCode):
    for char in morseCode:
        if char == ".":
            playsound('resources\\sounds\\morseCodeShort.mp3')
        elif char == "-":
            playsound('resources\\sounds\\morseCodeLong.mp3')


def saveMorseCode(morseCode):
    morseCodeLong = AudioSegment.from_file("resources\\sounds\\morseCodeLong.mp3", format='mp3')
    morseCodeShort = AudioSegment.from_file("resources\\sounds\\morseCodeShort.mp3", format='mp3')
    morseCodeSequence = None

    for char in morseCode:
        if morseCodeSequence is None and char != " ":
            if char == ".":
                morseCodeSequence = morseCodeShort
            elif char == "-":
                morseCodeSequence = morseCodeLong
        elif morseCodeSequence is not None:
            if char == ".":
                morseCodeSequence += morseCodeShort
            elif char == "-":
                morseCodeSequence += morseCodeLong

    morseCodeSequenceOutput = morseCodeSequence.export("output\\morseSequence.mp3", format="mp3")


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
        self.setWindowTitle("Window")
        self.setWindowIcon(QtGui.QIcon("resources\\images\\icon.png"))
        self.setFixedSize(600, 300)
        self.input = QtWidgets.QTextEdit(self)
        self.input.setGeometry(QtCore.QRect(60, 40, 490, 180))
        self.input.setStyleSheet("font-size: 30px;")
        self.input.setObjectName("inputBox")
        self.input.setPlaceholderText("Domyślne okno menu - test")
        self.input.horizontalScrollBar().setEnabled(False)
        self.input.setAcceptRichText(False)


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
        self.setWindowTitle("Settings")
        self.input.setPlaceholderText("Okno ustawień")


class HelpWindow(MenuWindow):
    """
    Help window where you can get some help if in trouble with using the app

    Args:
        MenuWindow (class): base class for menu window
    """
    def __init__(self):
        """
        Initiation of variables for HelpWindow class 
        """
        super().__init__()
        self.setWindowTitle("Help")
        self.input.setPlaceholderText("Okno pomocy")


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
        self.setWindowTitle("About")
        self.input.setPlaceholderText("Okno informacji o projekcie")


class BugReportWindow(MenuWindow):
    """
    Window for reporting bugs concerning the app

    Args:
        MenuWindow (class): base class for menu window
    """
    def __init__(self):
        """
        Initiation of variables for BugReportwindow class 
        """
        super().__init__()
        self.setWindowTitle("Bug report")
        self.input.setPlaceholderText("Okno zgłaszania błędów")


class InfoWindow(QDialog):
    def __init__(self, infoTitle, infoMessage, parent=None):
        self.infoTitle = infoTitle
        self.infoMessage = infoMessage
        super().__init__(parent)

        self.setWindowTitle(self.infoTitle)
        self.setWindowIcon(QtGui.QIcon("resources\\images\\icon.png"))

        infoButton = QtWidgets.QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QtWidgets.QDialogButtonBox(infoButton)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel(self.infoMessage)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


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

        with open("resources\\data\morseValues.txt", "r", encoding="UTF-8") as file:
            for line in file.readlines():
                char, value = line.split()

                self.chars[char] = value
                value = value.replace('•', '.')
                char = char.lower()
                self.morseCode[value] = char

        self.inputBoxStyle = """
        color: black;
        background-color: white;
        border: 2px solid black;
        border-radius: 18px;
        padding: 10px;"""

        self.changeTranslationButtonStyle = """
        border: 2px solid black;
        border-radius: 18px;
        color: black;"""

        self.sideButtonStyle = """
        QPushButton {
            background-color: transparent;
            border-radius: 22px;
        }
            
        QToolTip {
            color: #ffffff; 
            background-color: #000000;
            border: 0px;
        }"""

        self.scrollBarStyle = """
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

        self.inputBoxData = ""
        self.font = QtGui.QFont()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.background = QtWidgets.QLabel(self.centralwidget)
        self.changeTranslationButton = QtWidgets.QPushButton(self.centralwidget)
        self.inputBox1 = self.inputBoxHandler(60, 40, 490, 180, "field1")
        self.inputBox1.installEventFilter(self)
        self.inputBox2 = self.inputBoxHandler(60, 370, 490, 180, "field2")
        self.inputBox2.installEventFilter(self)
        self.readButton1 = self.sideButtonHandler(552, 62, 45, 45, "readButton.png", "read words")
        self.readButton1.installEventFilter(self)
        self.stopReadButton1 = self.sideButtonHandler(552, 109, 45, 45, "stopReadButton.png", "stop reading")
        self.stopReadButton1.installEventFilter(self)
        self.saveSoundButton1 = self.sideButtonHandler(552, 156, 45, 45, "saveSoundButton.png", "save to sound")
        self.saveSoundButton1.installEventFilter(self)
        self.readButton2 = self.sideButtonHandler(552, 393, 45, 45, "readButton.png", "read morse")
        self.readButton2.installEventFilter(self)
        self.stopReadButton2 = self.sideButtonHandler(552, 440, 45, 45, "stopReadButton.png", "stop reading")
        self.stopReadButton2.installEventFilter(self)
        self.saveSoundButton2 = self.sideButtonHandler(552, 487, 45, 45, "saveSoundButton.png", "save to sound")
        self.saveSoundButton2.installEventFilter(self)
        self.changeTranslationButton.installEventFilter(self)
        self.background.installEventFilter(self)
        self.readButton1.installEventFilter(self)
        self.readButton2.installEventFilter(self)
        self.stopReadButton1.installEventFilter(self)
        self.stopReadButton2.installEventFilter(self)
        self.saveSoundButton1.installEventFilter(self)
        self.saveSoundButton2.installEventFilter(self)
        self.morsePatterCheck = ""
        self.menuBar = QMenuBar()
        self.settingsWindow = None
        self.helpWindow = None
        self.aboutWindow = None
        self.reportWindow = None

    def layout(self, mainWindow):
        """
        Layout and object setup 

        Args:
            mainWindow (object): main window of the app  
        """
        mainWindow.setObjectName("MainWindow")
        mainWindow.setEnabled(True)
        mainWindow.setFixedSize(600, 600)

        self.centralwidget.setObjectName("centralwidget")

        self.background.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.background.setPixmap(QtGui.QPixmap("resources/images/background.png"))
        self.background.setObjectName("background")
        self.background.setMouseTracking(True)

        self.menuBar.setStyleSheet("background: url(resources/images/background.png);")
        self.menuBar.addAction("Settings", lambda: self.showSettingsWindow())
        self.menuBar.addAction("Help", lambda: self.showHelpWindow())
        self.menuBar.addAction("About", lambda: self.showAboutWindow())
        self.menuBar.addAction("Bug report", lambda: self.showBugReportWindow())

        mainWindow.setMenuBar(self.menuBar)

        self.font.setPointSize(25)
        self.font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)

        self.changeTranslationButton.setGeometry(QtCore.QRect(210, 260, 200, 70))
        self.changeTranslationButton.setFont(self.font)
        self.changeTranslationButton.setStyleSheet(self.changeTranslationButtonStyle)
        self.changeTranslationButton.setFlat(False)
        self.changeTranslationButton.setObjectName("changeTranslationType")
        self.changeTranslationButton.setText("Zamień")
        self.changeTranslationButton.clicked[bool].connect(self.changeTranslationType)

        self.font.setPointSize(20)

        self.inputBox1.setPlaceholderText("Wpisz tekst do przetłumaczenia")
        self.inputBox2.setReadOnly(True)

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def inputBoxHandler(self, positionX, positionY, width, height, name):
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
        self.font.setPointSize(20)
        self.inputBox = QtWidgets.QTextEdit(self.centralwidget)
        self.inputBox.setGeometry(QtCore.QRect(positionX, positionY, width, height))
        self.inputBox.setFont(self.font)
        self.inputBox.setStyleSheet(self.inputBoxStyle)
        self.inputBox.setObjectName(name)
        self.inputBox.verticalScrollBar().setStyleSheet(self.scrollBarStyle)
        self.inputBox.horizontalScrollBar().setEnabled(False)
        self.inputBox.setAcceptRichText(False)
        
        return self.inputBox

    def sideButtonHandler(self, positionX, positionY, width, height, image, toolTip):
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
        self.sideButton = QtWidgets.QPushButton(self.centralwidget)
        self.sideButton.setGeometry(positionX, positionY, width, height)
        self.sideButton.setStyleSheet(self.sideButtonStyle)
        self.sideButton.setIcon(QtGui.QIcon("resources\\images\\{}".format(image)))
        self.sideButton.setIconSize(QtCore.QSize(25, 25))
        self.sideButton.setToolTip(toolTip)

        return self.sideButton

    def eventFilter(self, obj, event):
        """
        Handler of the events happening within the app

        Args:
            obj (object): object e.g. input box 
            event (type): type of event occuring

        Returns:
            reference to eventFilter, method of QEvent class
        """
        if obj is self.inputBox1:
            if event.type() == QEvent.Type.KeyRelease:
                self.polishToMorse()
        elif obj is self.changeTranslationButton:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.changeTranslationButtonStyle = """
                border: 2px solid grey;
                border-radius: 20px;
                color: white;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.changeTranslationButton.setStyleSheet(self.changeTranslationButtonStyle)
            elif event.type() == QEvent.Type.HoverEnter:
                self.changeTranslationButtonStyle = """
                border: 2px solid grey;
                border-radius: 20px;
                color: black;
                background-color: rgba(0, 0, 0, 0.13);"""
                self.changeTranslationButton.setStyleSheet(self.changeTranslationButtonStyle)
            elif event.type() == QEvent.Type.HoverLeave:
                self.changeTranslationButtonStyle = """
                border: 2px solid black;
                border-radius: 18px;
                color: black;"""
                self.changeTranslationButton.setStyleSheet(self.changeTranslationButtonStyle)
        elif obj is self.inputBox2:
            if event.type() == QEvent.Type.KeyRelease:
                self.morseToPolish()
        elif obj is self.readButton1 and self.inputBox1.toPlainText() != "":
            if event.type() == QEvent.Type.MouseButtonPress and self.isProcessAlive("reading text") == False:
                self.textData = self.inputBox1.toPlainText()
                self.readingTextProcess = multiprocessing.Process(target=readText, args=(self.textData,), 
                daemon=True, name="reading text")
                self.readingTextProcess.start()
        elif obj is self.readButton2 and self.inputBox2.toPlainText() != "":
            if event.type() == QEvent.Type.MouseButtonPress and self.isProcessAlive("reading morse") == False:
                self.morseCode = self.inputBox2.toPlainText()
                self.readingMorseProcess = multiprocessing.Process(target=readMorse, args=(self.morseCode,), 
                daemon=True, name="reading morse")
                self.readingMorseProcess.start()
        elif obj is self.stopReadButton1:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.readingTextProcess.terminate()
        elif obj is self.stopReadButton2:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.readingMorseProcess.terminate()
        elif obj is self.saveSoundButton1:
            if event.type() == QEvent.Type.MouseButtonPress and self.inputBox1.toPlainText() != "":
                self.textData = self.inputBox1.toPlainText()
                self.saveTextToSoundProcess = multiprocessing.Process(target=saveTextSound, args=(self.textData,), 
                daemon=True, name="saving text to sound")
                self.showInfoWindow("Process info", "Text reading is saved to file in output directory")
                self.saveTextToSoundProcess.start()
        elif obj is self.saveSoundButton2:
            if event.type() == QEvent.Type.MouseButtonPress and self.inputBox2.toPlainText() != "":
                self.morseCode = self.inputBox2.toPlainText()
                self.saveMorseCodeToSoundProcess = multiprocessing.Process(target=saveMorseCode, args=(self.morseCode,),
                daemon=True, name="saving morse code to sound")
                self.showInfoWindow("Process info", "Morse code sequence is saved to file in output directory")
                self.saveMorseCodeToSoundProcess.start()

        return super().eventFilter(obj, event)

    def showSettingsWindow(self):
        """
        Settings window position functioning

        Returns:
            None
        """
        if self.settingsWindow is None:
            self.settingsWindow = MenuWindow()

        self.settingsWindow.show()
        self.settingsWindow.activateWindow()

    def showHelpWindow(self):
        """
        Help window position functioning
        
        Returns:
            None
        """
        if self.helpWindow is None:
            self.helpWindow = HelpWindow()

        self.helpWindow.show()
        self.helpWindow.activateWindow()

    def showAboutWindow(self):
        """
        About window position functioning
        
        Returns:
            None
        """
        if self.aboutWindow is None:
            self.aboutWindow = AboutWindow()

        self.aboutWindow.show()
        self.aboutWindow.activateWindow()

    def showBugReportWindow(self):
        """
        Report window position functioning
        
        Returns:
            None
        """
        if self.reportWindow is None:
            self.reportWindow = BugReportWindow()

        self.reportWindow.show()
        self.reportWindow.activateWindow()

    def showInfoWindow(self, infoTitle="info", infoMessage="info"):
        self.infoWindow = InfoWindow(infoTitle, infoMessage)
        self.infoWindow.show()
        self.infoWindow.activateWindow()

    def changeTranslationType(self):
        """
        Handler of translation change, switches between main input boxes

        Returns:
            None
        """
        if self.inputBox1.placeholderText() != "":
            self.inputBox1.setPlaceholderText("")
            self.inputBox1.setReadOnly(True)

            self.inputBox2.setReadOnly(False)
            self.inputBox2.setPlaceholderText("Wpisz kod do przetłumaczenia")
        else:
            self.inputBox1.setPlaceholderText("Wpisz tekst do przetłumaczenia")
            self.inputBox1.setReadOnly(False)

            self.inputBox2.setPlaceholderText("")
            self.inputBox2.setReadOnly(True)

        self.inputBox2.setText("")
        self.inputBox1.setText("")

    def polishToMorse(self):
        """
        Polish to morse translation mechanism 

        Returns:
            None
        """
        translation = ""
        self.inputBoxData = self.inputBox1.toPlainText().upper()

        for char in self.inputBoxData:
            if char == " ":
                translation += " | "
            elif char not in self.chars.keys():
                translation = "Znaleziono nieznany znak"
                break
            elif char != " ":
                translation += self.chars[char] + " "

        self.inputBox1.verticalScrollBar().setValue(self.inputBox1.verticalScrollBar().maximum())
        self.inputBox2.setText(translation)
        
    def morseToPolish(self):
        """
        Morse to polish translation mechanism

        Returns:
            None
        """
        translation = ""
        pattern = "^[.-]{1,7}$"
        words = self.inputBox2.toPlainText().split(" | ")
        wordsChars = []
        self.morsePatterCheck = True
        self.inputBox1.setText("")

        if self.inputBox2.toPlainText() != "":
            for i in range(0, len(words)):
                words[i] = words[i].strip()
                wordsChars.append(words[i].split(" "))

            for word in wordsChars:
                if not self.morsePatterCheck:
                    break
                else:
                    for char in word:
                        self.morsePatterCheck = match(pattern, char)

                        if self.morsePatterCheck and char in self.morseCode.keys():
                            translation += self.morseCode[char]
                        elif not self.morsePatterCheck or char not in self.morseCode.keys():
                            translation = "Błędne kodowanie!"
                            break

                    translation += " "

            self.inputBox1.setText(translation)
            self.inputBox2.verticalScrollBar().setValue(self.inputBox2.verticalScrollBar().maximum())

    def isProcessAlive(self, processName):
        for process in multiprocessing.active_children():
            if process.name == processName:
                return True

        return False 


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowTitle("MorsePy")
    MainWindow.setWindowIcon(QtGui.QIcon("resources\\images\\icon.png"))
    userInterface = MorseApp()
    userInterface.layout(MainWindow)
    MainWindow.show()
    exit(app.exec())
