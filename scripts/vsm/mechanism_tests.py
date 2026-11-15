from validate_issue06 import *

def prepare():
    stop()
    original={'initial':property_rows('VSM_InitialWIPTable'),'source':{x['name']:x['value'] for x in props(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals,Entities Per Arrival')['items']},'release':call('get_process_xml',path=MODEL+'/Processes/VSM_OnProductionRelease')['xml'],'prepare':call('get_process_xml',path=MODEL+'/Processes/VSM_PrepareStamping')['xml'],'reliability':{s:{x['name']:x['value'] for x in props(MODEL+'/Objects/Server_'+s,'Uptime Between Failures,Time To Repair')['items']} for s in ['Stamping','Weld2']}}
    (EVIDENCE/'issue06-mechanism-restore.json').write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding='utf-8')
    return original

def restore(o):
    stop();rows('VSM_InitialWIPTable',o['initial'])
    for n,v in o['source'].items():setp(MODEL+'/Objects/Source_ProductionRelease',n,v)
    for key in ['release','prepare']:call('set_process_xml',modelPath=MODEL,xml=o[key])
    for s in ['Stamping','Weld2']:
        setp(MODEL+'/Objects/Server_'+s,'Failure Type','Calendar Time Based')
        for n,v in o['reliability'][s].items():setp(MODEL+'/Objects/Server_'+s,n,v,'Hours')
    for n,v in [('VSM_NumberWorkdays','20'),('VSM_WorkdayHours',str(55200/3600)),('VSM_EnableSetups','1'),('VSM_EntityUnitQuantity','20')]:setp(MODEL+'/States/'+n,'初始状态值',v)
    call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=False)))

def tests():
    o=prepare();result={}
    try:
        rows('VSM_InitialWIPTable',[dict(r,BatchEntityCount='0') for r in o['initial']])
        for s in ['Stamping','Weld2']:setp(MODEL+'/Objects/Server_'+s,'Failure Type','No Failures')
        setp(MODEL+'/States/VSM_NumberWorkdays','初始状态值','1');setp(MODEL+'/States/VSM_WorkdayHours','初始状态值','4')
        setp(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals','1');setp(MODEL+'/Objects/Source_ProductionRelease','Entities Per Arrival','6')
        release=ET.fromstring(o['release'])
        for n in release.iter('Property'):
            if n.get('Name')=='NewValue' and (n.text or '').startswith('12 + 2*'):n.text='12 + Math.If(VSM_ReleaseSequence<=40 || VSM_ReleaseSequence>80,0,1)'
        call('set_process_xml',modelPath=MODEL,xml=ET.tostring(release,encoding='unicode'))
        call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=True)))
        out=run('issue06-M01-changeover-LLRRLL')
        for s,setup in [('Server_Stamping',1),('Server_Weld1',.167),('Server_Weld2',.167)]:
            ops=[r for r in out['tables']['VSM_Out_OperationLog'] if r['Resource']==s]
            assert [r['Product'] for r in ops]==['Left','Left','Right','Right','Left','Left']
            assert [round(float(r['SetupTime']),6) for r in ops]==[0,0,setup,0,setup,0]
            assert all(abs(float(r['ElapsedTime'])-float(r['ServiceTime'])-float(r['SetupTime']))<1e-10 for r in ops)
            result[s]=dict(sequence=[r['Product'] for r in ops],setups=[r['SetupTime'] for r in ops])
        stop();call('set_process_xml',modelPath=MODEL,xml=o['release'])
        setp(MODEL+'/Objects/Source_ProductionRelease','Entities Per Arrival','1')
        setp(MODEL+'/States/VSM_EnableSetups','初始状态值','0')
        setp(MODEL+'/States/VSM_WorkdayHours','初始状态值','3')
        p=ET.fromstring(o['prepare'])
        for n in p.iter('Property'):
            if n.get('Name')=='AssignmentsNewValue' and (n.text or '').startswith('Math.SumOfSamples'):n.text='1'
        call('set_process_xml',modelPath=MODEL,xml=ET.tostring(p,encoding='unicode'))
        ob=MODEL+'/Objects/Server_Stamping';setp(ob,'Failure Type','Calendar Time Based');setp(ob,'Uptime Between Failures','.5','Hours');setp(ob,'Time To Repair','1','Hours')
        call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=False)))
        out=run('issue06-M02-failure-resume')
        ops=[r for r in out['tables']['VSM_Out_OperationLog'] if r['Resource']=='Server_Stamping']
        assert len(ops)==1 and float(ops[0]['ServiceTime'])==1 and float(ops[0]['StartTime'])==0 and float(ops[0]['FinishTime'])==2
        assert [(r['Event'],float(r['EventTime'])) for r in out['tables']['VSM_Out_ResourceEvents']][:2]==[('Failed',.5),('Repaired',1.5)]
        result['failure_resume']=ops[0]
        stop();setp(MODEL+'/Objects/Source_ProductionRelease','Maximum Arrivals','0')
        out=run('issue06-M03-idle-failure')
        assert not out['tables']['VSM_Out_OperationLog']
        assert float(out['tables']['VSM_Out_ResourceEvents'][0]['EventTime'])==.5
        result['idle_failure']=out['tables']['VSM_Out_ResourceEvents']
    finally:restore(o)
    (EVIDENCE/'issue06-mechanisms-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('M01-M03 PASSED; production settings restored')

if __name__=='__main__':tests()
