from mechanism_tests import *

def tests():
    o=prepare();demand=property_rows(D);ledger=property_rows(L)
    try:
        rows('VSM_InitialWIPTable',[dict(r,BatchEntityCount='0') for r in o['initial']])
        rows(D,[dict(r,DueTime=str(i//2+1),DemandUnits='10' if i==2 else '30' if i==4 else '0') for i,r in enumerate(demand)])
        ll=[dict(r) for r in ledger];ll[11]['Planned']='40';rows(L,ll)
        for s in ['Stamping','Weld2']:setp(MODEL+'/Objects/Server_'+s,'Failure Type','No Failures')
        for n,v in [('VSM_NumberWorkdays','3'),('VSM_WorkdayHours','1'),('VSM_EnableSetups','0')]:setp(MODEL+'/States/'+n,'初始状态值',v)
        setp(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals','1');setp(MODEL+'/Objects/Source_ProductionRelease','Entities Per Arrival','2')
        call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=True)))
        out=run('issue06-M04-CT-complete-batch-partial-shipment')
        flows=out['tables']['VSM_Out_FlowTimes'];ship=out['tables'][A]
        assert len(flows)==2 and all(r['CTKnown']=='1' and r['Censored']=='0' for r in flows)
        assert abs(float(flows[0]['ManufacturingCT'])-188*20/3600)<1e-10
        assert [float(r['Units']) for r in ship]==[10,10,20]
        assert [float(r['ShipmentTime']) for r in ship]==[2,3,3]
        assert all(abs(float(r['EndToEnd'])-float(r['ManufacturingCT'])-float(r['FGWait']))<1e-10 for r in ship)
        batches=call('get_table_data',path=MODEL+'/Tables/VSM_Out_BatchSummary',offset=0,limit=10)
        first=dict(zip(batches['columns'],batches['rows'][0]))
        assert first['Complete']=='1' and first['Makespan']=='3' and first['Shipped']=='40'
        pop=call('get_table_data',path=MODEL+'/Tables/VSM_Out_RunSummary',offset=0,limit=5)
        summary=dict(zip(pop['columns'],pop['rows'][0]))
        assert summary['NativeInSystem']=='0' and summary['NativeCreated']==summary['NativeDestroyed']=='2'
        assert all(float(summary[s+'Allocated'])==0 for s in STAGES)
        (EVIDENCE/'issue06-CT-batch-summary.json').write_text(json.dumps(dict(firstManufacturingCT=flows[0]['ManufacturingCT'],shipments=ship,batch=first,population=pop),ensure_ascii=False,indent=2),encoding='utf-8')
    finally:restore(o);rows(D,demand);rows(L,ledger)
    print('M04 PASSED; production configuration restored')

if __name__=='__main__':tests()
