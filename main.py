'''
[+] Remove main music
[] Redo emote music with QSound
  [+] Allow disable music
[+] Rank Questions
[+] Filter :: Except Lowercase
[+] Filter :: Allow exact match
[+] Filter :: Force at least 3 letters
[+] Add reveal button
  [+] Ensure it is counted as answered, but by neither team
[] Beta-test
[] Undo button
'''

###############################
# Import system libraries
###############################
import os, sys, locale
import json
import numpy as np
#from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play


from PyQt5 import QtGui, QtCore, QtWidgets

#######################################
# Compile QT File
#######################################
ui_ui_path = 'feudwindow.ui'
ui_py_path = 'feudwindow.py'
qtCompilePrefStr = 'pyuic5 ' + ui_ui_path + ' -o ' + ui_py_path
print("Compiling QT GUI file", qtCompilePrefStr)
os.system(qtCompilePrefStr)

#######################################
# Load QT file
#######################################
from feudwindow import Ui_FeudWindow

#######################################
# Auxiliary functions
#######################################
def counts2rankpoints(counts):
    nVal = len(counts)
    nDiffVal = len(set(counts))
    points = [nDiffVal + 1]
    for i in range(1, nVal):
        step = int(counts[i-1] > counts[i])
        points += [points[-1] - step]
    return np.round(points / np.sum(points) * 100).astype(int)

