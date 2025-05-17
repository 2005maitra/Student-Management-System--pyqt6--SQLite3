import sys
import sqlite3

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QPushButton, QLabel, QWidget, QGridLayout, QLineEdit,
    QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QLayout,
    QMessageBox
)



class Mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(500,500)

        # Menu bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add student action
        add_student_action = QAction(QIcon("icons/add.png"),"Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # About action
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        # Search action
        search_action = QAction(QIcon("icons/search.png"),"Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "MobileNo"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Toolbar
        toolbar  = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # StatusBar
        self.statusbar =  QStatusBar()
        self.setStatusBar(self.statusbar)

        # Locate a cell
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)


        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)




    def load_data(self):
        connection = sqlite3.connect("004 database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog(self)
        dialog.exec()

    def search(self):
        dialog = SearchDialog(self)
        dialog.exec()

    def edit(self):
        dialog =  EditDialog(self)
        dialog.exec()

    def delete(self):
        dialog =  DeleteDialog(self)
        dialog.exec()

    def  about(self):
        dialog = AboutDialog(self)
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.setWindowTitle("About")
        content = ("This Student Management System is built using Python and SQLite. It provides a simple GUI to manage student records, including adding, editing, searching, and deleting entries. Designed for ease of use, it helps administrators keep track of student information efficiently and reliably within a local database environment."
                   "")
        self.setText(content)




class InsertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile No.")
        layout.addWidget(self.mobile)

        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.currentText()
        mobile = self.mobile.text()

        connection = sqlite3.connect("004 database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students(name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        self.main_window.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Name to Search")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("004 database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + name + '%',))

        self.main_window.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.main_window.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.main_window.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()
        self.close()

class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = self.main_window.table.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No Selection", "Please select a record to edit.")
            self.close()
            return
        student_name =  self.main_window.table.item(index,1).text()

        # Get Id
        self.student_id  = self.main_window.table.item(index,0).text()

        #Update Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText(student_name)
        layout.addWidget(self.student_name)

        #update Course
        course_name =  self.main_window.table.item(index,2).text()
        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Update Mobile No
        mobile_no =  self.main_window.table.item(index,3).text()
        self.mobile = QLineEdit(mobile_no)
        self.mobile.setPlaceholderText("Mobile No.")
        layout.addWidget(self.mobile)

        button = QPushButton("Register")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("004 database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?,mobile =? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.currentText(),
                        self.mobile.text()
                        ,self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        #Update  The Table
        self.main_window.load_data()
        self.close()

class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Delete Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout =QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")


        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no,1,1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        index = self.main_window.table.currentRow()
        student_id  = self.main_window.table.item(index,0).text()


        connection = sqlite3.connect("004 database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE  from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        self.main_window.load_data()
        self.close()

        confirmation_widgets = QMessageBox()
        confirmation_widgets.setWindowTitle("Success")
        confirmation_widgets.setText("The record was deleted successfully")
        confirmation_widgets.exec()


app = QApplication(sys.argv)
main_window = Mainwindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
