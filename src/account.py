class account:
    #账户名称,文件名称，开始行，结束行
    def __init__(self,filename='',name='',start_row=0,endrow=0,encoding='GBK'):
        self.file=filename
        self.name=name
        self.csv_headtrow=start_row
        self.csv_tailrow=endrow
        self.encoding=encoding

if __name__ =="__main__":
    import sys
    home='/'.join(sys.argv[0].split('/')[:-2])
    sys.path.append(home)
    from src.tool import csv_loader
    from src.sheet import sheet
    alipay=account(home+"/data/temp/alipay_record_20210103_1339_1.csv",'Alipay',5,7)
    fil=csv_loader.csv_file(alipay)
    alipay=sheet('tt.xlsx','alipay',start_row=5,end_row=7)
    alipay.import_data(fil)