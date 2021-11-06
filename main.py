from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qt_material import apply_stylesheet
import random
import datetime
import sqlite3
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.main = uic.loadUi('gameland.ui', self)
        self.gcreatenew.clicked.connect(self.createNew)
        self.gtable.cellClicked.connect(self.activateclock)
        self.delbtn.clicked.connect(self.deleterow)
        ##database
        self.onlyInt = QtGui.QIntValidator()
        self.conn = sqlite3.connect("gameland.db", check_same_thread=False, timeout=10)
        self.cur = self.conn.cursor()
        self.gcharge.setValidator(self.onlyInt)
        self.firstupdate()
        self.gtable.horizontalHeader().setMinimumSectionSize(150)
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.Updater)
        ###

        self.themes = ['dark_red.xml',
                       'dark_blue.xml',
                       'dark_cyan.xml',
                       'dark_lightgreen.xml',
                       'dark_pink.xml',
                       'dark_purple.xml',
                       'dark_amber.xml',
                       'dark_teal.xml',
                       'dark_yellow.xml',
                       'light_amber.xml',
                       'light_blue.xml',
                       'light_cyan.xml',
                       'light_cyan_500.xml',
                       'light_lightgreen.xml',
                       'light_pink.xml',
                       'light_purple.xml',
                       'light_red.xml',
                       'light_teal.xml',
                       'light_yellow.xml']

        apply_stylesheet(self.main, self.themes[random.randint(0,7)])#select between dark themes

        self.show()



    def activateclock(self):
        row = self.gtable.currentRow()
        col = self.gtable.currentColumn()
        item = self.gtable.item(row, 0).text()
        isitrunning = self.cur.execute("select runstatus from games where name='{0}'".format(item)).fetchone()[0]
        if(col == 5):
            if(isitrunning == 0):
                self.cur.execute("update games set runstatus=1 where name='{0}'".format(item))
                self.conn.commit()
                self.gtable.item(row,5).setText("Running!")
                self.gtable.item(row,5).setBackground(QtGui.QColor(255,100,0))
            else:
                self.cur.execute("update games set runstatus=0 where name='{0}'".format(item))
                self.conn.commit()
                self.gtable.item(row,5).setText("Ready to Start!")
                self.gtable.item(row,5).setBackground(QtGui.QColor(0,255,0))
        elif(col == 4):
            self.cur.execute("update games set time=0 where name='{0}'".format(item))
            self.conn.commit()
            if(isitrunning == 0):
                self.gtable.item(row,2).setText("00:00:00")
    def setcol(self):
        row = self.gtable.currentRow()
        col = self.gtable.currentColumn()
        if (col == 5):
            item = self.gtable.item(row, 0).text()
            isitrunning = self.cur.execute("select runstatus from games where name='{0}'".format(item)).fetchone()[0]
            if (isitrunning == 0):
                self.gtable.item(row, 5).setText("Running!")
                self.gtable.item(row, 5).setBackground(QtGui.QColor(255, 100, 0))
            else:
                self.gtable.item(row, 5).setText("Ready to Start!")
                self.gtable.item(row, 5).setBackground(QtGui.QColor(0, 150, 0))
    def createNew(self):
        try:
            name = self.gname.text()
            fee = self.gcharge.text()
            if(name!="" and fee!=""):
                self.cur.execute("insert into games values ('{0}','{1}','{2}','{3}')".format(name, fee, 0, 0))
                self.conn.commit()
                self.firstupdate()
        except Exception as e:
            print(e)

    def firstupdate(self):
        count = self.cur.execute("select count(*) from games").fetchone()
        data = self.cur.execute("select * from games").fetchall()
        self.gtable.setRowCount(count[0])
        for i in range(count[0]):
            self.gtable.setItem(i,0,QTableWidgetItem(data[i][0]))
            self.gtable.setItem(i,1,QTableWidgetItem(str(data[i][1])))
            self.gtable.setItem(i,4,QTableWidgetItem("Press To Reset!"))
            self.gtable.setItem(i,5,QTableWidgetItem("Ready to Start!"))
            self.gtable.item(i,5).setBackground(QtGui.QColor(0,150,0))
            self.setcol()
            self.gtable.setItem(i,2,QTableWidgetItem(str(data[i][2])))
            self.gtable.setItem(i,3,QTableWidgetItem("0"))
        self.updater()


    def updater(self):
        count = self.cur.execute("select count(*) from games").fetchone()
        data = self.cur.execute("select * from games").fetchall()
        for i in range(count[0]):
            if(data[i][3] == 1):
                self.gtable.item(i, 2).setText(str(datetime.timedelta(seconds=int(data[i][2]))))
                self.gtable.item(i, 3).setText(str(int(data[i][1] * (data[i][2] / 60))))

    def Updater(self):
        data = self.cur.execute("select name,time from games where runstatus=1").fetchall()
        for i in data:
            self.cur.execute("update games set time='{0}' where name='{1}'".format(i[1]+1,i[0]))
        self.conn.commit()
        self.updater()
        QCoreApplication.processEvents()


    def deleterow(self):
        row = self.gtable.currentRow()
        if(row >=0):
            name = self.gtable.item(row,0).text()
            self.cur.execute("delete from games where name='{0}'".format(name))
            self.conn.commit()
            self.firstupdate()

    def reset(self):
        self.cur.execute("update games set runstatus=0,time=0")
        self.conn.commit()

    def __del__(self):
        self.reset()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()