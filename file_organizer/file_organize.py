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

        self.current_directory = './'
        self.current_json = 'file_metadata.json'
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
        if filename:
            
            self.load_metadata(filename)
            new_root_dir = os.path.dirname(filename)
            self.current_directory = new_root_dir
            self.current_json =  filename
            self.update_tree_view(new_root_dir)
            self.populate_table()

    def count_files(self, directory):
        """Count the total number of files in the directory"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count
    
    def update_tree_view(self, path):
        """Update the tree view to show the contents of the specified path"""
        self.tree_view.setRootIndex(self.tree_model.index(path))
        self.Total_file_Lbl.setText(str(self.count_files(path)))

    def populate_table(self):
        self.table_model.clear()
        for file_path, metadata in self.file_metadata.items():
            file_name = QStandardItem(metadata["name"])
            tags = QStandardItem(", ".join(metadata["tags"]))
            notes = QStandardItem(metadata["notes"])
            self.table_model.appendRow([file_name, tags, notes])    

        self.table_model.setHorizontalHeaderLabels(["File Name", "Tags", "Notes"])
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
            file_path = self.tree_model.filePath(selected[0])
            rel_path = os.path.relpath(file_path, self.current_directory)
            
            tags = [tag.strip() for tag in self.tag_input.text().split(',') if tag.strip()]
            notes = self.note_input.toPlainText()

            if rel_path not in self.file_metadata:
                self.file_metadata[rel_path] = {
                    'name': os.path.basename(file_path),
                    'tags': [],
                    'notes': ''
                }

            self.file_metadata[rel_path]['tags'] = list(set(self.file_metadata[rel_path]['tags'] + tags))
            
            if notes:
                self.file_metadata[rel_path]['notes'] = notes

            self.save_to_json()
            self.populate_table()
            self.tag_input.clear()
            self.note_input.clear()
            
            QMessageBox.information(self, "Success", "Metadata saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Please select a file first")

    def get_file_path(self, index):
        path = []
        while index.isValid():
            path.insert(0, index.data())
            index = index.parent()
        return os.path.join(*path)

    def load_metadata(self, filepath=None):
        try:
            if not filepath:
                default_path = os.path.join(self.current_directory, self.current_json)
                if os.path.exists(default_path):
                    with open(default_path, 'r') as f:
                        self.file_metadata = json.load(f)
            else:
                with open(filepath, 'r') as f:
                    self.file_metadata = json.load(f)
                
                # Update paths in metadata to be relative to the new root directory
                new_metadata = {}
                base_dir = os.path.dirname(filepath)
                
                for file_path, metadata in self.file_metadata.items():
                    # Convert absolute paths to relative paths if necessary
                    if os.path.isabs(file_path):
                        try:
                            rel_path = os.path.relpath(file_path, base_dir)
                            new_metadata[rel_path] = metadata
                            metadata['name'] = os.path.basename(file_path)
                        except ValueError:
                            # If paths are on different drives or cannot be made relative
                            new_metadata[file_path] = metadata
                    else:
                        new_metadata[file_path] = metadata
                
                self.file_metadata = new_metadata
                
        except FileNotFoundError:
            self.file_metadata = {}
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON file format")
            self.file_metadata = {}

    def save_to_json(self):
        with open(self.current_json, 'w') as f:
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