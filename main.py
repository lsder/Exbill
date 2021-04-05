# This Python file uses the following encoding: utf-8
from src.csv_loader import csv_file
from src.account import account
import sys
import os
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from src.impoter import AliPayimpoter, impoter
from src.sheet  import sheet

class main(QWidget):
    def __init__(self, fa):
        super(main, self).__init__()
        self.load_ui()
        self.fa = fa

    def close(self) -> bool:
        return super().close()

    def sel_file(self) -> bool:
        '''选择目录，返回选中的路径'''
        FileDialog = QFileDialog(self.ui)
        FileDirectory = FileDialog.getOpenFileNames(self.ui, "请选择账单文件")
        print(FileDirectory)
        for item in FileDirectory[0]:
            self.ui.listWidget.addItem(item)
        return 0

    def del_file(self) -> bool:
        '''删除选中项'''
        self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())

    def upload(self) -> bool:
        # 获取listwidget中条目
        widgetres = []
        count = self.ui.listWidget.count()
        for i in range(count):
            widgetres.append(self.ui.listWidget.item(i).text())
        import os
        file="./tt.xlsx"
        if  os.path.isfile(file):
            os.remove(file)
        # 遍历listwidget中的内容
        alipay=sheet('tt.xlsx','all',start_row=0,end_row=0)
        alipay.insert_row(1,['交易时间'	,'交易详情','金额（元）','收/支','交易平台','交易类型','预算归属','交易状态' ,'来源\去向','备注'])
        alipay.wb.save(file)#保存数据
        u=[]
        for file in widgetres:
            print(file)
            acc=account(file)
            acc.get_type()
            alipay=account(acc.file,acc.type,acc.csv_headtrow,acc.csv_tailrow)
            a=AliPayimpoter(alipay)
            a.run()

    def load_ui(self):
        '''加载UI文件'''
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "main.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        # 绑定回调函数
        self.ui.add_item.clicked.connect(self.sel_file)
        self.ui.del_item.clicked.connect(self.del_file)
        self.ui.upload.clicked.connect(self.upload)


if __name__ == "__main__":
    app = QApplication([])
    widget = main(app)
    widget.ui.show()
    sys.exit(app.exec_())
