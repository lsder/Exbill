class account:
    

    def __init__(self,filename='',name='',start_row=0,endrow=0,encoding='GBK'):
        """
        @description: :
        @param  :
        @Returns  :
        """
        self.file=filename
        self.name=name
        self.type=''
        self.csv_headtrow=start_row
        self.csv_tailrow=endrow
        self.encoding=encoding
    def get_type(self):
        '''获取账单类型'''
        if 'alipay' in self.file:
            self.type='AliPay'
            self.csv_headtrow=5
            self.csv_tailrow=7
            self.encoding='GBK'
        elif '微信' in self.file:
            self.type='WechatPay'
            self.csv_headtrow=17
            self.csv_tailrow=0
            self.encoding='UTF-8'
        elif 'hisdetail' in self.file:
            self.type='ICBC'
            self.csv_headtrow=7
            self.csv_tailrow=2
            self.encoding='UTF-8'
        else:pass
        return self.type
if __name__ =="__main__":
    import sys
    home='/'.join(sys.argv[0].split('/')[:-2])
    sys.path.append(home)
    from src.csv_loader import csv_file
    from src.sheet import sheet
    alipay=account(home+"/data/temp/alipay_record_20210103_1339_1.csv",'Alipay',5,7)
    fil=csv_file(alipay)
    alipay=sheet('tt.xlsx','alipay',start_row=5,end_row=7)
    alipay.import_data(fil)