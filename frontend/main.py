# -*- coding: utf-8 -*-

import os
import sys
import json
import pandas
from pathlib import Path
from subprocess import Popen
from typing import Optional
from sqlalchemy import create_engine
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *

from windows.Windows import *
from config import CurrentDir, ConfigDir

##############################################################################################################################

class MainWindow(Window_MainWindow):
    def __init__(self):
        super().__init__()

    def import_data_to_table(self, df: pandas.DataFrame):
        # 清空表格
        self.ui.Table.clearContents()
        # 设置行列数
        self.ui.Table.setRowCount(len(df))
        self.ui.Table.setColumnCount(len(df.columns) + 1)
        # 设置表头
        self.ui.Table.setHorizontalHeaderLabels(df.columns.tolist() + ["选框"])
        # 填充数据
        '''
        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[row_idx][col_idx]))
                self.ui.Table.setItem(row_idx, col_idx, item)
        '''
        self.ui.Table.SetValue(
            [[str(df.iloc[row_idx][col_idx]) for col_idx in range(len(df.columns))] for row_idx in range(len(df))]
        )

    def export_data_to_sqlite(self):
        # 提取表格数据到列表
        '''
        data = []
        for row in range(self.ui.Table.rowCount()):
            row_data = []
            for column in range(self.ui.Table.columnCount()):
                item = self.ui.Table.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')  # 或者你喜欢的其他默认值
            data.append(row_data)
        '''
        data = self.ui.Table.GetValue()
        print(data)
        # 将列表转为DataFrame
        df = pandas.DataFrame(data)
        # 创建SQLite数据库引擎
        engine = create_engine('sqlite:///my_data.db')
        # 将DataFrame写入SQLite数据库
        df.to_sql(
            name = 'data_table',
            con = engine,
            if_exists = 'replace',
            index = False
        ) # 假设表名为data_table，如果表已存在替换它
        QMessageBox.information(self, "完成", "数据已成功写入SQLite数据库。")

    def open_excel_file(self):
        # 弹出文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self,
            caption = "打开Excel文件",
            dir = "",
            filter = "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:
                # 使用pandas读取Excel文件
                df = pandas.read_excel(file_path)
            except Exception as e:
                print(f"读取Excel文件时出错: {e}")
            else:
                # 导入Excel数据到表格
                self.import_data_to_table(df)
                self.export_data_to_sqlite()

    def Main(self):
        self.setWindowTitle("Excel Data to Table")

        self.ui.Button_LoadData.setText("打开Excel文件")

        self.ui.Button_LoadData.clicked.connect(self.open_excel_file)

        self.show()

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())

##############################################################################################################################