#!/usr/bin/env python3
import csv, gzip, io, urllib.request
from collections import defaultdict

URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz"
OUT = "nfl_scripted_drive_2026.csv"
DRIVES_OUT = "nfl_scripted_drive_2026_drives.csv"
MD_OUT = "nfl_scripted_drive_2026.md"

def fnum(v, default=None):
    try:
        if v is None or v == "": return default
        return float(v)
    except Exception:
        return default
def fint(v, default=None):
    x=fnum(v, None)
    return default if x is None else int(x)
def truth(v):
    return str(v).strip().lower() in {"1","1.0","true","t","yes"}
def points_delta(rows):
    starts=[]; posts=[]
    for r in rows:
        a=fnum(r.get("posteam_score")); b=fnum(r.get("posteam_score_post"))
        if a is not None: starts.append(a)
        if b is not None: posts.append(b)
    if starts and posts: return max(0.0, max(posts)-min(starts))
    result=(rows[-1].get("fixed_drive_result") or "").lower()
    if "touchdown" in result: return 7.0
    if "field goal" in result: return 3.0
    return 0.0
def drive_half(rows):
    qs=[fint(r.get("qtr")) for r in rows if fint(r.get("qtr")) is not None]
    q0=min(qs) if qs else fint(rows[0].get("drive_quarter_start"),1)
    return 1 if q0 <= 2 else 2
def sum_yards(rows):
    return sum((fnum(r.get("yards_gained"),0) or 0) for r in rows)
def first_downs(rows):
    vals=[fnum(r.get("drive_first_downs")) for r in rows if fnum(r.get("drive_first_downs")) is not None]
    if vals: return max(vals)
    total=0.0; seen=set()
    for r in rows:
        pid=r.get("play_id")
        if pid in seen: continue
        seen.add(pid)
        if truth(r.get("first_down")) or any(truth(r.get(k)) for k in ("first_down_rush","first_down_pass","first_down_penalty")):
            total += 1
    return total
def play_count(rows):
    vals=[fnum(r.get("drive_play_count")) for r in rows if fnum(r.get("drive_play_count")) is not None]
    if vals: return int(max(vals))
    return sum(1 for r in rows if (r.get("play_type") or "") in {"run","pass","qb_kneel","qb_spike"})
def kneel_only(rows, pc):
    if pc <= 0: return True
    k=sum(1 for r in rows if truth(r.get("qb_kneel")) or (r.get("play_type") or "")=="qb_kneel")
    return k >= pc
def drive_result(rows):
    vals=[r.get("fixed_drive_result") for r in rows if r.get("fixed_drive_result")]
    return vals[-1] if vals else (rows[-1].get("drive_result") or "")
def dl_rows():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 scripted-drive-tracker"})
    with urllib.request.urlopen(req,timeout=120) as resp:
        gz=gzip.GzipFile(fileobj=resp); txt=io.TextIOWrapper(gz,encoding="utf-8",newline="")
        for r in csv.DictReader(txt):
            if r.get("season_type")=="REG" and fint(r.get("season"))==2026: yield r

groups=defaultdict(list)
for r in dl_rows():
    team=r.get("posteam"); game=r.get("game_id"); d=r.get("fixed_drive") or r.get("drive")
    if team and game and d: groups[(game,team,d)].append(r)

drives=[]
for (game,team,d), rows in groups.items():
    rows.sort(key=lambda x:fnum(x.get("play_id"),0) or 0)
    pc=play_count(rows)
    if pc<=0 or kneel_only(rows,pc): continue
    pts=points_delta(rows); res=drive_result(rows); fd=first_downs(rows)
    drives.append({"game_id":game,"week":fint(rows[0].get("week"),0),"team":team,"drive_id":d,
        "half":drive_half(rows),"play_id_start":fnum(rows[0].get("play_id"),0) or 0,
        "points":pts,"yards":sum_yards(rows),"plays":pc,"first_downs":fd,
        "score":1 if pts>0 else 0,"td":1 if pts>=6 or "touchdown" in res.lower() else 0,
        "three_and_out":1 if pc==3 and fd==0 and "punt" in res.lower() else 0,"result":res})

