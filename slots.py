#!/usr/bin/env python
import random
from itertools import *
from themeconf import *

def ninja_get_row_lines(freespin):
    if freespin=='reels_F':
        return LINES44433,(4,4,4,3,3)
    if freespin.startswith('reels_B'):
        return LINES1, (3,3,3,3,3)
    return LINES33444, (3,3,4,4,4)

def get_pay_table(themeid):
    return THEME_CONFIG[themeid]['pay']

def get_lines(themeid):
    return ALLLINES[themeid]

def random_reels(themeid,freespin,rows):
    ret = []
    reels = THEME_CONFIG[themeid][freespin]
    i=0
    for l in rows:
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
witch_jackpot=0
witch_total_jackpot=0
buffalo_scatter=0
def get_by_pro(p):
    r=random.random()
    for k,v in enumerate(p):
        if r<v:
            return k
    #error
    exit('get_by_pro')
def spin_core(themeid,freespin,linecount):
    global zeus_bonus
    global zeus_bonus_time
    global witch_jackpot

    if themeid!=NINJA_THEME:
        curlines,rows=ALLLINES[themeid],THEME_CONFIG[themeid]['rows']
    else:
        curlines,rows=ninja_get_row_lines(freespin)

    paytable=get_pay_table(themeid)
    itemlist1=random_reels(themeid,freespin,rows)
    
    resultlist = []
    bonus = 0
    sumreward = 0
    scatter = 0
    five=six=0
    # how many columns
    cols = len(itemlist1)
    if themeid==ZEUS_THEME:
        itemlist=copy.deepcopy(itemlist1)
    else: 
        itemlist=[map(lambda x:x-1, k) for k in itemlist1]
        if themeid==WITCH_THEME: itemlist=[[y if y!=4 else 2 for y in x] for x in itemlist]
        elif themeid==NINJA_THEME:itemlist=[[y-1 if y in (5,7) else y for y in x] for x in itemlist] #big change into normal
    if themeid==NINJA_THEME:
        if freespin in ('reels_N', 'reels_M', 'reels_H'):
            if itemlist[0][1]==6:
                    itemlist[0]=itemlist[1]=[6]*3
            elif itemlist[0][0]==6 or itemlist[0][2]==6:
                if random.random()<0.5:
                    itemlist[0][1]=itemlist[1][1]=6
        elif freespin=='reels_B_whole_column':
            r=random.random()
            for i in range(5):
                r-=THEME_CONFIG[themeid]['BONUS_SPIN_COLUMN'][i]
                if r<0:
                    itemlist[i]=[2]*3
                    break
        elif freespin=='reels_B_random_item':
            r=random.random()
            x=THEME_CONFIG[themeid]['BONUS_SPIN_ITEM']
            for i in range(len(x)):
                r-=k[i]
                if r<0:
                    k=i
                    cnt=0
                    left=[]
                    for i in range(3):
                        for j in range(3):
                            if itemlist[i][j]==k:
                                itemlist[i][j]=2
                                cnt+=1
                            elif itemlist[i][j]!=2:
                                left.append((i,j))
                    if cnt<3:
                        cnt=3-cnt
                        for i,j in random.sample(left,cnt):
                            itemlist[i][j]=k
                    break
        elif freespin=='reels_B_most_item':
            cnt=[0]*20
            for i in range(3):
                for j in range(3):
                    cnt[itemlist[i][j]]+=1
            k=cnt.index(max(cnt))
            for i in range(3):
                for j in range(3):
                    if itemlist[i][j]==k:
                        itemlist[i][j]=2
        

    if freespin=='reels_B':
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
    elif freespin=='reels_F':
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
        elif themeid==WITCH_THEME:
            for col in range(len(itemlist)):
                if 2 in itemlist[col]:
                    itemlist[col]=[2]*4
        elif themeid==BUFFALO_THEME:
            global buffalo_scatter
            for k in range(THEME_CONFIG[themeid]['bonus_spin_buffalo_time'][buffalo_scatter-1]):
                for i in range(len(itemlist)):
                    for j in range(len(itemlist[i])):
                        if itemlist[i][j]!=4 and random.random()<THEME_CONFIG[themeid]['bonus_spin'][k][i*len(itemlist[i])+j]:
                            itemlist[i][j]=4
        elif themeid==NINJA_THEME:
            if itemlist[0][1]==4 or itemlist[0][2]==4:
                itemlist[0]=itemlist[1]=[4]*4
            elif itemlist[0][0]==4 or itemlist[0][3]==4: #big super ninja
                k=random.randint(1,3)
                if k==3:
                    itemlist[0][1]=itemlist[0][2]=itemlist[1][1]=itemlist[1][2]=itemlist[2][1]=itemlist[2][2]=4
                elif k==2:
                    k=1 if itemlist[0][0]==4 else 2
                    itemlist[0][k]=itemlist[1][k]=itemlist[2][k]=4
            


    elif freespin=='reels_W':
            if themeid==WITCH_THEME:
                for row in range(len(itemlist[2])):
                    if itemlist[2][row]==3:
                        itemlist[2][row]=2
                        for col in (0,1,3,4):
                            p=THEME_CONFIG[themeid]['magic'][col]
                            for row in range(len(itemlist[col])):
                                if random.random()<p:
                                    itemlist[col][row]=2
            elif themeid==BUFFALO_THEME:
                change=get_by_pro(THEME_CONFIG[themeid]['change'])
                for i in range(len(itemlist)):
                    for j in range(len(itemlist[i])):
                        if itemlist[i][j]==3:
                            itemlist[i][j]=change

    elif freespin=='reels_N':
        if themeid==WITCH_THEME:
            if witch_jackpot:
                for col in range(len(itemlist)):
                    if random.random()<THEME_CONFIG[WITCH_THEME]['jackpot'][col]:
                        for row in range(len(itemlist[col])):
                            if itemlist[col][row]==1:
                                itemlist[col][row]=-1
                                break
                        else:
                            itemlist[col][0]=-1
        
    elif freespin=='reels_H':
        if themeid==WITCH_THEME:
            if witch_jackpot:
                for col in range(5):
                    if random.random()<THEME_CONFIG[WITCH_THEME]['jackpot'][col]:
                        for row in range(len(itemlist[col])):
                            if itemlist[col][row]==1:
                                itemlist[col][row]=-1
                                break
                        else:
                            itemlist[col][0]=-1




    for i in range(linecount):
        last_k = 2
        bonus = 0
        longest_length = -1
        longest_id = 0
        longest_wild=0
        zeus_wild=1
        for j in range(cols):
            try:
                k = itemlist[j][curlines[i][j]]
            except:
                print itemlist,freespin, j, cols, curlines
                exit()
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
            elif longest_length==6: six=1
        if longest_wild>0:
            longest_length=longest_wild
            longest_length=min(longest_length,len(paytable[2]))
            reward = max(reward,paytable[2][longest_length-1])
            if themeid==ZEUS_THEME:
                reward*=zeus_wild

        sumreward += reward
    bonus = sum(j.count(0) for j in itemlist)
    scatter = sum(j.count(1) for j in itemlist)
    if bonus>=3 and scatter>=3:
        print themeid, itemlist
        exit('both bonus and scatter')

    #there is bonus spin in buffalo, no scatter
    if themeid==BUFFALO_THEME:
        bonus,scatter=0,bonus
    elif themeid==NINJA_THEME:
        prescatter=sum(j.count(3) for j in itemlist)
        bonus+=prescatter
        scatter+=prescatter
    return [itemlist,resultlist,sumreward,bonus,scatter, five, six]

