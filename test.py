from bs4 import BeautifulSoup
# from matplotlib.pyplot import title
soup = BeautifulSoup(open('./2.html',encoding='utf-8'), 'html.parser')
res=soup.table.children
# res=BeautifulSoup(table,'lxml')
# print(res)
# res.next
# for i in list(res)[1:]:
#     print(i)
# prilist(res))
res=[i for i in res if i!='\n']
# for i in res:
#     print(i.find_all(title='编辑'))
res=[i for i in res if i.find_all(title='编辑')]
print(res)


# print(res[2])
# print(res[2].find_all(title=''))
# r=BeautifulSoup(res[2],"html.parser")

    