byght=defaultdict(list)
for d in drives: byght[(d["game_id"],d["team"],d["half"])].append(d)
for arr in byght.values():
    arr.sort(key=lambda x:x["play_id_start"])
    for i,d in enumerate(arr,1): d["half_drive_no"]=i

latest_week=max((d["week"] for d in drives),default=0)
def aggregate(arr):
    n=len(arr)
    if not n: return {"n":0,"scores":0,"tds":0,"score_pct":None,"td_pct":None,"ppd":None,"ypd":None,"threeout_pct":None,"fdpd":None}
    scores=sum(x["score"] for x in arr); tds=sum(x["td"] for x in arr)
    return {"n":n,"scores":scores,"tds":tds,"score_pct":scores/n,"td_pct":tds/n,
        "ppd":sum(x["points"] for x in arr)/n,"ypd":sum(x["yards"] for x in arr)/n,
        "threeout_pct":sum(x["three_and_out"] for x in arr)/n,"fdpd":sum(x["first_downs"] for x in arr)/n}

rowsout=[]
for t in sorted({d["team"] for d in drives}):
    td=[d for d in drives if d["team"]==t]
    a1=aggregate([d for d in td if d["half"]==1 and d["half_drive_no"]==1])
    a2=aggregate([d for d in td if d["half"]==2 and d["half_drive_no"]==1])
    a=aggregate([d for d in td if d["half_drive_no"]<=2])
    an=aggregate([d for d in td if d["half_drive_no"]>=3])
    adv=(a["ppd"]-an["ppd"]) if a["ppd"] is not None and an["ppd"] is not None else None
    rowsout.append({"team":t,"games":len({d["game_id"] for d in td}),
        "h1_n":a1["n"],"h1_scores":a1["scores"],"h1_tds":a1["tds"],"h1_score_pct":a1["score_pct"],"h1_td_pct":a1["td_pct"],"h1_ppd":a1["ppd"],"h1_ypd":a1["ypd"],"h1_3out_pct":a1["threeout_pct"],"h1_fdpd":a1["fdpd"],
        "h2_n":a2["n"],"h2_scores":a2["scores"],"h2_tds":a2["tds"],"h2_score_pct":a2["score_pct"],"h2_td_pct":a2["td_pct"],"h2_ppd":a2["ppd"],"h2_ypd":a2["ypd"],"h2_3out_pct":a2["threeout_pct"],"h2_fdpd":a2["fdpd"],
        "script_n":a["n"],"script_scores":a["scores"],"script_tds":a["tds"],"script_score_pct":a["score_pct"],"script_td_pct":a["td_pct"],"script_ppd":a["ppd"],"script_ypd":a["ypd"],"script_3out_pct":a["threeout_pct"],"script_fdpd":a["fdpd"],
        "nonscript_n":an["n"],"nonscript_ppd":an["ppd"],"script_advantage":adv})
def key(r):
    z=lambda v:-999 if v is None else v
    return (z(r["script_ppd"]),z(r["script_advantage"]),z(r["script_td_pct"]),z(r["script_score_pct"]),z(r["script_ypd"]))
rowsout.sort(key=key,reverse=True)
for i,r in enumerate(rowsout,1): r["rank"]=i