def find_add(conf, to_add, k):
    for i, v in enumerate(conf):
        if k>=v:
            to_add[i]+=1

def spin_result(themeid,freespin,run_times=10000):
    if themeid!=NINJA_THEME:
        lines=ALLLINES[themeid]
        linecount=len(lines)
        rows=THEME_CONFIG[themeid]['rows']
    else:
        lines,rows=ninja_get_row_lines(freespin)
        linecount=len(lines)
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
    
    pos_count=[[0]*r for r in rows]
    pos_count1=[0]*len(POSITION_COUNT)
    cnt=[[[0]*_ for _ in rows] for i in range(len(POSITION_COUNT))]
    global witch_jackpot
    global witch_total_jackpot

    if themeid==BUFFALO_THEME:
        buffalo=[0]*5
        buffalo_jackpot=0
    elif themeid==WITCH_THEME:
        if witch_jackpot:
            get_jackpot=0
            get_jackpot_time=[0,0,0]
    for _ in range(run_times):
        ret=spin_core(themeid,freespin, linecount)
        win=ret[2]

        if themeid==BUFFALO_THEME:
            global buffalo_scatter
            buffalo_scatter=3
            b=sum(j.count(4) for j in ret[0])
            if b>=11:
                if b>15: b=15
                buffalo[b-11]+=1
                j=THEME_CONFIG[themeid]['jackpot'][b-11]*linecount
                buffalo_jackpot+=j
                win=j


        if witch_jackpot:
            witch_total_jackpot+=linecount*0.01
            jackpotcnt=sum(j.count(-1) for j in ret[0])
            if jackpotcnt>=3:
                j=linecount*THEME_CONFIG[WITCH_THEME]['pay'][0][jackpotcnt-1]+witch_total_jackpot
                get_jackpot+=j
                get_jackpot_time[jackpotcnt-3]+=1
                win+=j
                witch_total_jackpot=0
        if ret[2]>0:
            win_times+=1
        if ret[5]:
            five+=1
        if ret[6]:
            six+=1
        if ret[3]>=3:
            bonus_times+=1
            if themeid in (ZEUS_THEME, NINJA_THEME):
                k=THEME_CONFIG[themeid]['pay'][0][ret[3]-1]
                a=[spin_core(themeid,'reels_B',linecount)[2] for f in range(k)] if themeid==ZEUS_THEME else [spin_core(themeid,'reels_B_whole_column',linecount)[2] for f in range(k)] 
                bspin+=1
                t_bspin+=k
                s=sum(a)
                bspin_coins+=s
                win+=s
        if ret[4]>=3:
            assert(freespin!='reels_F')
            scatter_times+=1
            global buffalo_scatter
            k=THEME_CONFIG[themeid]['pay'][1][min(ret[4],5)-1]
            buffalo_scatter=ret[4]
            s=0
            for _ in range(k):
                tmp=spin_core(themeid,'reels_F',linecount)
                if themeid==BUFFALO_THEME:
                    b=sum(j.count(4) for j in tmp[0])
                    if b>=11:
                        buffalo[b-11]+=1
                        j=THEME_CONFIG[themeid]['jackpot'][b-11]*linecount
                        buffalo_jackpot+=j
                        s+=j
                    else:
                        s+=ret[2]
                else:
                    s+=ret[2]
	        buffalo_scatter=0
            fspin+=1
            t_fspin+=k
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
                row=lines[line][col]
                if not vst[col][row]:
                    pos_count[col][row]+=1
                    items_count1[ret[0][col][row]]+=1
                    vst[col][row]=1
        for t in range(len(POSITION_COUNT)):
            vst=[[0]*_ for _ in rows]
            for line,longest in ret[1]:
                for col in range(longest):
                    row=lines[line][col]
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


    print '-----------theme %d: %s,  runtimes: %d, win_times %d------------------' %  (themeid, freespin, run_times,win_times)
    print 'max_reward/bet',  max_reward*1.0/linecount
    print 'scatter_times ratio: ', scatter_times*1.0/run_times,'bonus_times ratio: ', bonus_times*1.0/run_times
    print 'win_times/run_times: ', win_times*1.0/run_times, 'total_win/win_times: ', totalwin*1.0/win_times
    #print 'bigwin, megawin, superwin', bigwin*1.0/run_times, megawin*1.0/run_times, superwin*1.0/run_times
    print 'five in line: ', five*1.0/run_times, ', six in line: ', six*1.0/run_times
    print 'total_win %d, total_cost %d, return rate %f' % (totalwin, total_cost, totalwin*1.0/total_cost)
    group= [(k, len(list(v))) for k, v in groupby(allwins, key=lambda x: x>0)]
    print 'max winning streak', max([v for k,v in group if k]+[0]),  ', max losing streak', max([v for k,v in group if not k]+[1])
    print 'free_spin :', fspin*1./run_times, t_fspin*1./run_times, fspin_coins*1./run_times
    print 'bonus_spin :', bspin*1./run_times, t_bspin*1./run_times, bspin_coins*1./run_times
    print 'items_count', map(lambda x: x*1.0/run_times, items_count)
    print 'items_count1', map(lambda x: x*1.0/run_times, items_count1)
    print 'big_win: ', map(lambda x: x*1.0/run_times, big_wins)
    print 'win_strip_times: ', map(lambda x: x*1.0/run_times, win_strip_times)
    print 'win_strip_winning: ', map(lambda x: x*1.0/run_times, win_strip_winning)
    print 'position_count: ', [map(lambda x: x*1.0/run_times, p) for p in pos_count]
    print 'position_count1: ', map(lambda x: x*1.0/run_times, pos_count1)

    

    if themeid==BUFFALO_THEME:
        print 'buffalo>=11: ', buffalo, ' in ', run_times, ' spins ', ' total_bet: ', linecount*run_times, ' win_jackpot:', buffalo_jackpot

    if witch_jackpot:
        print 'witch total jackpot: ', get_jackpot, 'get jackpot times: ', get_jackpot_time, ' in ', run_times, ' spins ', ' total_bet: ', linecount*run_times
    return totalwin*1.0/total_cost

    #aver=totalwin*1.0/run_times
    #print 'fangcha', sum(map(lambda win: (win-aver)*(win-aver), allwins))/run_times
