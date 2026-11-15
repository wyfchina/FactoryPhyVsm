from native import *

def capture(label, tables):
    status=call('get_run_status',modelPath=MODEL)
    if status.get('running'):raise RuntimeError('Run still active; capture later')
    out={'label':label,'status':status,'time':call('evaluate_runtime_expression',modelPath=MODEL,expression='TimeNow'),'tables':{}}
    for name in tables:
        offset=0;rows=[]
        while True:
            d=call('get_table_data',path=MODEL+'/Tables/'+name,offset=offset,limit=100)
            rows += [dict(zip(d['columns'],r)) for r in d['rows']]
            if not d['hasMore']:break
            offset=d['nextOffset']
        out['tables'][name]=rows
    dest=EVIDENCE/(label+'.json');dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    return out

if __name__=='__main__':
    o=capture(sys.argv[1],sys.argv[2:])
    print(json.dumps({'label':o['label'],'status':o['status'],'counts':{k:len(v) for k,v in o['tables'].items()}},ensure_ascii=False))
