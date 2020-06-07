from urllib import request
from bs4 import BeautifulSoup
import time,csv,sys,io,json,requests,os,re,numpy as np
import pandas as pd

headers = {'user-agent':'https://www.104.com.tw/jobs/search/?ro=0&keyword=python&order=1&asc=0&page=1&mode=s&jobsource=2018indexpoc'}
headers2= {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
url_1 = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=python&order=15&asc=0&page='
url_2 = '&mode=s&jobsource=2018indexpoc'


empty_column=[]
job_datas=[]
num_tool=[]
for page in range(150):
    url = url_1+str(page)+url_2
    req = request.Request(url=url,headers=headers)
    res  = request.urlopen(req)
    soup = BeautifulSoup(res.read(),'lxml')
    title = soup.find_all('article',class_='js-job-item')

    for job in title:
        try  :
            company_name = job.get('data-cust-name')  #公司名稱
            job_name = job.get('data-job-name')  #職缺內容
            need_skill = job.find_all('p',class_='job-list-item__info')[0].text #所需技能
            link = job.find('a').get('href').replace('//','')

            new_url = 'https://www.104.com.tw/job/ajax/content/' + str((link.split('/')[2].split('?')[0]))
            new_header = {'Referer':'https://www.104.com.tw/job/63z79',
                    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}


            tool=[]
            new_req = requests.get(url=new_url,headers=new_header)
            json_data = json.loads(new_req.text)
            x = json_data['data']['condition']['specialty']
            for i in range(len(x)):
                tool.append(x[i]['description'])
                empty_column = empty_column + tool
                new_column =list(set(empty_column))

            num_tool.append(tool)
            # print('============================')
            # print(new_column)
            # s = pd.DataFrame(np.zeros(5*len(new_column)).reshape((5, len(new_column))),columns=list(new_column))

            data={'公司名稱':company_name,'職缺內容':job_name,'所需技能':need_skill,'職缺網址':link,'擅長工具':tool}
            job_datas.append(data)
        except UnicodeEncodeError:
            continue
        except IndexError:
            continue
        time.sleep(3)
    time.sleep(10)


skill_list = pd.DataFrame(np.zeros(len(num_tool)*len(new_column)).reshape((len(num_tool), len(new_column))),columns=list(new_column))
print(skill_list)
# # print(type(num_tool[3][1])) #<class 'str'>
# print(list(skill_list.iloc[1])) #<class 'numpy.float64'>
for i in range(len(num_tool)):
    for j in range(len(num_tool[i])):
        if num_tool[i][j] in skill_list.columns:
                location = skill_list.columns.get_loc(num_tool[i][j])
                skill_list.iloc[i,location] = 1
        else :
                continue
skill_list.to_csv("skill.csv",index=None,encoding='utf-8-sig')

csvFile = '104.csv'
columns = ['公司名稱', '職缺內容', '所需技能','職缺網址','擅長工具']
#print(job_datas)
df_test = pd.DataFrame(job_datas)
df_test.to_csv(csvFile, header=columns,index=None, encoding='utf-8-sig')

#with open(csvFile,'w+',newline='',encoding='utf-8-sig',errors='ignore' ) as csvFile:
#    dictWriter = csv.DictWriter(csvFile,fieldnames=columns)            #定義寫入器
#    dictWriter.writeheader()
#    for data in job_datas:
#        dictWriter.writerow(data)

df1 = pd.read_csv('skill.csv',encoding='utf-8-sig')
df2 = pd.read_csv('104.csv',encoding='utf-8-sig')

df = pd.concat([df2,df1],axis=1)
df.to_csv('final_104.csv', index=None, encoding='utf-8-sig')