def check():
    for themeid in THEME_CONFIG.keys():
        bonus,scatter=1,2 if themeid!=ZEUS_THEME else 0,1
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
                        checknums=(0,1)
                        if x[i%len(x)] in checknums:
                            if i-last<l:
                                print  t,  i, last, l, x
                                exit('theme %d, 0 1 in same column' % themeid)
                            last=i
                '''if t=='reels_W':
                    for i in range(4,len(x)):
                        if x[i-4:i].count(-1)==0:
                            exit('theme 2 wild fail')'''
import traceback
if __name__=='__main__':
    from sys import argv, exc_info

    #check()
    run_times=10000
    try:
        run_times=int(argv[1])
        themeids=map(int, argv[2:]) if len(argv)>2 else THEME_CONFIG.keys()
    except Exception, e:
        print '|'.join(traceback.format_exception(e.__class__,e,exc_info()[2]))
        themeids=THEME_CONFIG.keys()
           
    for themeid in themeids:
        for k in THEME_CONFIG[themeid].keys():
            if k.startswith('reels_'):
                spin_result(themeid,k,run_times=run_times)
        if themeid==WITCH_THEME:
            global witch_jackpot
            witch_jackpot=1
            print '\n\n---------------------------------------------------------------------------'
            print 'witch jackpot is open for reels_N and reels_H'
            spin_result(WITCH_THEME,'reels_N',run_times=run_times)
            spin_result(WITCH_THEME,'reels_H',run_times=run_times)
            witch_jackpot=0
