O_length=3564/(40.0789*1e6)
OC_length=524288*O_length


# This function adds global timestamps to a trigger primitives collection, returns the new collection
# Arguments:
#  tpcollecton -> the trigger primitives collection to work on
# Return:
#  new_collection -> a copy of the trigger primitives collection with added 'timestamp' key

def get_global_timestamps_tp(tpcollection):
#     O_length=3564/(40.0789*1e6)
#     OC_length=524288*O_length
    TDCcount=1/(32*40.0789*1e6)
    new_collection=[]
    old_oc=tpcollection[0]['arrival']['OC']
    n_oc=0
    for tp in tpcollection:
        this_oc=tp['arrival']['OC']
        this_bx=tp['arrival']['BX']
        tp_t0=tp['t0']
        this_oc_corr=this_oc - (1 if (this_bx<100 and tp_t0 > 112320) else 0)
        if this_oc_corr<old_oc:
            n_oc+=1 
        old_oc=this_oc_corr
        tp['timestamp']=n_oc*OC_length+this_oc_corr*O_length+tp_t0*TDCcount
        new_collection.append(tp)
    return new_collection



# This function adds global timestamps to a hit collection, returns the new collection
# Arguments:
#  hitcollecton -> the hit collection to work on
#  mode -> if 'light', a reduced information hit collection is output; if anything else all the original 
#   info is retained
#  max_timestamp -> a maximum value of hit timestamp where to stop the operations (0 if no max)
# Return:
#  new_collection -> the hit collection with added 'timestamp' key, reduced or full content depending on mode par

def get_global_timestamps_hit(hitcollection, mode, max_timestamp):
#     O_length=3564/(40.0789*1e6)
#     OC_length=524288*O_length
    bx=1/(40.0789*1e6)   # è uguale a sopra, da rendere omogeneo
    TDCcount=bx/32
    new_collection=[]
    old_oc=hitcollection[0]['arrival']['OC']
    n_oc=0
    uselightformat=(mode=='light')
    for hit in hitcollection:
        this_oc=hit['arrival']['OC']
        this_bx=hit['arrival']['BX']
        hit_bx=hit['bctr']
        this_oc_corr=this_oc - (1 if (this_bx<100 and hit_bx >3464) else 0)
        if this_oc_corr<old_oc-1:
            n_oc+=1 
        old_oc=this_oc_corr
        thets=n_oc*OC_length+this_oc_corr*O_length+hit_bx*bx+hit['tdc']*TDCcount
        if max_timestamp>0:
            if thets>max_timestamp+1:
                break
        if uselightformat:
            light_hit={}
            light_hit['timestamp']=thets
            light_hit['ly']=hit['ly']
            light_hit['wi']=hit['wi']
            light_hit['st']=hit['st'] 
            new_collection.append(light_hit)
        else:
            hit['timestamp']=thets
            new_collection.append(hit)
    return new_collection


# This function selects hits from a hit collection based on a timestamp and a time matching window
# Arguments:
#  timestamp -> the "event" timestamp of interest
#  chamber -> select hits from chamber, can be 0 (MiniDT_X), 1 (MinDT_Y) or 2 (any MiniDT) 
#  marginlowns, marginhighns -> offsets that are added to the timestamp to define the window of valid hits
#  index_margin -> additional margin for search in terms of the pointer to hits in the hit collection
#                 added for safety in case of high number of scrambled hits, typ 250-500 for extra safety
#  seed_index -> the search starting position of the pointer to hits, use the value returned at the previous
#                call of this funcion when scanning sequentially a series of event timestamps
# Return:
#  hit_j -> the position of the hit pointer at the end of the search (pass as seed_index at the next call)
#  matched_hits -> a list of hit pointers, corresponding to selected hits

