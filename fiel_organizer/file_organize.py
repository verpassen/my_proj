import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHeaderView,QMessageBox,QFileSystemModel,QFileDialog )
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5 import uic

class FileOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('file_organize.ui', self)
 
        self.setupModel()
        self.connect_signals()

        # Set up the filter proxy model
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)

        # Search bar
        self.search_bar.textChanged.connect(self.filter_table)
        self.save_btn.clicked.connect(self.save_metadata)
        self.delete_btn.clicked.connect(self.remove_metadata)
        self.clear_btn.clicked.connect(self.clean_metadata)
        self.load_btn.clicked.connect(self.load_file)

        self.file_metadata = {}
        self.load_metadata()
        self.populate_tree()
        self.populate_table()

    def setupModel(self):
         # Tree View
        # self.tree_model = QStandardItemModel()
        self.tree_model = QFileSystemModel()
        self.tree_model.setRootPath(' ')
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setRootIndex(self.tree_model.index('./')) # Default dir. the current fold 

        # Table View
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["File Name", "Tags", "Notes"])
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
 
    def connect_signals(self):
        self.tree_view.clicked.connect(self.on_tree_view_clicked)

    def on_tree_view_clicked(self,index):
        path = self.tree_model.filePath(index)
        if os.path.isdir(path):
            self.current_directory = path
            self.populate_table()

    def populate_tree(self):
        root_dir = "/home/chang/Documents/papers/"  # Replace with your desired directory
        root_item = self.tree_model.rootPath()
        self.add_directory(root_dir, root_item)
        
    def add_directory(self, path, parent):
        # print(path)
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            file_item = QStandardItem(item)
            if os.path.isdir(item_path):
                self.add_directory(item_path, file_item)

        self.Total_file_Lbl.setText(str(self.tree_model.rowCount()))

    def load_file(self):
        filename, _  =  QFileDialog.getOpenFileName(self, 'Open File', os.getenv('./'))
        self.load_metadata(filename)
        self.populate_tree()
        self.populate_table()
        
    def populate_table(self):
        self.table_model.clear()
        for file_path, metadata in self.file_metadata.items():
            file_name = QStandardItem(metadata["name"])
            tags = QStandardItem(", ".join(metadata["tags"]))
            notes = QStandardItem(metadata["notes"])
            self.table_model.appendRow([file_name, tags, notes])    

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def clean_metadata(self):
        pass

    def remove_metadata(self):
        selected = self.table_view.selectedIndexes()
        if selected:
            file_name = self.proxy_model.data(selected[0])
            file_path_to_remove = None

            for file_path , metadata in self.file_metadata.items():
                if metadata["name"] == file_name:
                    file_path_to_remove = file_path
                    break
            if file_path_to_remove:
                del self.file_metadata[file_path_to_remove]

                self.save_to_json()
                self.populate_table()
                QMessageBox.information(self,"Success", f"Metadata for {file_name} has been removed.")
                                                  
            else:
                QMessageBox.warning(self,"Error","Could not find the selected file in the metadata.")
        else:
            QMessageBox.warning(self,"Error","Please select an item to remove.")

    def save_metadata(self):
        selected = self.tree_view.selectedIndexes()
        if selected:
            file_path = self.get_file_path(selected[0])
            tags = [tag.strip() for tag in self.tag_input.text().split(',')]
            notes = self.note_input.toPlainText()

        if file_path not in self.file_metadata:
            self.file_metadata[file_path] = {'name':  file_path, 'tags':[],'notes':''}

        self.file_metadata[file_path]['tags'] = list(set(self.file_metadata[file_path]['tags'] + tags))

        if notes:
            self.file_metadata[file_path]['notes'] = notes
 
        self.save_to_json()
        self.populate_table()
        self.tag_input.clear()

    def get_file_path(self, index):
        path = []
        while index.isValid():
            path.insert(0, index.data())
            index = index.parent()
        return os.path.join(*path)

    def load_metadata(self,filepath=None):
        try:
            if not filepath : 
                with open('file_metadata.json', 'r') as f:
                    self.file_metadata = json.load(f)
            else:
                with open(filepath,'r') as f: 
                    self.file_metadata = json.load(f)
                    
        except FileNotFoundError:
            self.file_metadata = {}

    def save_to_json(self):
        with open('file_metadata.json', 'w') as f:
            json.dump(self.file_metadata, f, indent=2)

    def filter_table(self, text):
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterRegExp(text)
        self.select_file_Lbl.setText(str(self.proxy_model.rowCount()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec_())