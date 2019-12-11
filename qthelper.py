from PyQt5 import QtGui, QtCore, QtWidgets


# Fill in combo box
def qcombo_fill(qcombo, values):
    qcombo.clear()
    for val in values:
        qcombo.addItem(str(val))

# Add a row to an existing table
def qtable_addrow(qtable, iRow, values):
    qtable.insertRow(iRow)
    qtable_setrowval(qtable, iRow, values)

# Replace values of an existing row
def qtable_setrowval(qtable, iRow, values):
    for iCol, val in enumerate(values):
        qtable.setItem(iRow, iCol, QtWidgets.QTableWidgetItem(str(val)))


# Replace values of an existing column
def qtable_setcolval(qtable, iCol, values):
    for iRow, val in enumerate(values):
        qtable.setItem(iRow, iCol, QtWidgets.QTableWidgetItem(str(val)))


def qtable_setrowcolor(qtable, iRow, color):
    for iCol in range(qtable.columnCount()):
        qtable.item(iRow, iCol).setBackground(color)


def qtable_setcolcolor(qtable, iCol, color):
    for iRow in range(qtable.rowCount()):
        qtable.item(iRow, iCol).setBackground(color)