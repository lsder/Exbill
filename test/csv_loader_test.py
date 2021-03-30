import sys
home='/'.join(sys.argv[0].split('/')[:-2])
sys.path.append(home) 
from src.tool import csv_loader
fil=csv_loader.csv_file(home+"/data/temp/alipay_record_20210103_1339_1.csv")

print(fil.row_count)