def select_hits(timestamp,hits,chamber,marginlow_ns,marginhigh_ns,index_margin,seed_index):
    marginlow=marginlow_ns*1E-9
    marginhig=marginhigh_ns*1E-9
    maxhit=len(hits)-1
    hit_j=seed_index
    win_low_j=0
    win_high_j=0
    tp_ts=timestamp
    hit_ts=hits[hit_j]['timestamp']
    matched_hits=[]
    if hit_ts>=tp_ts+marginlow:    # pointing too forward, need to go backward before loading good hits
        while hit_ts>tp_ts+marginlow:
            hit_j-=1 
            if hit_j<0:
                hit_j=0
                hit_ts=hits[hit_j]['timestamp']
                break
            hit_ts=hits[hit_j]['timestamp']
        hit_j+=1  
    else:
        if hit_ts<tp_ts+marginlow:  
            while hit_ts<tp_ts+marginlow:  # pointing too backward, need to go forward before loading good hits 
                hit_j+=1
                if hit_j==maxhit:
                    break
                hit_ts=hits[hit_j]['timestamp']
    # now hit_j would be the first hit within the window if the ordering by timestamp was ensured...
    win_low_j=hit_j-index_margin # we apply some margin for difficult situations (congestion screws the hit ordering)
    if win_low_j<0:
        win_low_j=0
    # now we look for the upper margin of the matching window
    while hit_ts<(tp_ts+marginhig):
        hit_j+=1
        if hit_j>=maxhit:
            break
        hit_ts=hits[hit_j]['timestamp']
    # now hit_j would be the last hit within the window if the ordering by timestamp was ensured...
    win_high_j=hit_j+index_margin # we apply some margin for difficult situations (congestion screws the hit ordering)
    if win_high_j>=maxhit:
        win_high_j=maxhit-1
    hit_j=win_low_j
    #print(win_high_j,win_low_j)
    for hit_j in range(win_low_j, win_high_j, 1):
        hit_ts=hits[hit_j]['timestamp'] 
        if hits[hit_j]['st']==chamber or chamber==2:
            #print('lowmargin '+str(tp_ts-marginlow)+' - hit ts '+str(hit_ts)+' - upmargin '+str(tp_ts+marginhig))
            #print(marginhig+marginlow)
            if hit_ts<(tp_ts+marginhig) and hit_ts>=(tp_ts+marginlow):
                matched_hits.append(hit_j)

    return hit_j,matched_hits


# This function matched trigger primitives from two collections by timestamps
# Arguments:
#  dtx -> first collection of trigger primitives
#  dty -> second collection of trigger primitives
#  qcutx -> quality cut in selecting TPs from the first  collection (3= accept all; 4 accept only H)
#  qcuty -> quality cut in selecting TPs from the second collection (3= accept all; 4 accept only H)
#  halfwindow_ns -> the size of half matching window, in ns
# Return:
#  indexes -> a list of two-elements lists, containing the index of the tp matched from the first collection
#    and the index of the tp matched from the second collection
# NOTE: the first primitive found in dty that matches the current primitive in dtx is returned, and the search
# moves to the next primitive in dtx. So the search for the "best" match in case there would be multiple
# matches is not well accounted for. On the other hand, if the same primitive in dty can be matched
# to a different primitive in dtx, it is done, there is no check regarding "already used" primitives.

def match_tps_sameBx(dtx,dty,qcutx,qcuty, halfwindow_ns):    #qcut: 3-> accept both L and H; 4-> accept only H
    halfwindow=halfwindow_ns*1E-9
    indexes=[]
    j=0
    for i,px in enumerate(dtx):
        if int(px['str'][0])<qcutx:
            continue
        xts=px['timestamp']
        yts=dty[j]['timestamp']
        while yts>xts-100*1E-9:  #go back at least 100 ns
            j-=1
            if j<0:
                j=0
                break
            yts=dty[j]['timestamp']
        start=j
        while yts<xts+100*1E-9:  # go fwd at least 100 ns
            j+=1
            if j>len(dty)-1:
                j=len(dty)-1
                break
            yts=dty[j]['timestamp']
        stop=j+1
        for j in range(start,stop,1):
            if int(dty[j]['str'][0])<qcuty:
                continue
            yts=dty[j]['timestamp']
            if xts-yts>-halfwindow and xts-yts<halfwindow:
                indexes.append([i,j])
                break
    return indexes