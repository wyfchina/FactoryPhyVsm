from mechanism_tests import *

def tests():
    o=prepare();results=[]
    try:
        for q in [20,1]:
            stop()
            setp(MODEL+'/States/VSM_EnableSetups','初始状态值','0')
            setp(MODEL+'/States/VSM_EntityUnitQuantity','初始状态值',q)
            for s in ['Stamping','Weld2']:setp(MODEL+'/Objects/Server_'+s,'Failure Type','No Failures')
            init=o['initial'] if q==20 else [dict(r,BatchEntityCount=r['EntitiesPerArrival'],BatchUnitQuantity='1') for r in o['initial']]
            rows('VSM_InitialWIPTable',init)
            call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=True)))
            out=run('issue06-Q'+str(q)+'-deterministic-reference',[L,'VSM_Out_DemandFulfillment','VSM_Out_BatchSummary','VSM_Out_FlowTimes'],allowed_warnings=['Model_HighNumberOfAgentsInSystem'] if q==1 else [])
            t=out['tables'];f=t['VSM_Out_FlowTimes'];done=[r for r in f if r['Censored']=='0' and r['CTKnown']=='1']
            denom=sum(float(r['Units']) for r in done)
            result=dict(q=q,demand={n:sum(float(r[n]) for r in t['VSM_Out_DemandFulfillment']) for n in ['DemandUnits','OnTime','LateByHorizon','Unfilled']},received=sum(float(r['Received']) for r in t[L]),shipped=sum(float(r['Shipped']) for r in t[L]),manufacturingCTHours=sum(float(r['ManufacturingCT'])*float(r['Units']) for r in done)/denom,completedNewUnits=denom,censoredUnits=sum(float(r['Units']) for r in f if r['Censored']=='1'),batches=t['VSM_Out_BatchSummary'])
            assert result['received']==35530 and result['demand']['DemandUnits']==18400
            assert result['censoredUnits']==sum(float(r['Received'])-float(r['Manufactured']) for r in t[L] if r['SourceID'] not in ['InitialWIP_W05_L','InitialWIP_W05_R'])
            results.append(result);print(result,flush=True)
    finally:restore(o)
    (EVIDENCE/'issue06-aggregation-comparison.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Q20/Q1 reference complete; production configuration restored')

if __name__=='__main__':tests()
