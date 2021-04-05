import calendar
import csv
import re
from typing import MutableSet
from zipfile import ZipFile
from datetime import date
from io import StringIO, BytesIO
import dateparser
import json
import sys
home='/'.join(sys.argv[0].split('/')[:-2])
sys.path.append(home)
from src.csv_loader import csv_file
from src.sheet import sheet
from src.account import account
'''
0	1	2	3	4	5	6	7	8	9	10	11	12	13	14	15	
交易号                  	商家订单号               	交易创建时间              	付款时间                	最近修改时间              	交易来源地     	类型              	交易对方            	商品名称                	金额（元）   	收/支     	交易状态    	服务费（元）   	成功退款（元）  	备注                  	资金状态     	
交易时间	交易详情          	金额（元）	收/支     	交易平台	交易类型	预算归属	交易状态    	来源\去向	备注							
1	1	1	1	1	2	2	有效、已废、待废	2	2							

'''
#数据进行处理与合并
class impoter:
    
    def __init__(self, account):#输入字典列表
        csv_obj=csv_file(account)
        self.csv_obj=csv_obj
        self.acc=account
        self.orig_data=csv_obj._get_data()#暂不使用字典格式
        self.content = []
        self.to_deal = []

    def _io_from_jydf(self,JYDF):#从交易对方获取交易类型
        
        #todo JYDF_LIST.dat可加入account 
        with open('JYDF_LIST.dat', 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if JYDF==row['JYDF']:return row['class']
        return 0

    def _get_statu(self,row):#获取交易状态与处理暂存区，
       pass
    
    def _last_deal(self,row):#无效交易的处理，
        pass

    def _frist_deal(self,row):#第一次处理条目
        pass

    def parse(self):#转换为统一的格式
        for row in self.orig_data:
            meta=self._frist_deal(row)#处理为统一格式
            if(meta!=0):
                self.content.append(meta)
        for row in self.to_deal:
            meta=self._last_deal(row)#处理为统一格式,处理to_deal
            if(meta!=0):
                self.content.append(meta)
        return self.content

    def run(self):#运行导入，导入原始账单与合并账单
        #alipay.import_data(self.orig_data)#导入原始账单
        
        self.parse()
        
        alipay=sheet('tt.xlsx',self.acc.name,start_row=5,end_row=7)
        alipay.import_data_from_csv(self.csv_obj)

        alipay=sheet('tt.xlsx','all',start_row=0,end_row=0)
        alipay.insert_rows(2,self.content)
        alipay.wb.save(alipay.file_name)#保存数据

class AliPayimpoter(impoter):
    def _get_statu(self,row):#获取交易状态与处理暂存区，
        #就没付款
        if row[11] == '交易关闭' and row[15] == '':
            return '已废'
        #只是冻结，没花钱
        elif row[11] == '冻结成功':
            return '已废'
        #列表里没有
        elif row[11] == '交易关闭' and row[15] == '已支出':
            self.to_deal.append(row)#加入to_deal
            return 0
        elif row[11] == '退款成功' and row[15] == '已收入':
            self.to_deal.append(row)#加入to_deal
            return 0
        else:
            return '有效'
    
    def _last_deal(self,row):#无效交易的处理，
        item=['','','','','','','','','','']
        #匹配退款账单并使其无效
        item[7]=  '待处理'
        if(row[0]==''):#递归调用时
            item[7]= '已废'
        for i in range(len(self.to_deal)):##匹配列表并处理关联项
            if(self.to_deal[i][0]==row[0]):#不与自己匹配
                    continue
            elif(self.to_deal[i][0]==row[0].split('_')[0]):#退款匹配到了
                if (row[11] == '交易关闭' and row[15] == '已支出')\
                    or (row[11] == '退款成功' and row[15] == '已收入'):
                    if self.to_deal[i][9]==self.to_deal[i][13]:
                        ta=self.to_deal[i]
                        self.to_deal.remove(self.to_deal[i])#删除对方
                        for ii in range(len(self.to_deal)):#删除自己
                            if(self.to_deal[ii][0]==row[0]):
                                self.to_deal.remove(self.to_deal[ii])  
                                break 
                        ta[0]=''
                        self.content.append(self._last_deal(ta))#处理对方  
                        item[7]= '已废'
                        break

        #交易时间
        item[0] = row[3]
        if item[0] == '':
            item[0] = row[2]
        #金额（元）
        item[2] = float( row[9].strip('¥'))
        #收/支  
        if item[7]=='已废':
            item[3]=''   
        elif row[10] == '' :
            if row[15]== '资金转移':
                item[3]= '转移'
            elif  '余额宝' in row[8] and '收益发放' in row[8]:
                item[3]= '收入'
            else:item[7]='待处理'
        elif row[10] == '支出' or row[10] == '收入':
            item[3]= row[10]
        else :item[7]='待处理'
            
        item[4]='AliPay'
        item[1]=row[7]+row[8]
        item[5]=''
        item[6]=''
        item[8]=''
        item[9]=''
        return item

    def _frist_deal(self,row):#第一次处理条目
        item=['','','','','','','','','','']
        #先获取账单状态，待处理则先不处理
        item[7]=self._get_statu(row)
        if(item[7]==0):#已加入to——deal 不必处理
            return 0
        #交易时间
        item[0] = row[3]
        if item[0] == '':
            item[0] = row[2]
        #金额（元）
        item[2] = float( row[9].strip('¥'))
        #收/支     
        if item[7]=='已废':
            item[3]=''   
        elif row[10] == '' :
            if row[15]== '资金转移':
                item[3]= '转移'
            elif  '余额宝' in row[8] and '收益发放' in row[8]:
                item[3]= '收入'
            else:#第一次处理时，未能处理的item
                self.to_deal.append(row)
                return 0       #已加入to——deal 不必处理
        elif row[10] == '支出' or row[10] == '收入':
            item[3]= row[10]
        else :#第一次处理时，未能处理的item
            self.to_deal.append(row)
            return 0#已加入to——deal 不必处理
            
        item[4]='AliPay'
        item[1]=row[7]+row[8]
        item[5]=''
        item[6]=''
        item[8]=''
        item[9]=''
        return item

class WeChatimpoter(impoter):
    def _get_statu(self,row):#获取交易状态与处理暂存区，
        #付款后又退款了,且无手续费
        if row[7] == '已全额退款':
            self.to_deal.append(row)#加入列表等待
            return 0
        else:
            return '有效'
    
    def _last_deal(self,row):#无效交易的处理，
        item=['','','','','','','','','','']
        #匹配退款账单并使其无效
        item[7]=  '待处理'
        if(row[8]==''):#递归调用时
            item[7]= '已废'
        else:
            for i in range(len(self.to_deal)):##匹配列表并处理关联项
                if(self.to_deal[i][8]==row[8]):#不与自己匹配
                        continue
                elif(self.to_deal[i][2]==row[2] and row[7] == '已全额退款'):#退款匹配到了
                    if (self.to_deal[i][4] == '收入' and row[4] == '支出')\
                        or (self.to_deal[i][4] == '支出' and row[4] == '收入'):
                        if self.to_deal[i][5]==row[5]:
                            ta=self.to_deal[i]
                            self.to_deal.remove(self.to_deal[i])#删除对方
                            for ii in range(len(self.to_deal)):#删除自己
                                if(self.to_deal[ii][0]==row[0]):
                                    self.to_deal.remove(self.to_deal[ii])  
                                    break 
                            ta[8]=''
                            self.content.append(self._last_deal(ta))#处理对方  
                            item[7]= '已废'
                            break
        #交易时间
        item[0] = row[0]
        #金额（元）
        item[2] =float( row[5].strip('¥'))
        #收/支  
        if item[7]=='已废':
            item[3]=''   
        elif row[4] == '/' :
            if row[1]== '零钱提现':
                item[3]= '转移'
            else:item[7]='待处理'
        elif row[4] == '支出' or row[4] == '收入':
            item[3]= row[4]
        else :
            item[7]='待处理'
            
        item[4]='WeChatPay'
        item[1]=row[2]+row[3]
        item[5]=''
        item[6]=''
        item[8]=''
        item[9]=''
        return item

    def _frist_deal(self,row):#第一次处理条目
        item=['','','','','','','','','','']
        #先获取账单状态，待处理则先不处理
        item[7]=self._get_statu(row)
        if(item[7]==0): #已加入to——deal 不必处理
            return 0
        #交易时间
        item[0] = row[0]
        #金额（元）
        item[2] =float( row[5].strip('¥'))
        #收/支   
        #print(self.orig_data) 
        if item[7]=='已废':
            item[3]='' 
             
        elif row[4] == '/' :
            if row[1]== '零钱提现':
                item[3]= '转移'
            else:#第一次处理时，未能处理的item
                self.to_deal.append(row)
                return 0       #已加入to——deal 不必处理
        elif row[4] == '支出' or row[4] == '收入':
            item[3]= row[4]
        else :
            item[7]='待处理'
            
        item[4]='WeChatPay'
        item[1]=row[2]+row[3]
        item[5]=''
        item[6]=''
        item[8]=''
        item[9]=''
        return item

class ICBCimpoter(impoter):
    def _get_statu(self,row):#获取交易状态与处理暂存区，
        #就没付款
        if row[2].split('-')[0] == '财付通' or row[2].split('-')[0] == '支付宝':
                if row[2] == '充值' and row[2]== '微信零钱提现':
                    return '有效'
                    jy_type= '转移'
                else:
                    return 0
            #退款
        if row[1] == '退款' :
            self.to_deal.append(row)#加入列表等待匹配删除
            return 0
        else:
            return '有效'
    
    def _last_deal(self,row):#无效交易的处理，
        item=['','','','','','','','','','']
        #匹配退款账单并使其无效
        item[7]=  '待处理'
        ##处理几个关于退款的待处理，有几个退款不能匹配
        if row[1]=='退款':
            for i in range(len(self.content)):##匹配列表并处理关联项
                if(self.content[i][1].split('@')[0]==row[2]):#找到对方
                    self.content[i][7]='已废'
                    item[7]='已废'
        #交易时间
        item[0] = row[0]
        #金额（元）
        if row[8]=='':
            item[2] = float(row[9].strip('¥').replace(',','') )
        elif  row[9]=='':
            item[2] = float(row[8].strip('¥').replace(',','') )
        
        #收/支  
        if item[7]=='已废':
            item[3]=''
        if row[2] == '充值' and row[2]== '微信零钱提现':
            item[3]= '转移'
        elif row[8]=='':
            item[3]= '支出'
        elif  row[9]=='':
            item[3]= '收入'
        else :
            self.to_deal.append(row)
            return 0
            
        item[4]='ICBC'+row[2].split('-')[0]
        item[1]=row[2]+'@'+row[3]
        item[5]=''
        item[6]=''
        item[8]=''
        item[9]=''
        return item

    def _frist_deal(self,row):#第一次处理条目
        item=['','','','','','','','','','']
        #先获取账单状态，待处理则先不处理
        item[7]=self._get_statu(row)
        if(item[7]==0): #已加入to——deal 不必处理
            return 0
        #交易时间
        item[0] = row[0]
        #金额（元）
        if row[8]=='':
            item[2] = float(row[9].strip('¥').replace(',','') )
        elif  row[9]=='':
            item[2] = float(row[8].strip('¥').replace(',','') )
        
        #收/支  
        if item[7]=='已废':
            item[3]=''
        if row[2] == '充值' and row[2]== '微信零钱提现':
            item[3]= '转移'
        elif row[8]=='':
            item[3]= '支出'
        elif  row[9]=='':
            item[3]= '收入'
        else :
            self.to_deal.append(row)
            return 0
            
        item[4]='ICBC'+row[2].split('-')[0]
        item[1]=row[2]+'@'+row[3]
        item[5]=''
        item[6]=''
        item[8]=''
        item[9]=''
        return item

if __name__ =="__main__":
    import os
    file=home+"/tt.xlsx"
    if  os.path.isfile(file):
        os.remove(file)

    alipay=sheet('tt.xlsx','all',start_row=0,end_row=0)
    alipay.insert_row(1,['交易时间'	,'交易详情','金额（元）','收/支','交易平台','交易类型','预算归属','交易状态' ,'来源\去向','备注'])
    alipay.wb.save(file)#保存数据

    alipay=account(home+"/data/temp/alipay_record_20210404_1059_1.csv",'Alipay',5,7)
    a=AliPayimpoter(alipay)
    a.run()

    wechat=account(home+"/data/temp/微信支付账单(20210301-20210401).csv",'WechatPay',start_row=17,endrow=0,encoding='UTF-8')
    a=WeChatimpoter(wechat)
    a.run()

    icbc=account(home+"/data/temp/hisdetail1617505513900.csv",'icbc',start_row=7,endrow=2,encoding='UTF-8')
    a=ICBCimpoter(icbc)
    a.run()
    