#######################################################
# Main Window
#######################################################
class FamilyFeudGui():
    def __init__(self, dialog):

        # Init GUI
        self.dialog = dialog
        self.gui = Ui_FeudWindow()
        self.gui.setupUi(dialog)

        # Adjust window size to display
        screenRes = QtWidgets.QDesktopWidget().screenGeometry()
        #self.gui.logoLabel.setGeometry(0,0, screenRes.width()*0.8, screenRes.height()*0.8)
        self.gui.answersLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        #self.gui.answerLabel.setMargin(0)

        # GUI-Constants
        self.fontsize = 25

        # Load JSON File
        with open('questions_main.json') as json_file:
            self.questiondata = json.load(json_file)

        # Init sounds
        self.thisSoundThread = None
        self.haveSounds = True
        self.sounds = {
            "fail" : "midi/fail.wav",
            "yay": "midi/yay.wav",
            "victory": "midi/victory.wav",
        }

        self.bgsounds = ["midi/million" + str(i) + ".mp3" for i in range(1, 7)]

        # Init scores
        self.nTotalQuestions = len(self.questiondata)
        self.teamThatAnswered = {k : ["None"]*len(v["Answers"]) for k,v in self.questiondata.items()}
        for question in self.questiondata.values():
            question["Scores"] = counts2rankpoints(question["Values"])
        self.teamName2color = {
            "Team Red" : QtGui.QColor(247, 146, 156),
            "Team Blue" : QtGui.QColor(146, 175, 247)}
        self.nTeams = len(self.teamName2color)

        # Init answer
        self.gui.answerLabel.setMargin(200)

        # Fill in Stats Table
        self.gui.statsTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.gui.statsTableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.gui.statsTableWidget.setRowCount(0)
        for iRow, questionKey in enumerate(self.questiondata.keys()):
            self.gui.statsTableWidget.insertRow(iRow)
            self.gui.statsTableWidget.setItem(iRow, 0, QtWidgets.QTableWidgetItem(str(questionKey)))
            for iTeam in range(self.nTeams):
                self.gui.statsTableWidget.setItem(iRow, iTeam+1, QtWidgets.QTableWidgetItem(""))
        self.gui.statsTableWidget.insertRow(self.nTotalQuestions)
        self.gui.statsTableWidget.setItem(self.nTotalQuestions, 0, QtWidgets.QTableWidgetItem("Total Score"))
        for iTeam in range(self.nTeams):
            self.gui.statsTableWidget.setItem(self.nTotalQuestions, iTeam + 1, QtWidgets.QTableWidgetItem(""))

        # Init Answers Table
        self.gui.answersTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.gui.answersTableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Fill in Question Combo Box
        self.gui.questionsComboBox.clear()
        #self.gui.questionsComboBox.addItem("---Select Question----")
        for questionKey in self.questiondata.keys():
            self.gui.questionsComboBox.addItem(questionKey)
        self.reactQuestionSelect()

        # Listeners - UI
        self.gui.questionsComboBox.currentIndexChanged.connect(self.reactQuestionSelect)
        self.gui.answerPushButton.clicked.connect(self.reactQuestionSubmit)
        self.dialog.keyPressEvent = self.keyPressEvent
        self.updateSystemFontSize()


    def reactQuestionSelect(self):
        #self.playsound(np.random.choice(self.bgsounds))
        questionKey = self.gui.questionsComboBox.currentText()
        self.gui.answerLabel.setText(self.questiondata[questionKey]["Title"])
        self.updateAnswersTable(questionKey)


    # Check if current answer matches exactly 1 answer, update answers storage, update table, update stats
    # Otherwise report if answer is wrong or imprecise
    def reactQuestionSubmit(self):
        questionKey = self.gui.questionsComboBox.currentText()
        teamKey = self.gui.teamsComboBox.currentText()
        thisQAnswers = self.questiondata[questionKey]["Answers"]
        thisQTeams = self.teamThatAnswered[questionKey]
        thisAnswer = self.gui.answerLineEdit.text()

        isExact = np.array([thisAnswer.lower() == answer.lower() for answer in thisQAnswers])
        isPartialMatch = np.array([thisAnswer.lower() in answer.lower() for answer in thisQAnswers])
        isCorrect = isExact if np.any(isExact) else isPartialMatch
        isUnrevealed = np.array([teamAnswered == "None" for teamAnswered in thisQTeams])
        filterAnswers = np.where(np.logical_and(isCorrect, isUnrevealed))[0]
        nFilterAnswers = len(filterAnswers)
        minAnswerLen = np.min([len(answer) for answer in thisQAnswers])


        if len(thisAnswer) < np.min((minAnswerLen, 3)):
            print(teamKey, ": Answer Too Sort")
            #self.playsound(self.sounds['fail'])
        elif nFilterAnswers == 0:
            print(teamKey, ": NOPE!")
            self.playsound(self.sounds['fail'])

        elif nFilterAnswers > 1:
            print(teamKey, ": Imprecise!")
            self.playsound(self.sounds['fail'])
        else:
            answerIdx = filterAnswers[0]
            print(teamKey, ": YES! Answer", thisAnswer, "matches", thisQAnswers[answerIdx])
            self.teamThatAnswered[questionKey][answerIdx] = teamKey
            self.updateAnswersTable(questionKey)
            self.updateStatsTable()
            self.playsound(self.sounds['yay'])


    def revealQuestion(self):
        questionKey = self.gui.questionsComboBox.currentText()
        # if questionKey != "---Select Question----":
        thisQTeams = self.teamThatAnswered[questionKey]
        isUnrevealed = np.array([teamAnswered == "None" for teamAnswered in thisQTeams])
        if np.any(isUnrevealed):
            answerIdx = np.where(isUnrevealed)[0][0]
            self.teamThatAnswered[questionKey][answerIdx] = "Revealed"
            print("Revealing answer", answerIdx, "for", questionKey)
            self.updateAnswersTable(questionKey)
        else:
            print("No unrevealed answers left")


    def setRowColor(self, table, iRow, color):
        for iCol in range(table.columnCount()):
            #print(iRow, iCol)
            table.item(iRow, iCol).setBackground(color)


    def setColColor(self, table, iCol, color):
        for iRow in range(table.rowCount()):
            #print(iRow, iCol)
            table.item(iRow, iCol).setBackground(color)


    # Reload answers table from scratch, marking only questions that have already been answered
    def updateAnswersTable(self, questionKey):
        thisQAnswers =  self.questiondata[questionKey]["Answers"]
        thisQValues = self.questiondata[questionKey]["Values"]
        thisQScores = self.questiondata[questionKey]["Scores"]
        thisQTeams = self.teamThatAnswered[questionKey]

        self.gui.answersTableWidget.setRowCount(0)
        #self.gui.answersTableWidget.setColumnCount(3)
        for iRow, teamAnsweredThisQuestion in enumerate(thisQTeams):
            self.gui.answersTableWidget.insertRow(iRow)
            if teamAnsweredThisQuestion != "None":
                self.gui.answersTableWidget.setItem(iRow, 0, QtWidgets.QTableWidgetItem(thisQAnswers[iRow]))
                self.gui.answersTableWidget.setItem(iRow, 1, QtWidgets.QTableWidgetItem(str(thisQValues[iRow])))
                self.gui.answersTableWidget.setItem(iRow, 2, QtWidgets.QTableWidgetItem(str(thisQScores[iRow])))
                if teamAnsweredThisQuestion != "Revealed":
                    teamColor = self.teamName2color[teamAnsweredThisQuestion]
                    self.setRowColor(self.gui.answersTableWidget, iRow, teamColor)


    # Calculate number of points for each team for each question and total
    def updateStatsTable(self):
        totalPoints = {teamName : 0 for teamName in self.teamName2color.keys()}
        # Update points per question
        for iQuestion, (questionKey, questionVal) in enumerate(self.questiondata.items()):
            pointsThisQuestion = {team : 0 for team in self.teamName2color.keys()}
            nAnswerThis = len(questionVal["Answers"])
            for iAns in range(nAnswerThis):
                teamAnswered = self.teamThatAnswered[questionKey][iAns]
                if teamAnswered not in ["None", "Revealed"]:
                    pointsThisQuestion[teamAnswered] += questionVal["Scores"][iAns]

            for iTeam, (teamName, teamPoints) in enumerate(pointsThisQuestion.items()):
                self.gui.statsTableWidget.setItem(iQuestion, iTeam+1, QtWidgets.QTableWidgetItem(str(teamPoints)))
                totalPoints[teamName] += teamPoints

        # Update total points
        for iTeam, (teamName, teamPoints) in enumerate(totalPoints.items()):
            self.gui.statsTableWidget.setItem(self.nTotalQuestions, iTeam+1, QtWidgets.QTableWidgetItem(str(teamPoints)))

        # Update column colors
        for iCol, teamColor in enumerate(self.teamName2color.values()):
            self.setColColor(self.gui.statsTableWidget, iCol+1, teamColor)


    # React to key presses
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Plus or e.key() == QtCore.Qt.Key_Minus:
            self.fontsize += int(e.key() == QtCore.Qt.Key_Plus) - int(e.key() == QtCore.Qt.Key_Minus)
            self.updateSystemFontSize()
        elif e.key() == QtCore.Qt.Key_F:
            self.revealQuestion()
        elif e.key() == QtCore.Qt.Key_M:
            self.haveSounds = not self.haveSounds
            print("Sounds set to", self.haveSounds)
        elif e.key() == QtCore.Qt.Key_W:
            self.playsound(self.sounds['victory'])


    def updateSystemFontSize(self):
        print("New font size", self.fontsize)
        self.gui.centralWidget.setStyleSheet("font-size: " + str(self.fontsize) + "pt;")
        self.gui.answerLabel.setStyleSheet("font-size: " + str(self.fontsize + 40) + "pt;")


    def playsound(self, soundpath):
        if self.haveSounds:
            self.thisSoundThread = playSoundThread(soundpath)
            self.thisSoundThread.finished.connect(self.stopsound)
            self.thisSoundThread.start()
            #del self.thisSoundThread

    def stopsound(self):
        #del self.thisSoundThread
        pass


class playSoundThread(QtCore.QThread):
    def __init__(self, soundpath):
        QtCore.QThread.__init__(self)

        self.soundpath = soundpath

    def __del__(self):
        #self.wait()
        print("Thread exited")

    def run(self):
        play(AudioSegment.from_mp3(self.soundpath))


#######################################################
## Start the QT window
#######################################################
if __name__ == '__main__' :
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = QtWidgets.QMainWindow()
    screenRes = QtWidgets.QDesktopWidget().screenGeometry()
    mainwindow.setFixedSize(screenRes.width(), screenRes.height())
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    pth1 = FamilyFeudGui(mainwindow)
    mainwindow.show()
    sys.exit(app.exec_())
