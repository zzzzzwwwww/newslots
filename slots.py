#!/usr/bin/env python
import random
from itertools import *
from themeconf import *


def get_pay_table(themeid):
    return THEME_CONFIG[themeid]['pay']

def get_lines(themeid):
    return ALLLINES[themeid]

def get_reels(themeid,freespin):
    if freespin==4:
        return THEME_CONFIG[themeid]['reels_B']
    if freespin==3:
        return THEME_CONFIG[themeid]['reels_H']
    if freespin==2:
        return THEME_CONFIG[themeid]['reels_W']
    return THEME_CONFIG[themeid]['reels_F'] if freespin else THEME_CONFIG[themeid]['reels_N']

def random_reels(themeid,freespin=0):
    ret = []
    reels = get_reels(themeid,freespin)
    i=0
    for l in THEME_CONFIG[themeid]['rows']:
        idx = random.randint(0,len(reels[i])-1)
        if idx+l<=len(reels[i]):
            ret.append(reels[i][idx:idx+l])
        else:
            ret.append((reels[i]+reels[i])[idx:idx+l])
        i+=1
    return ret

import copy
zeus_bonus = {}
zeus_bonus_time = 0
def spin_core(themeid,freespin,linecount):
    global zeus_bonus
    global zeus_bonus_time
    paytable=get_pay_table(themeid)
    itemlist1=random_reels(themeid,freespin)
    curlines = get_lines(themeid)
    resultlist = []
    bonus = 0
    sumreward = 0
    scatter = 0
    five=six=0
    # how many columns
    cols = len(THEME_CONFIG[themeid]['rows'])
    itemlist=copy.deepcopy(itemlist1)

    if freespin==4:
        if themeid==ZEUS_THEME:
            for k,v in zeus_bonus.items():
                itemlist[k[0]][k[1]]=v
            for i in range(len(itemlist)):
                for j in range(len(itemlist[i])):
                    k=random.random()
                    if (i,j) not in zeus_bonus:
                        if itemlist[i][j]>3 and k<THEME_CONFIG[ZEUS_THEME]['bonus_game'][0]:
                            itemlist[i][j]=zeus_bonus[(i,j)]=3
                        elif itemlist[i][j]==3 and k<THEME_CONFIG[ZEUS_THEME]['bonus_game'][1]:
                            itemlist[i][j]=zeus_bonus[(i,j)]=2
                        elif itemlist[i][j]==2:
                            s=0
                            for i in range(4):
                                s+=THEME_CONFIG[ZEUS_THEME]['bonus_game'][2+i]
                                if s>=k:
                                    itemlist[i][j]=zeus_bonus[(i,j)]=-2-i
                                    break
            zeus_bonus_time+=1
            if zeus_bonus_time==THEME_CONFIG[ZEUS_THEME]['pay'][0][2]:
                zeus_bonus_time=0
                zeus_bonus=dict()
    elif freespin==1:
        if themeid==ZEUS_THEME:
            flag=0
            for j in range(5):
                if random.random()<THEME_CONFIG[themeid]['free_spin'][0][j]:
                    flag=1
                    for i in range(3):
                        k=random.randint(1,5)
                        itemlist[j][i]=-k if k>1 else 2
            if not flag:
                s=0
                k=random.random()
                for j in range(5):
                    s+=THEME_CONFIG[themeid]['free_spin'][1][j]
                    if s>=k:
                        for i in range(3):
                            k=random.randint(1,5)
                            itemlist[j][i]=-k if k>1 else 2
                        break
    for i in range(linecount):
        last_k = 2
        bonus = 0
        longest_length = -1
        longest_id = 0
        longest_wild=0
        zeus_wild=1
        for j in range(cols):
            k = itemlist[j][curlines[i][j]]
            # -2 -3 -4 -5
            if themeid==ZEUS_THEME and k<0:
                zeus_wild*=-k
                k=2
            if last_k==2 and k>2:
                last_k = k
            if last_k==k or k==2:
                if last_k>2 and j+1>longest_length:
                    longest_length = j+1
                    longest_id = last_k
                if k==last_k==2:
                    longest_wild = j+1
            else:
                last_k = -1
        reward = 0
        if longest_id>0:
            longest_length=min(longest_length,len(paytable[longest_id]))
            if paytable[longest_id][longest_length-1]>0:
                resultlist.append([i,longest_length])
            reward = paytable[longest_id][longest_length-1]
            if longest_length==5: five=1
            if longest_length==6: six=1
        if longest_wild>0:
            longest_length=longest_wild
            longest_length=min(longest_length,len(paytable[3]))
            reward = max(reward,paytable[3][longest_length-1])
            if themeid==ZEUS_THEME:
                reward*=zeus_wild

        sumreward += reward
    bonus = sum(j.count(0) for j in itemlist)
    scatter = sum(j.count(1) for j in itemlist)
    if bonus>=3 and scatter>=3:
        print themeid, itemlist
        exit('both bonus and scatter')
    return [itemlist,resultlist,sumreward,bonus,scatter, five, six]
