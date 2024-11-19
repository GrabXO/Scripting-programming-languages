import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTableView,
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QFormLayout
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import QTimer

class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просмотр базы данных")
        self.setGeometry(300, 300, 700, 500) # размер окна

        self.setupUI()
        self.connect_to_db()
        self.load_data()

    def setupUI(self):
        
        self.main_widget = QWidget(self) # основной виджет приложения
        self.setCentralWidget(self.main_widget) # обозначаем main_widget как центральный виджет
        self.search_box = QLineEdit(self) # создаем поле для текста
        self.search_box.setPlaceholderText("Поиск по заголовку...") # текст-подсказка для поиска
        self.search_box.textChanged.connect(self.filter_data) # при изменении текста вызываем метод фильтрации

        # Кнопки и их методы, срабатывающие при нажатии
        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_posts)
        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_record)

      
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button) # добавляем кнопку на макет приложения
        button_layout.addWidget(self.delete_button)
        layout = QVBoxLayout()
        layout.addLayout(button_layout) # добавляем кнопки
        layout.addWidget(self.search_box) # добавляем поиск
        self.table_view = QTableView(self)
        self.table_view.setAlternatingRowColors(True)
        layout.addWidget(self.table_view) # добавляем таблицу
        self.main_widget.setLayout(layout) # устанавливаем созданный макет в основной виджет.

    def connect_to_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("lab4.db")  
        if not self.db.open():
            print("Не удалось подключиться к базе данных.")
            return
        self.model = QSqlTableModel(self)
        self.model.setTable("posts")
        self.model.select()
        self.table_view.setModel(self.model)
        self.table_view.verticalHeader().setVisible(False)

    def load_data(self):
        self.model.select()
        QTimer.singleShot(0, self.setwidths)

    def setwidths(self):
        total_width = self.table_view.width()
        title_percentage = 30  
        body_percentage = 55   
        id_persentage = 5
        user_id_persentage = 10
        
        title_width = int((title_percentage / 100) * total_width)
        body_width = int((body_percentage / 100) * total_width)
        id = int((id_persentage / 100) * total_width)
        user_id = int((user_id_persentage / 100) * total_width)
        self.table_view.setColumnWidth(0, id) # ширина столбца "id"
        self.table_view.setColumnWidth(1, user_id) # ширина столбца "user_id"
        self.table_view.setColumnWidth(2, title_width) # ширина столбца "title"
        self.table_view.setColumnWidth(3, body_width) # ширина столбца "body"

    def resizeEvent(self, event):
        self.setwidths()
        super().resizeEvent(event)

    def filter_data(self):
        filter_text = self.search_box.text()
        self.model.setFilter(f"title LIKE '%{filter_text}%'")
        self.model.select()

    def add_posts(self):
        dialog = QWidget()
        dialog.setWindowTitle("Добавить запись")
        layout = QFormLayout()
        user_id_input = QLineEdit(dialog)
        title_input = QLineEdit(dialog)
        body_input = QLineEdit(dialog)
        layout.addRow("User ID:", user_id_input)
        layout.addRow("Title:", title_input)
        layout.addRow("Body:", body_input)
        add_button = QPushButton("Добавить", dialog)
        add_button.clicked.connect(lambda: self.save_new_posts(user_id_input.text(), title_input.text(), body_input.text(), dialog))
        layout.addWidget(add_button)
        dialog.setLayout(layout)
        dialog.setGeometry(400, 400, 300, 200)
        dialog.show()

    def save_new_posts(self, user_id, title, body, dialog):
        query = QSqlQuery()
        query.prepare("INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)")
        query.addBindValue(user_id)
        query.addBindValue(title)
        query.addBindValue(body)
        if query.exec_():
            self.load_data()  
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить запись.")

    def delete_record(self):
        
        index = self.table_view.currentIndex()
        if index.isValid():
            record_id = self.model.index(index.row(), 0).data() 
            reply = QMessageBox.question(self, 'Подтверждение', 'Вы уверены, что хотите удалить эту запись?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                query = QSqlQuery()
                query.prepare("DELETE FROM posts WHERE id = ?")
                query.addBindValue(record_id)
                if query.exec_():
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить запись.")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())