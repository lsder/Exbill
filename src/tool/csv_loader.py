import csv
from collections import Counter
len_config={'AliPay':17}

#从原始账单文件获取数据
class csv_file:
    def __init__(self,file_name,encoding='GBK',head_count=0,tail_count=0):
        self.file_name=file_name
        self.encoding=encoding
        self.type=''

        self.head_count=head_count
        self.tail_count=tail_count
        self.row_count=0
        self.data_count=0

        self.head=[]#头部
        self.tail=[]#尾部
        self.rows=[]#所有行
        self.data=[]#数据行

        self._read_type()
        self._read_csv()
        self._get_head()
        self._get_data()
        self._get_tail()
    def _read_type(self):
        '''获取账单类型'''
        if 'alipay' in self.file_name:
            self.type='AliPay'
        elif '微信' in self.file_name:
            self.type='WechatPay'
        elif 'hisdetail' in self.file_name:
            self.type='ICBC'
        else:pass
        return self.type

    def _read_csv(self):
        '''逐行读取所有数据.返回数据及行数'''
        rows=[]
        with open(self.file_name,encoding=self.encoding)as f:
            f_csv = csv.reader(f)
            for i,row in enumerate(f_csv): 
                rows.append(row)
        self.rows=rows
        self.row_count=i+1
        return self.rows,self.row_count
    def _get_head(self):
        self.head.extend(self.rows[:self.head_count])

    def _get_data(self):
        self.data.extend(self.rows[self.head_count:(self.row_count-self.tail_count)])

    def _get_tail(self):
        self.tail.extend(self.rows[-self.tail_count:])

    def data_parser(self):pass
    '''数据转换为字典格式'''
if __name__ =="__main__":
    import sys
    home='/'.join(sys.argv[0].split('/')[:-3])
    fil=csv_file(home+"/data/temp/test.csv",head_count=5,tail_count=7)
    print(fil.data[0][0])
    print(fil.data[-1][0])
    print(fil.head)
    print(fil.tail)
    