def find_add(conf, to_add, k):
    for i, v in enumerate(conf):
        if k>=v:
            to_add[i]+=1

SPINTYPE=["normal spin", "free spin", "wild spin", 'high_spin', 'bonus_spin']
def spin_result(themeid,freespin,run_times=10000):
    linecount=len(ALLLINES[themeid])
    total_cost=run_times*linecount
    totalwin=max_reward=scatter_times=bonus_times=win_times=0
    bigwin=megawin=superwin=0
    five=six=0
    allwins=[]
    fspin=t_fspin=fspin_coins=0
    bspin=t_bspin=bspin_coins=0
    items_count=[0]*len(THEME_CONFIG[themeid]['pay'])
    items_count1=[0]*len(THEME_CONFIG[themeid]['pay'])
    big_wins=[0]*len(BIG_WIN_REWARD)
    win_strip_times=[0]*len(WIN_STRIP_TIMES)
    win_strip_count=0
    win_strip_winning=[0]*len(WIN_STRIP_WINNING)
    win_strip_win=0
    rows=THEME_CONFIG[themeid]['rows']
    pos_count=[[0]*r for r in rows]
    pos_count1=[0]*len(POSITION_COUNT)
    cnt=[[[0]*_ for _ in rows] for i in range(len(POSITION_COUNT))]
    for _ in range(run_times):
        ret=spin_core(themeid,freespin, linecount)
        win=ret[2]
        if ret[2]>0:
            win_times+=1
        if ret[-2]:
            five+=1
        if ret[-1]:
            six+=1
        if ret[3]>=3:
            bonus_times+=1
            if themeid==ZEUS_THEME:
                k=THEME_CONFIG[ZEUS_THEME]['pay'][0][ret[3]-1]
                a=[spin_core(themeid,4,linecount)[2] for f in range(k)]
                bspin+=1
                t_bspin+=k
                s=sum(a)
                bspin_coins+=s
                win+=s
        if ret[4]>=3:
            assert(freespin!=1)
            scatter_times+=1
            k=THEME_CONFIG[themeid]['pay'][1][ret[4]-1]
            a=[spin_core(themeid,1,linecount)[2] for f in range(k)]
            fspin+=1
            t_fspin+=k
            s=sum(a)
            fspin_coins+=s
            win+=s
        totalwin+=win
        find_add(BIG_WIN_REWARD, big_wins, win/linecount)
        max_reward=max(max_reward, win)
        allwins.append(win)
     #   allpos.append(ret[1])
        for c in ret[0]:
            for r in c:
                if r<0: r=2
                items_count[r]+=1
        vst=[[0]*r for r in rows]
        for line, longest in ret[1]:
            for col in range(longest):
                row=ALLLINES[themeid][line][col]
                if not vst[col][row]:
                    pos_count[col][row]+=1
                    items_count1[ret[0][col][row]]+=1
                    vst[col][row]=1
        for t in range(len(POSITION_COUNT)):
            vst=[[0]*_ for _ in rows]
            for line,longest in ret[1]:
                for col in range(longest):
                    row=ALLLINES[themeid][line][col]
                    if not vst[col][row]:
                        cnt[t][col][row]+=1
                        vst[col][row]=1
            if min(min(x) for x in cnt[t])>=POSITION_COUNT[t]:
                pos_count1[t]+=1
                cnt[t]=[[0]*_ for _ in rows]
    for win in allwins+[0]:
        if win:
            win_strip_count+=1
            win_strip_win+=win
        else:
            find_add(WIN_STRIP_TIMES, win_strip_times, win_strip_count)
            find_add(WIN_STRIP_WINNING, win_strip_winning, win_strip_win/linecount)
            win_strip_count=win_strip_win=0

    print '-----------theme %d: %s,  runtimes: %d------------------' %  (themeid, SPINTYPE[freespin], run_times)
    print 'max_reward/bet',  max_reward*1.0/linecount
    print 'scatter_times ratio: ', scatter_times*1.0/run_times,'bonus_times ratio: ', bonus_times*1.0/run_times
    print 'win_times/run_times: ', win_times*1.0/run_times, 'total_win/win_times: ', totalwin*1.0/win_times
    print 'bigwin, megawin, superwin', bigwin*1.0/run_times, megawin*1.0/run_times, superwin*1.0/run_times
    print 'five in line: ', five*1.0/run_times, ', six in line: ', six*1.0/run_times
    print 'total_win %d, total_cost %d, return rate %f' % (totalwin, total_cost, totalwin*1.0/total_cost)
    group= [(k, len(list(v))) for k, v in groupby(allwins, key=lambda x: x>0)]
    print 'max winning streak', max([v for k,v in group if k]+[0]),  ', max losing streak', max([v for k,v in group if not k]+[1])
    print 'free_spin :', fspin*10./run_times, t_fspin*1.0/run_times, fspin_coins*1.0/run_times
    print 'bonus_spin :', bspin*10./run_times, t_bspin*1.0/run_times, bspin_coins*1.0/run_times
    print 'items_count', map(lambda x: x*1.0/run_times, items_count)
    print 'items_count1', map(lambda x: x*1.0/run_times, items_count1)
    print 'big_win: ', map(lambda x: x*1.0/run_times, big_wins)
    print 'win_strip_times: ', map(lambda x: x*1.0/run_times, win_strip_times)
    print 'win_strip_winning: ', map(lambda x: x*1.0/run_times, win_strip_winning)
    print 'position_count: ', [map(lambda x: x*1.0/run_times, p) for p in pos_count]
    print 'position_count1: ', map(lambda x: x*1.0/run_times, pos_count1)
    return totalwin*1.0/total_cost
    #aver=totalwin*1.0/run_times
    #print 'fangcha', sum(map(lambda win: (win-aver)*(win-aver), allwins))/run_times
