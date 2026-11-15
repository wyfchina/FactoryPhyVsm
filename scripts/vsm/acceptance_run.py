from validate_issue06 import *

TABLES=[L,D,'VSM_Out_WIPSnapshot','VSM_Out_DemandFulfillment',A,F,'VSM_Out_BatchSummary','VSM_Out_FlowTimes','VSM_Out_OperationLog','VSM_Out_ResourceEvents','VSM_Out_RunSummary']

def check(out):
    t=out['tables'];sr=t['VSM_Out_RunSummary'][0]
    assert float(sr['Balance'])==0 and float(sr['InitialUnits'])==17130 and float(sr['ReleasedUnits'])==18400
    assert int(sr['NativeCreated'])-int(sr['NativeDestroyed'])==int(sr['NativeInSystem'])
    assert int(sr['NativeCreated'])==1777
    w=t['VSM_Out_WIPSnapshot'];assert len(w)==1890 and all(float(r['SourceBalance'])==0 for r in w)
    assert sorted(set(float(r['SnapshotTime']) for r in w))==[i*55200/3600 for i in range(21)]
    for r in t[L]:
        current=sum(float(r[s+'In'])-float(r[s+'Out']) for s in STAGES)
        assert float(r['Received'])==float(r['Shipped'])+float(r['Scrapped'])+current
        assert float(r['Received'])==float(r['Planned'])
    dd=t['VSM_Out_DemandFulfillment'];assert len(dd)==40
    assert sum(float(r['DemandUnits']) for r in dd)==18400
    assert all(float(r['DemandUnits'])==float(r['OnTime'])+float(r['LateByHorizon'])+float(r['Unfilled']) for r in dd)
    sh=t[A];assert sum(float(r['Units']) for r in sh)==float(sr['ShippedUnits'])
    assert all(float(r['ShipmentTime'])<=1104000/3600 and float(r['Units'])>0 for r in sh)
    stock=t[F];assert all(0<=float(r['RemainingUnits'])<=float(r['OriginalUnits']) for r in stock)
    assert sum(float(r['OriginalUnits'])-float(r['RemainingUnits']) for r in stock)==float(sr['ShippedUnits'])
    for i,r in enumerate(stock,1):
        assert sum(float(a['Units']) for a in sh if int(a['StockRow'])==i)==float(r['OriginalUnits'])-float(r['RemainingUnits'])
    flow=t['VSM_Out_FlowTimes'];censored=[r for r in flow if r['Censored']=='1'];done=[r for r in flow if r['Censored']=='0']
    assert sum(float(r['Units']) for r in done)==sum(float(r['Manufactured']) for r in t[L])
    assert sum(float(r['Units']) for r in censored)==sum(float(r[s+'In'])-float(r[s+'Out']) for r in t[L] for s in STAGES if s!='FGStaging')
    assert all(float(r['ManufacturingCT'])==-1 for r in flow if r['CTKnown']=='0' or r['Censored']=='1')
    assert all(abs(float(r['EndToEnd'])-float(r['ManufacturingCT'])-float(r['FGWait']))<1e-8 for r in sh if r['CTKnown']=='1')
    ops=t['VSM_Out_OperationLog']
    for s in STAGES[:-1]:
        station=[r for r in ops if r['Resource']=='Server_'+s]
        assert all(float(r['ElapsedTime'])+1e-9>=float(r['ServiceTime'])+float(r['SetupTime']) for r in station)
        assert all(float(b['StartTime'])+1e-9>=float(a['FinishTime']) for a,b in zip(station,station[1:]))
    for name,rr in t.items():
        if name.startswith('VSM_Out_'):
            assert all(r.get('Version')=='VSM_V0.12_FlowDemandLedgerCandidate' for r in rr)
            assert all(r.get('Replication')=='20261114' for r in rr)
    return dict(native=sr,demand={n:sum(float(r[n]) for r in dd) for n in ['DemandUnits','OnTime','LateByHorizon','Unfilled']},censoredUnits=sum(float(r['Units']) for r in censored),outputRows={k:len(v) for k,v in t.items()})

def main():
    stop()
    for collection,name in [('Elements','VSM_TestSupplyClock'),('Processes','VSM_TestSupplyProcess'),('Tables','VSM_TestSupply')]:
        if any(x['name']==name for x in call('list_children',path=MODEL+'/'+collection)['items']):call('delete_item',path=MODEL+'/'+collection+'/'+name)
    for n,v in [('VSM_EntityUnitQuantity','20'),('VSM_NumberWorkdays','20'),('VSM_WorkdayHours',55200/3600),('VSM_EnableSetups','1')]:setp(MODEL+'/States/'+n,'初始状态值',v)
    call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=False,SpecificReplicationNumber=20261114)))
    out=run('issue06-V012-final-random-rep20261114',TABLES);res=check(out);print('CHECK',res,flush=True)
    stop();call('reset_model',modelPath=MODEL)
    empty=call('get_table_data',path=MODEL+'/Tables/'+A,offset=0,limit=1)
    assert empty['totalCount']==0
    resetledger=call('get_table_data',path=MODEL+'/Tables/'+L,offset=0,limit=20)
    stop();again=run('issue06-V012-repeat-random-rep20261114',TABLES);res2=check(again)
    assert out['tables']==again['tables'],'Fixed replication produced different output tables'
    print('PASS repeat identical and reset clears outputs',flush=True)
    (EVIDENCE/'issue06-acceptance-summary.json').write_text(json.dumps(dict(checks=res,repeatIdentical=True,resetAllocationRows=empty['totalCount'],resetLedger=resetledger,diagnostics=call('get_diagnostics',modelPath=MODEL)),ensure_ascii=False,indent=2),encoding='utf-8')
    stop()

if __name__=='__main__':main()
