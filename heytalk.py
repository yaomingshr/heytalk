import numpy as np
import MySQLdb as mysql
from datetime import date,datetime
import math
from time import time
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
import random

conn = mysql.connect(host = '203.195.138.60',user='root',passwd='123456',port=3306)
#conn = mysql.connect(host = 'localhost',user='root',passwd = '1234',port=3306)
cur = conn.cursor()
conn.select_db("heytalkdb")

def pre_calc_score():
    cur = conn.cursor()
    count = cur.execute("select usi,discuss,transmit,time from saycontent")
    row_data = cur.fetchmany(count)
    result = []
    for i in row_data:
        delta = date.today() - i[-1].date()
        rec = [i[0],int(i[1]),int(i[2]),delta.days]
        result.append(rec)
    #[usi,discuss,transmit,days]
    return result

def pre_cluster():
#    conn.select_db("heytalk")
    cur = conn.cursor()
    user_count = cur.execute("select usi from user")
    raw_data = cur.fetchmany(user_count)
    usi_list = []
    for i in raw_data:
        usi_list.append(i[0])
    interest_count = cur.execute("select * from interest")
    beginid = 1011
    m_interest = np.zeros((user_count,interest_count))
    for i in range(0,len(usi_list)):
        count = cur.execute('select interestid from userinterest where usi = "%s"'%(usi_list[i]))
        ui_res = cur.fetchmany(count)
        for j in ui_res:
            m_interest[i,j[0]-beginid] = 1
    cat_list = [("shop",20),("video",20),("education",20),("news",30),("game",30),("music",500)]
    return usi_list,m_interest,cat_list
    
def ScoreLive(say_feature):
    scores = []
    sigma = 500
    weigh_disc = 1
    weigh_trans = 1
    upper_disc = 10
    upper_trans = 1000
    for r in say_feature:
        temp_score = math.exp(-r[3]/sigma)*(weigh_disc*min(r[1], upper_disc) + weigh_trans*min(r[2], upper_trans))
        say_score = [r[0], temp_score]
        scores.append(say_score)
    uni_usi_list = set(row[0] for row in say_feature)
    usi_score_live = dict()
    for usi in uni_usi_list:
        person_score = 0
        for say_score in scores:
            if say_score[0] == usi:
                person_score += say_score[1]
        usi_score_live[usi] = person_score
    return usi_score_live

def NormalData(mat_inter, cate_list):
    coef_norm = [];
    for r in cate_lsit:
        mat_inter()
        coef_norm.append(coef)




def InterestCluster(mat_inter, cate_list):
    para_K = 4
  #  mat_inter = NormalData(mat_inter = mat_inter, cate_list = cate_list)
    kmeans = KMeans(n_clusters=para_K, n_init=10)
    kmeans.fit(mat_inter)
    label = kmeans.predict(mat_inter)
    return label
'''
def ClusterRank(usi_list, label, usi_score_live):
    uni_label = set(label)
    usi_label = [usi_list, label]
    ranked_cluster = dict()
    for uni_l in uni_label:
        cluster_list = []
        for pair in usi_label:
            if pair[1]==uni_l:
                score_usi = dict()
                #score_usi(usi_score_live[pair[0]]) = pair[0]
                cluster_list.append(score_usi) 
        cluster_list.sort()
        randked_cluster[uni_l] = cluster_list
    return ranked_cluster
'''

def getRes(usi,usi_list,label,usi_score_live):
    #set usi_score_live to one column order by usi
    score_np = np.zeros((len(usi_list),))
    for i in usi_score_live.keys():
        temp = usi_list.index(i)
        score_np[temp] = usi_score_live[i]

    this_index = usi_list.index(usi)
    category = label[this_index]
    kindscore_list = []
    for i in range(0,len(usi_list)):
        if (i!=this_index and category==label[i]):
            kindscore_list.append((usi_list[i],score_np[i]))
    sorted_list = sorted(kindscore_list,key = lambda x : x[1],reverse = True)
    
    res = []
    for i in range(0,min(15,len(sorted_list))):
        res.append(sorted_list[i][0])
    return res



def NormOne(array_num):
    norm_coef =[float(1)/sum(array_num)]*len(array_num)
    array_num = np.array(array_num)
    if sum(array_num)!=0:
        array_num = array_num*np.array(norm_coef)
    return array_num