def check():
    for themeid in THEME_CONFIG.keys():
        for t in  ('reels_N', 'reels_F', 'reels_W', 'reels_H'):
            if 0 in THEME_CONFIG[themeid][t][0]+THEME_CONFIG[themeid][t][4]:
                print t,  THEME_CONFIG[themeid][t][0]+THEME_CONFIG[themeid][t][4]
                exit('0 in wrong column, theme %d' % themeid)
            if 1 in THEME_CONFIG[themeid][t][1]+THEME_CONFIG[themeid][t][3]:
                print t,THEME_CONFIG[themeid][t][1]+THEME_CONFIG[themeid][t][3]
                exit('1 in wrong column, theme %d' % themeid)
            for i in range(len(THEME_CONFIG[themeid]['rows'])):
                l = THEME_CONFIG[themeid]['rows'][i]
                x = THEME_CONFIG[themeid][t][i]
                last=-10000
                if 1:#themeid not in (2,3):
                    for i in range(len(x)*2):
                        checknums=(0,1)if themeid!=4 else (0,1,2)
                        if x[i%len(x)] in checknums:
                            if i-last<l:
                                print  t,  i, last, l, x
                                exit('theme %d, 0 1 in same column' % themeid)
                            last=i
                if t=='reel_W' and themeid==2 and i in (2,3,4):
                    for i in range(4,len(x)):
                        if x[i-4:i].count(-1)==0:
                            exit('theme 2 wild fail')
import traceback
if __name__=='__main__':
    from sys import argv, exc_info

    check()
    try:
        run_times=int(argv[1])
        themeids=map(int, argv[2:]) if len(argv)>2 else THEME_CONFIG.keys()
        for themeid in themeids:
            k=4 if themeid!=ZEUS_THEME else 5
            for i in range(k):
                spin_result(themeid,i,run_times=run_times)
    except Exception, e:
        print '|'.join(traceback.format_exception(e.__class__,e,exc_info()[2]))
        for themeid in THEME_CONFIG.keys():
            k=4 if themeid!=ZEUS_THEME else 5
            for i in range(k):
                spin_result(themeid,i)
