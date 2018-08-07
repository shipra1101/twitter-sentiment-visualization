# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 22:51:57 2018

@author: deeks
"""

import matplotlib.pyplot as plt
import numpy as np

x = np.arange(5)
y = np.array([53,54,76,100,76])

plt.gca().set_color_cycle(['red', 'green', 'yellow'])

plt.plot(x,y)
plt.plot(x, 2 * y)
plt.plot(x, 3 * y)

plt.legend(['Positive', 'Negative', 'Nuetral'], loc='upper left')


plt.show()  


'mysql+pymysql://dk488492:sameera123@cloudupload.czlq7phghrul.us-east-2.rds.amazonaws.com/awsdb'

q='SELECT * FROM SEARCH_INFO WHERE SEARCH=\''+"twitter"+"\'" +" ORDER BY ID ASC"
result  = engine.execute(q).fetchall()

postive=[]
negative=[]
nuetral=[]

import numpy as np 
for row in result:
    postive.append(row[2])
    negative.append(row[3])
    nuetral.append(row[4])

pos=np.array(postive)
neg=np.array(negative)
neut=np.array(nuetral)   



plt.gca().set_color_cycle(['red', 'green', 'yellow'])

d = np.arange(len(pos))
e = np.arange(len(neg))
f = np.arange(len(neut))

plt.plot(d,pos)
plt.plot(e, neg)
plt.plot(f,neut)

plt.legend(['Positive', 'Negative', 'Nuetral'], loc='upper left')


plt.show() 
