"""Native acceptance cases; saves all evidence, restores production configuration."""
import time
from build_issue06 import *
from capture_run import capture

def stop():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)

def property_rows(name):
    d=call('get_table_data',path=MODEL+'/Tables/'+name,offset=0,limit=100)
    keep=[x['name'] for x in d['columnDetails'] if x['columnKind']=='property']
    return [{k:v for k,v in dict(zip(d['columns'],r)).items() if k in keep} for r in d['rows']]

def rows(name, data):call('set_table_data',path=MODEL+'/Tables/'+name,rows=json.dumps(data),startRow=0,clearExisting=True)

def run(label, tables=None, allowed_warnings=None):
    diag=call('get_diagnostics',modelPath=MODEL)
    if diag['errorCount']:raise RuntimeError(str(diag))
    call('fast_forward_model',modelPath=MODEL)
    for _ in range(120):
        time.sleep(.3)
        r=call('get_run_status',modelPath=MODEL)
        if not r['running'] and r['dispatcherStatus']=='idle':
            unexpected=[w for w in r.get('warnings',[]) if w.get('identifier') not in (allowed_warnings or [])]
            if r['lastError'] or unexpected:raise RuntimeError(str(r))
            return capture(label,tables or [L,D,'VSM_Out_DemandFulfillment',A,F,'VSM_Out_FlowTimes','VSM_Out_OperationLog','VSM_Out_ResourceEvents'])
    raise RuntimeError('Native test did not finish')

def rig():
    stop()
    state('VSM_NumberWorkdays',initial='20',desc='工作日数量；正式模型20；专用机制验证可受控修改，验证后恢复。')
    state('VSM_WorkdayHours','Real',initial=str(55200/3600),time=True,desc='每天有效工时15小时20分；仅计工作时间；日末为整数日乘本值。')
    clock=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_DailyClock')['xml'])
    for x in clock.iter('Property'):
        if x.get('Name')=='ConditionOrProbability' and x.text=='VSM_ClockDay <= 20':x.text='VSM_ClockDay <= VSM_NumberWorkdays'
        if x.get('Name')=='DelayEndTime':x.text='VSM_ClockDay * Math.Round(VSM_WorkdayHours * 3600) / 3600'
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(clock,encoding='unicode'))
    table('VSM_TestSupply',[col('ArrivalTime','Real',time=True,k='property',d='专用测试供货时刻，小时。'),col('Quantity',k='property'),col('SourceRow',k='property')],False,'仅供F01–F07机制测试的输入；生产配置中对应Timer关闭且此表为空；不参与业务仿真。')
    timer=ensure('Elements','VSM_TestSupplyClock','Timer')
    setp(timer,'Initially Enabled','False');setp(timer,'Maximum Events','1');setp(timer,'Time Offset','0')
    p=Process('VSM_TestSupplyProcess','专用测试刺激；表驱动按给定时刻创建库存实体并送到成品；不参与生产配置。')
    p.step('Search','遍历测试刺激',dict(CollectionType='TableRows',TableName='VSM_TestSupply',SearchRelatedRowsOnly='False',MatchCondition='VSM_TestSupply.Quantity>0',Limit='Infinity',CopyOverTableRowReferences='True',TokenWaitAction='NoWait'),[('Found','Alternate',3)])
    p.last=None;p.step('Delay','等待指定供货时刻',dict(DelayType='UntilTime',DelayEndTime='VSM_TestSupply.ArrivalTime'),connect=False)
    create=p.step('Create','生成测试库存实体',dict(CreateType='NewObject',EntityType='DefaultEntity',NumberToCreate='1',TokenWaitAction='WaitUntilNewTokenProcessingCompleted'),[('Created','Alternate',5)])
    p.last=None;p.assign('登记测试来源',[(R,'VSM_TestSupply.SourceRow'),(Q,'VSM_TestSupply.Quantity'),('ModelEntity.VSM_ProductTypeState',f'{L}[{R}].Product'),('ModelEntity.VSM_ProductionBatchState',f'{L}[{R}].SourceID'),(f'{L}[{R}].Received',f'{L}[{R}].Received+{Q}')],connect=False)
    p.step('Transfer','测试库存入库',dict(EntityType='AssociatedObject',FromType='FreeSpace',ToType='Node',NodeName='Input@Server_FG_Staging',TokenWaitAction='WaitUntilTransferred'));p.send()
    setp(timer,'Triggered Process Name','VSM_TestSupplyProcess')