fields=["rank","team","games","h1_n","h1_scores","h1_tds","h1_score_pct","h1_td_pct","h1_ppd","h1_ypd","h1_3out_pct","h1_fdpd","h2_n","h2_scores","h2_tds","h2_score_pct","h2_td_pct","h2_ppd","h2_ypd","h2_3out_pct","h2_fdpd","script_n","script_scores","script_tds","script_score_pct","script_td_pct","script_ppd","script_ypd","script_3out_pct","script_fdpd","nonscript_n","nonscript_ppd","script_advantage"]
with open(OUT,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for r in rowsout: w.writerow({k:r.get(k) for k in fields})
dfields=["game_id","week","team","half","half_drive_no","points","yards","plays","first_downs","score","td","three_and_out","result","drive_id"]
with open(DRIVES_OUT,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=dfields); w.writeheader()
    for d in sorted(drives,key=lambda x:(x["week"],x["game_id"],x["team"],x["half"],x["half_drive_no"])):
        w.writerow({k:d.get(k) for k in dfields})

def pct(v): return "—" if v is None else f"{100*v:.1f}%"
def num(v,d=2): return "—" if v is None else f"{v:.{d}f}"
def rawpct(x,n,p): return f"{x}/{n} ({pct(p)})" if n else "—"
with open(MD_OUT,"w",encoding="utf-8") as f:
    f.write(f"# 2026 NFL Scripted Drive Tracker — through Week {latest_week}\n\n")
    f.write("Ranking = first-two-drives-of-each-half points/drive, with Script Advantage, TD%, score%, then yards/drive as tiebreakers. Opening-drive columns keep 1H and 2H separate. Kneel-only end-of-half/game possessions are excluded.\n\n")
    f.write("|Rk|Team|G|1H opener Score|1H TD|1H PPD|1H Y/Dr|1H 3&O|1H FD/Dr|2H opener Score|2H TD|2H PPD|2H Y/Dr|2H 3&O|2H FD/Dr|First 2/half PPD|Score|TD|Y/Dr|3&O|FD/Dr|Non-script PPD|Adv|\n")
    f.write("|-:|:--|-:|:--|:--|-:|-:|:--|-:|:--|:--|-:|-:|:--|-:|-:|:--|:--|-:|:--|-:|-:|-:|\n")
    for r in rowsout:
        f.write("|{rank}|{team}|{games}|{h1score}|{h1td}|{h1ppd}|{h1ypd}|{h13o}|{h1fd}|{h2score}|{h2td}|{h2ppd}|{h2ypd}|{h23o}|{h2fd}|{sppd}|{sscore}|{std}|{sypd}|{s3o}|{sfd}|{nppd}|{adv}|\n".format(
            rank=r["rank"],team=r["team"],games=r["games"],h1score=rawpct(r["h1_scores"],r["h1_n"],r["h1_score_pct"]),h1td=rawpct(r["h1_tds"],r["h1_n"],r["h1_td_pct"]),h1ppd=num(r["h1_ppd"]),h1ypd=num(r["h1_ypd"],1),h13o=rawpct(round((r["h1_3out_pct"] or 0)*r["h1_n"]),r["h1_n"],r["h1_3out_pct"]),h1fd=num(r["h1_fdpd"],2),
            h2score=rawpct(r["h2_scores"],r["h2_n"],r["h2_score_pct"]),h2td=rawpct(r["h2_tds"],r["h2_n"],r["h2_td_pct"]),h2ppd=num(r["h2_ppd"]),h2ypd=num(r["h2_ypd"],1),h23o=rawpct(round((r["h2_3out_pct"] or 0)*r["h2_n"]),r["h2_n"],r["h2_3out_pct"]),h2fd=num(r["h2_fdpd"],2),
            sppd=num(r["script_ppd"]),sscore=rawpct(r["script_scores"],r["script_n"],r["script_score_pct"]),std=rawpct(r["script_tds"],r["script_n"],r["script_td_pct"]),sypd=num(r["script_ypd"],1),s3o=rawpct(round((r["script_3out_pct"] or 0)*r["script_n"]),r["script_n"],r["script_3out_pct"]),sfd=num(r["script_fdpd"],2),nppd=num(r["nonscript_ppd"]),adv=num(r["script_advantage"])))
print(f"Wrote {len(rowsout)} teams, {len(drives)} drives, latest week {latest_week}")
