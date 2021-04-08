from numba import njit, types, vectorize, prange
import numpy as np
import laspy
import time
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiPolygon ,Polygon
import os
# cd /d H:\Ender\retangle_shrinking
#import rectangles
rec=pd.read_csv('rectangles.csv')

# las=laspy.file.File('20200218_Icrisat1020.las')

@njit()
def shrink(i,step,threshold,xx,yy,zz,rec,results):
    flag=True
    flag2=True

    x1=rec[0]
    y1=rec[1]
    x2=rec[2]
    y2=rec[3]
    x3=rec[4]
    y3=rec[5]
    x4=rec[6]
    y4=rec[7]

    #y=mx+k, we need the line functions between points 1 2 3 4 (see relationship)
    m12=(y2-y1)/(x2-x1) 
    m34=(y3-y4)/(x3-x4) 
    m14=(y4-y1)/(x4-x1) 
    m23=(y3-y2)/(x3-x2)
    k12=y1-m12*x1
    k34=y4-m34*x4
    k14=y1-m14*x1
    k23=y2-m23*x2
    index14=yy>m14*xx+k14
    index23=yy<m23*xx+k23
    index_long=np.logical_and(index14,index23)
    old_height=878787

    n=0
    while flag == True:
                #left line:y=m(x-step*n)+k, 
        if x4+step*n>x1:
            flag2=False
            break
        indexl=yy<m34*(xx-step*n)+k34
        indexr=yy>m34*(xx-step*(n+1))+k34
        index_short=np.logical_and(indexl,indexr)
        indexx=np.logical_and(index_short,index_long)
        try:
            # new_height=np.mean(zz[indexx])
            new_height=np.median(zz[indexx])
            # new_height=np.quantile(zz[indexx],0.3)
            if new_height-old_height<threshold:
                old_height=new_height
                n=n+1
            else:
                rec_x3=x3+step*n
                rec_y3=m23*rec_x3+k23
                rec_x4=x4+step*n
                rec_y4=m14*rec_x4+k14
                results[6][i]=rec_x4
                results[7][i]=rec_y4
                results[4][i]=rec_x3
                results[5][i]=rec_y3
                flag=False
        except:
            n=n+1
    n=0
    old_height=87878787

    while flag == False:
        #right line:y=m(x+step*n)+k, 
        if x1-step*n<x4:
            flag2=False
            break
        indexl=yy<m12*(xx+step*(n+1))+k12
        indexr=yy>m12*(xx+step*n)+k12
        index_short=np.logical_and(indexl,indexr)
        indexx=np.logical_and(index_short,index_long)
        try:
            # new_height=np.mean(zz[indexx])
            new_height=np.median(zz[indexx])
            # new_height=np.quantile(zz[indexx],0.3)

        except:
            n=n+1
            continue
        if new_height-old_height<threshold:
            old_height=new_height
            n=n+1
        else:
            rec_x1=x1-step*n
            rec_y1=m14*rec_x1+k14
            rec_x2=x2-step*n
            rec_y2=m23*rec_x2+k23
            results[2][i]=rec_x2
            results[3][i]=rec_y2
            results[0][i]=rec_x1
            results[1][i]=rec_y1
            flag=True

    if flag2==False: #only when it moves more than one rectangle
        results[2][i]=x2
        results[3][i]=y2
        results[0][i]=x1
        results[1][i]=y1
        results[6][i]=x4
        results[7][i]=y4
        results[4][i]=x3
        results[5][i]=y3
        print(i)

def create_shp(rec,fname):
    p_lsit=[]
    for i in range(len(rec['x1'])):
        p_lsit.append(Polygon([(rec['x1'][i],rec['y1'][i]),(rec['x2'][i],rec['y2'][i]),(rec['x3'][i],rec['y3'][i]),(rec['x4'][i],rec['y4'][i])]))
    shp=MultiPolygon(p_lsit)
    features=[i for i in range(len(rec['x1']))] # shp ID=0-49
    f=gpd.GeoDataFrame({'feature':features,'geometry':shp})
    f.to_file(fname)
# @njit()
def __main__():
    results=np.full((8,200),-1.0)
    las=laspy.file.File('20200218_Icrisat1020.las')
    xx=las.x
    yy=las.y
    zz=las.z
    for i in prange(0,200,4):
        a=np.array([rec['x1'][i],rec['y1'][i],rec['x2'][i],rec['y2'][i],rec['x3'][i],rec['y3'][i],rec['x4'][i],rec['y4'][i]])
        # print(a)
        shrink(i,0.08,thresholds[j],xx,yy,zz,a,results)
    result=dict()
    result['x1']=results[0]
    result['y1']=results[1]
    result['x2']=results[2]
    result['y2']=results[3]
    result['x3']=results[4]
    result['y3']=results[5]
    result['x4']=results[6]
    result['y4']=results[7]
    df=pd.DataFrame(result)
    # df.to_csv('median_008_10cm.csv')
    fname=f'./result/0_200_raw/median_008_{str(names[j])}cm.shp'
    # print(fname)
    create_shp(result,fname)
start=time.time()
thresholds=[0.1,0.2,0.3,0.4,0.5]
names=[10,20,30,40,50]
for j in range(5):
    __main__()


endd=time.time()
print(endd-start)