def CalcuCateRangeWei(cate_list, weight_cate):
 #   weight_cate = np.array(weight_cate)
 #   norm_coef = [1/sum(weight_cate)]*len(weight_cate)
 #   weight_cate = np.array(weight_cate)*np.array(norm_coef)
    weight_cate = NormOne(weight_cate)
    cate_range_wei = []
    start = 0
    i = 0
    for cate in cate_list:
        end = start + cate[1]-1
        cate_range_wei.append([start, end, weight_cate[i], 0, 0])
        start = end+1
        i += 1
    return cate_range_wei


def GeneShowDim(index, weight_cate, cate_list):
    cate_range_wei = CalcuCateRangeWei(cate_list = cate_list, weight_cate = weight_cate)
    cate_range_wei = np.array(cate_range_wei)
    index_cate = np.zeros(len(index))
    for nc in range(0, len(cate_list)):
        for nind in range(0, len(index)):
            if cate_range_wei[nc][0]<= index[nind]<=cate_range_wei[nc][1]:
                cate_range_wei[nc][3] +=1
                index_cate[nind] = nc
        if cate_range_wei[nc][3]!=0:
            cate_range_wei[nc][4] = cate_range_wei[nc][2]/cate_range_wei[nc][3]
    pred_wei = np.zeros(len(index))
    for nind in range(0, len(index_cate)):
        pred_wei[nind] = cate_range_wei[int(index_cate[nind])][4]
    pred_wei = NormOne(array_num = pred_wei)
    random_num = random.random()
    pred_sum = 0
    for nind in range(0, len(index)):
        pred_sum += pred_wei[nind]
        if pred_sum>=random_num:
            show_inter = index[nind]
            break
    return show_inter

def GetShowInform(mat_inter, usi_list, res, usi, cate_list):
    weight_cate = [6,5,4,3,2,1]
    res_feat = np.zeros( (len(res), len(mat_inter[0])) )
    for i in range(0, len(usi_list)):
        if usi_list[i]==usi:
            usi_feature = mat_inter[i]
        for j in range(0, len(res)):
            if usi_list[i] == res[j]:
                res_feat[j] = mat_inter[i]
    all_show_inter = []
    for i in range(0, len(res)):
        comm_inter = np.array(usi_feature)*np.array(res_feat[i])
        index = []
        for j in range(0, len(comm_inter)):
            if (comm_inter[j]!=0):
                index.append(j)
        if len(index)!=0:
            show_inter = GeneShowDim(index = index, weight_cate = weight_cate, cate_list = cate_list)
         #   show_inter = index[random.randint(0,len(index)-1)]
        else:
            show_inter = -1
        all_show_inter.append(show_inter)
    beginid = 1011
    info_res = [x+beginid for x in all_show_inter]
    return info_res


def getSimilar(usi):
    say_feature = pre_calc_score()
    usi_list,usi_feature,cate_list = pre_cluster()
    if usi not in usi_list:
        return (0,())
    usi_score_live  = ScoreLive(say_feature = say_feature)
    label = InterestCluster(mat_inter = usi_feature, cate_list = cate_list)
    similar_list = getRes(usi,usi_list,label,usi_score_live)
    show_inters = GetShowInform(mat_inter=usi_feature, usi_list=usi_list, res = similar_list, usi ='0', cate_list = cate_list)
    #part_res = []
    #for i in range(0,len(similar_list)):
    #    part_res.append(similar_list[i])
    #    part_res.append(str(show_inters[i]))
    #tPart = tuple(part_res)
    #final_res = (len(similar_list)*2,tPart)
    #return final_res
    dict_res = {}
    for i in range(0,len(similar_list)):
        dict_res[similar_list[i]] = show_inters[i]
    return dict_res;


def savetodb(usi_list):
    cur = conn.cursor()
    count = 1
    for one_user in usi_list:
        simi_dict = getSimilar(one_user)
        for simi_user in simi_dict.keys():
            cur.execute("insert into similar (usi,similaruser,cointerestid) values (%s,%s,%s);",(one_user,simi_user,simi_dict[simi_user]))
        print count
        count += 1
    conn.commit()
        
def filluser(usi_list):
    cur = conn.cursor()
    sex_list = [0,1]
    age_list = [x for x in range(17,34)]
    for user in usi_list:
        sex = random.choice(sex_list)
        age = random.choice(age_list)
        #print user
#        cur.execute("""update user set age = %s,sex = %s where usi = %s""",(age,sex,user))
        cur.execute("update user set status = 1")
    conn.commit()

if __name__== "__main__":
        usi_list,usi_feature,cate_list = pre_cluster()
        filluser(usi_list)
