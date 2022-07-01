import pyttsx3 as tts
from re import match
from ctypes import windll
from platform import system
from sys import argv, exit
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QWidget
from PySide6.QtCore import QEvent

if system() == "Windows":
    appId = u'jerryntom.python.morseapp.3422'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
else:
    pass


class MenuWindow(QWidget):
    def __init__(self):
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


class MenuWindow(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.input.setPlaceholderText("Okno ustawień")


class HelpWindow(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.input.setPlaceholderText("Okno pomocy")


class AboutWindow(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.input.setPlaceholderText("Okno informacji o projekcie")


class BugReportWindow(MenuWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bug report")
        self.input.setPlaceholderText("Okno zgłaszania błędów")


class MorseApp(QMainWindow):
    def __init__(self):
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

        self.buttonStyle = """
        border: 2px solid black;
        border-radius: 18px;
        color: black;"""

        self.sideButtonStyle = """
        border: 2px solid black;
        background-color: white;
        border-radius: 22px;
        color: black;"""

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
        self.field1 = self.inputBoxHandler(60, 40, 490, 180, "field1")
        self.field1.installEventFilter(self)
        self.field2 = self.inputBoxHandler(60, 370, 490, 180, "field2")
        self.field2.installEventFilter(self)
        self.readButton1 = self.sideButtonHandler(552, 64, 45, 45, "readButton.png")
        self.readButton1.installEventFilter(self)
        self.stopReadButton1 = self.sideButtonHandler(552, 111, 45, 45, "stopReadButton.png")
        self.stopReadButton1.installEventFilter(self)
        self.saveSoundButton1 = self.sideButtonHandler(552, 158, 45, 45, "saveSoundButton.png")
        self.saveSoundButton1.installEventFilter(self)
        self.readButton2 = self.sideButtonHandler(552, 395, 45, 45, "readButton.png")
        self.readButton2.installEventFilter(self)
        self.stopReadButton2 = self.sideButtonHandler(552, 442, 45, 45, "stopReadButton.png")
        self.stopReadButton2.installEventFilter(self)
        self.saveSoundButton2 = self.sideButtonHandler(552, 489, 45, 45, "saveSoundButton.png")
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
        self.readEngine = tts.init()
        self.menuBar = QMenuBar()
        self.settingsWindow = None
        self.helpWindow = None
        self.aboutWindow = None
        self.reportWindow = None

    def layout(self, mainWindow):
        mainWindow.setObjectName("MainWindow")
        mainWindow.setEnabled(True)
        mainWindow.setFixedSize(600, 600)

        self.centralwidget.setObjectName("centralwidget")

        self.background.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.background.setPixmap(QtGui.QPixmap("resources/images/background.png"))
        self.background.setObjectName("background")
        self.background.setMouseTracking(True)

        self.menuBar.setStyleSheet("background: url(resources/images/background.png);")
        self.menuBar.addAction("Settings", lambda: self.showSettings())
        self.menuBar.addAction("Help", lambda: self.showHelp())
        self.menuBar.addAction("About", lambda: self.showAbout())
        self.menuBar.addAction("Bug report", lambda: self.showReport())

        mainWindow.setMenuBar(self.menuBar)

        self.font.setPointSize(25)
        self.font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)

        self.changeTranslationButton.setGeometry(QtCore.QRect(210, 260, 200, 70))
        self.changeTranslationButton.setFont(self.font)
        self.changeTranslationButton.setStyleSheet(self.buttonStyle)
        self.changeTranslationButton.setFlat(False)
        self.changeTranslationButton.setObjectName("changeTranslationType")
        self.changeTranslationButton.setText("Zamień")
        self.changeTranslationButton.clicked[bool].connect(self.changeTranslationType)

        self.font.setPointSize(20)

        self.field1.setPlaceholderText("Wpisz tekst do przetłumaczenia")

        self.field2.setReadOnly(True)

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def inputBoxHandler(self, positionX, positionY, width, height, name):
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

    def sideButtonHandler(self, positionX, positionY, width, height, image):
        self.sideButton = QtWidgets.QPushButton(self.centralwidget)
        self.sideButton.setGeometry(positionX, positionY, width, height)
        self.sideButton.setStyleSheet(self.sideButtonStyle)
        self.sideButton.setIcon(QtGui.QIcon("resources\\images\\{}".format(image)))
        self.sideButton.setIconSize(QtCore.QSize(25, 25))

        return self.sideButton

    def eventFilter(self, obj, event):
        if obj is self.field1:
            if event.type() == QEvent.Type.KeyRelease:
                self.polishToMorse()
        elif obj is self.changeTranslationButton:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.buttonStyle = """
                        border: 2px solid grey;
                        border-radius: 20px;
                        color: black;
                        background-color: rgba(0, 0, 0, 0.13);
                        """

                self.changeTranslationButton.setStyleSheet(self.buttonStyle)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.buttonStyle = """
                        border: 2px solid black;
                        border-radius: 20px;
                        color: black;
                        """

                self.changeTranslationButton.setStyleSheet(self.buttonStyle)
        elif obj is self.field2:
            if event.type() == QEvent.Type.KeyRelease:
                self.morseToPolish()
        elif obj is self.readButton1:
            if event.type() == QEvent.Type.MouseButtonPress:
                if self.field1.toPlainText() != "":
                    data = self.field1.toPlainText()
                else:
                    data = self.field1.placeholderText()

                self.readText(data)
        elif obj is self.readButton2:
            pass

            """
            if event.type() == QEvent.Type.MouseButtonPress:
                if self.field2.toPlainText() != "":
                    self.read_text(self.field1.toPlainText())
                else:
                    self.read_text(self.field1.placeholderText())"""
        elif obj is self.stopReadButton2:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.stop_read()
        elif obj is self.stopReadButton1:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.read_text(self.field1.toPlainText(), True)
        elif obj is self.saveSoundButton2:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.save_sound(self.field2.toPlainText())
        elif obj is self.saveSoundButton1:
            pass

            # if event.type() == QEvent.Type.MouseButtonPress:
            #    self.save_sound(self.field1.toPlainText())

        return super().eventFilter(obj, event)

    def showSettings(self):
        if self.settingsWindow is None:
            self.settingsWindow = MenuWindow()

        self.settingsWindow.show()
        self.settingsWindow.activateWindow()

    def showHelp(self):
        if self.helpWindow is None:
            self.helpWindow = HelpWindow()

        self.helpWindow.show()
        self.helpWindow.activateWindow()

    def showAbout(self):
        if self.aboutWindow is None:
            self.aboutWindow = AboutWindow()

        self.aboutWindow.show()
        self.aboutWindow.activateWindow()

    def showReport(self):
        if self.reportWindow is None:
            self.reportWindow = BugReportWindow()

        self.reportWindow.show()
        self.reportWindow.activateWindow()

    def changeTranslationType(self):
        if self.field1.placeholderText() != "":
            self.field1.setPlaceholderText("")
            self.field1.setReadOnly(True)

            self.field2.setReadOnly(False)
            self.field2.setPlaceholderText("Wpisz kod do przetłumaczenia")
        else:
            self.field1.setPlaceholderText("Wpisz tekst do przetłumaczenia")
            self.field1.setReadOnly(False)

            self.field2.setPlaceholderText("")
            self.field2.setReadOnly(True)

        self.field2.setText("")
        self.field1.setText("")

    def polishToMorse(self):
        translation = ""
        self.inputBoxData = self.field1.toPlainText().upper()

        for char in self.inputBoxData:
            if char == " ":
                translation += " | "
            elif char not in self.chars.keys():
                translation = "Znaleziono nieznany znak"
                break
            elif char != " ":
                translation += self.chars[char] + " "

        self.field1.verticalScrollBar().setValue(self.field1.verticalScrollBar().maximum())
        self.field2.setText(translation)
        
    def morseToPolish(self):
        translation = ""
        pattern = "^[.-]{1,7}$"
        words = self.field2.toPlainText().split(" | ")
        wordsChars = []
        self.morsePatterCheck = True
        self.field1.setText("")

        if self.field2.toPlainText() != "":
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

            self.field1.setText(translation)
            self.field2.verticalScrollBar().setValue(self.field2.verticalScrollBar().maximum())

    def readText(self, data, stop=False):
        voices = self.readEngine.getProperty('voices')
        self.readEngine.setProperty('rate', 150)
        self.readEngine.setProperty('voice', voices[1].id)
        self.readEngine.say(data)
        self.readEngine.runAndWait()

    def stopReadText(self):
        self.readEngine.endLoop()

    def saveSoundText(self, data):
        print("Saving...")


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setWindowTitle("MorsePy")
    MainWindow.setWindowIcon(QtGui.QIcon("resources\\images\\icon.png"))
    userInterface = MorseApp()
    userInterface.layout(MainWindow)
    MainWindow.show()
    exit(app.exec())