def ftests():
    rig()
    original={'initial':property_rows('VSM_InitialWIPTable'),'demand':property_rows(D),'source':props(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals')['items'][0]['value'],'clock':call('get_process_xml',path=MODEL+'/Processes/VSM_DailyClock')['xml']}
    (EVIDENCE/'issue06-test-restore.json').write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding='utf-8')
    results=[]
    def case(code, supplies, demand, days=2, dayhours=1, unfinished=False):
        stop()
        init=[dict(r,BatchEntityCount='0') for r in original['initial']]
        if unfinished:init[7]['BatchEntityCount']='1';init[7]['BatchUnitQuantity']='20'
        rows('VSM_InitialWIPTable',init)
        dd=[dict(r,DueTime=str((i//2+1)*dayhours),DemandUnits=str(demand.get((i//2+1,r['Product']),0))) for i,r in enumerate(original['demand'])]
        rows(D,dd)
        rows('VSM_TestSupply',[dict(ArrivalTime=t,SourceRow=s,Quantity=q) for t,s,q in supplies])
        setp(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals','0')
        setp(MODEL+'/Elements/VSM_TestSupplyClock','Initially Enabled','True')
        for s in ['Stamping','Weld2']:setp(MODEL+'/Objects/Server_'+s,'Failure Type','No Failures')
        setp(MODEL+'/States/VSM_EnableSetups','初始状态值','0')
        setp(MODEL+'/States/VSM_NumberWorkdays','初始状态值',days)
        setp(MODEL+'/States/VSM_WorkdayHours','初始状态值',dayhours)
        setp(MODEL+'/Objects/Server_Assembly2','Processing Time','3601/3600' if unfinished else 'ModelEntity.VSM_ServiceTime + ModelEntity.VSM_SetupTime','Hours')
        call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=True)))
        out=run('issue06-'+code)
        f=out['tables']['VSM_Out_DemandFulfillment']
        summ={n:sum(float(r[n]) for r in f) for n in ['DemandUnits','OnTime','LateByHorizon','Unfilled']}
        results.append(dict(test=code,totals=summ,allocationRows=len(out['tables'][A]),stock=[float(r['RemainingUnits']) for r in out['tables'][F]],time=out['time']))
        print(code,results[-1],flush=True)
        return out,summ
    try:
        o,s=case('F01',[(0,10,620),(0,11,300)],{(1,'Left'):600,(1,'Right'):320})
        assert s==dict(DemandUnits=920,OnTime=900,LateByHorizon=0,Unfilled=20)
        assert sum(float(r['RemainingUnits']) for r in o['tables'][F])==20
        o,s=case('F02',[(0,10,500),(2-1/3600,10,700)],{(1,'Left'):600,(2,'Left'):600})
        assert s==dict(DemandUnits=1200,OnTime=1100,LateByHorizon=100,Unfilled=0)
        o,s=case('F03',[(0,10,20)],{(1,'Left'):40},unfinished=True)
        assert s==dict(DemandUnits=40,OnTime=20,LateByHorizon=20,Unfilled=0)
        o,s=case('F04',[(0,10,20)],{(1,'Left'):10,(2,'Left'):10})
        assert [float(r['Units']) for r in o['tables'][A]]==[10,10]
        assert len(o['tables'][F])==1 and float(o['tables'][F][0]['RemainingUnits'])==0
        o,s=case('F05',[(1-1/3600,10,20),(1,10,20),(1+1/3600,10,20)],{(1,'Left'):60})
        assert s==dict(DemandUnits=60,OnTime=40,LateByHorizon=20,Unfilled=0)
        dem={(i,p):q for i in range(1,21) for p,q in [('Left',600),('Right',320)]}
        o,s=case('F06',[(1104000/3600,10,12000),(1104000/3600,11,6400)],dem,days=20,dayhours=55200/3600)
        assert s==dict(DemandUnits=18400,OnTime=920,LateByHorizon=17480,Unfilled=0)
        assert o['time']['result']['value']==1104000/3600
        assert all(float(r['ShipmentTime'])==1104000/3600 for r in o['tables'][A])
        o,s=case('F07',[(0,10,20)],{})
        assert len(o['tables'][A])==0 and float(o['tables'][F][0]['RemainingUnits'])==20
        assert all(r['RateDefined']=='0' and r['DueDateUnitFillRate']=='-1' for r in o['tables']['VSM_Out_DemandFulfillment'])
    finally:
        stop();rows('VSM_InitialWIPTable',original['initial']);rows(D,original['demand']);rows('VSM_TestSupply',[])
        setp(MODEL+'/Elements/VSM_TestSupplyClock','Initially Enabled','False')
        setp(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals',original['source'])
        setp(MODEL+'/States/VSM_NumberWorkdays','初始状态值','20');setp(MODEL+'/States/VSM_WorkdayHours','初始状态值',55200/3600)
        setp(MODEL+'/States/VSM_EnableSetups','初始状态值','1')
        setp(MODEL+'/Objects/Server_Assembly2','Processing Time','ModelEntity.VSM_ServiceTime + ModelEntity.VSM_SetupTime','Hours')
        for s in ['Stamping','Weld2']:setp(MODEL+'/Objects/Server_'+s,'Failure Type','Calendar Time Based')
        call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=False)))
        (EVIDENCE/'issue06-F01-F07-summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('F01-F07 PASSED; production settings restored')

if __name__=='__main__':ftests()
