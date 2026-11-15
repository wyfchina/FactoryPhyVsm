from build_issue06 import *

def finalize():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)
    # Consume native, typed business parameters rather than keep a second hard-coded copy.
    table('VSM_OperationTable',[col('ProcessingStream',k='property',d='PROC_P01–P05映射到原生随机流101–105，工序之间独立。')],False,'五制造工序及Shipping的权威运行参数；时间字段有Time单位；开始时Process冻结独立单件样本总和。')
    for ix,s in enumerate(['Stamping','Weld1','Weld2','Assembly1','Assembly2'],1):
        call('set_table_data',path=MODEL+'/Tables/VSM_OperationTable',rows=json.dumps([dict(ProcessingStream=100+ix,SetupMinutes=60 if ix==1 else 10.02 if ix in [2,3] else 0)]),startRow=ix-1,clearExisting=False)
        root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_Prepare'+s)['xml'])
        for x in root.iter('Property'):
            if x.get('Name')=='AssignmentsNewValue' and (x.text or '').startswith('Math.SumOfSamples'):
                x.text=f'Math.SumOfSamples(Random.Exponential(VSM_OperationTable[{ix}].ProcessTimeSeconds,VSM_OperationTable[{ix}].ProcessingStream),{Q})'
            if x.get('Name')=='AssignmentsNewValue' and 'VSM_EnableSetups' in (x.text or ''):
                x.text=f'Math.If(VSM_EnableSetups==1 && VSM_{s}LastProduct!="" && VSM_{s}LastProduct!=ModelEntity.VSM_ProductTypeState,VSM_OperationTable[{ix}].SetupMinutes,0)'
        call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
        setp(MODEL+'/Objects/Server_'+s,'说明',f'{s}：工序均值/换型/随机流引用VSM_OperationTable第{ix}行。单件SCV=1、独立累加；开始时冻结。仅产品变更换型，首件不加。换型与加工使用同一Server原生容量和故障暂停/续作，合计占用但分别输出时间；原生Setup状态未单列。')
    table('VSM_ReliabilityTable',[col('FailureStream',k='property',d='原生故障间隔随机流；Stamping201、Weld2 211。'),col('RepairStream',k='property',d='原生维修时间随机流；Stamping202、Weld2 212，与间隔独立。')],False,'故障运行参数；含空闲的有效开机时间累计uptime；维修后续作；目标可用率为输入，观测值另算。已替换原型旧MTTF=8h参数。')
    for i,s,mttf,stream in [(1,'Stamping',5.6667,201),(3,'Weld2',4,211)]:
        call('set_table_data',path=MODEL+'/Tables/VSM_ReliabilityTable',rows=json.dumps([dict(MTTFHours=mttf,MTTRHours=1,FailureStream=stream,RepairStream=stream+1,SourceType='项目选择：指数开机故障/维修；含待机，维修后继续剩余作业；目标可用率非观测值。')]),startRow=i-1,clearExisting=False)
        ob=MODEL+'/Objects/Server_'+s
        setp(ob,'Uptime Between Failures',f'Random.Exponential(VSM_ReliabilityTable[{i}].MTTFHours,VSM_ReliabilityTable[{i}].FailureStream)','Hours')
        setp(ob,'Time To Repair',f'Random.Exponential(VSM_ReliabilityTable[{i}].MTTRHours,VSM_ReliabilityTable[{i}].RepairStream)','Hours')
    for n in ['FirstRelease','LastShipment']:setp(MODEL+'/Tables/'+L+'/Columns/'+n,'初始状态值','-1')
    for i,h in [(0,55200/3600),(1,55200/3600+1.2)]:call('set_table_data',path=MODEL+'/Tables/VSM_ScenarioTable',rows=json.dumps([dict(DailyAvailableHours=h)]),startRow=i,clearExisting=False)
    setp(MODEL,'VSM_ModelVersion','VSM_V0.12_FlowDemandLedgerCandidate')
    setp(MODEL,'VSM_BaselineStage','INITIAL_FLOW_VALIDATION_CANDIDATE')
    setp(MODEL,'说明','Michigan Steel V0.12：Issue06初始流程候选。表驱动Process初始化WIP，15来源动态State账本、原生Output Table、P1/P2释放、CT/删失、FIFO成品/需求部分分配、产品变更换型及原生故障续作。仅有效工时，20件计算实体保留10件尾批。不是已验收B0/B1；30复制统计和作者对照归08/09。用户保存重载前为未持久化候选。')
    setp(MODEL+'/Elements/VSM_DemandClock','说明','单次t0启动每日过程；按整数有效秒的绝对日末等待，原生晚优先级处理同刻完工后分配盘点；20日末EndRun，不推进额外时间。')
    for name,desc in [('Link_Assembly2ToFGStaging','Assembly2制造完成后送入可用成品；零运输时间；尚未分配不得当作发运。'),('Link_FGStagingToShipping','仅剩余库存为0的空计算实体进入Sink回收；实际件数在分配事件已计账，不重复累计。')]:setp(MODEL+'/Links/'+name,'说明',desc)
    # Remove the temporary test stimulus from the production candidate; its builder/evidence remain external.
    for collection,name in [('Elements','VSM_TestSupplyClock'),('Processes','VSM_TestSupplyProcess'),('Tables','VSM_TestSupply')]:
        if any(x['name']==name for x in call('list_children',path=MODEL+'/'+collection)['items']):call('delete_item',path=MODEL+'/'+collection+'/'+name)
    # Every output freezes its version and native replication; no display-time recomputation.
    outputs=[x['name'] for x in call('list_children',path=MODEL+'/Tables')['items'] if x['name'].startswith('VSM_Out_')]
    for name in outputs:
        table(name,[col('Version','String',d='生成该记录的模型版本快照。'),col('Replication',d='原生Simio复制编号；与固定随机流一起界定复现身份。'),col('RandomnessDisabled',d='1=确定性检查，0=随机运行；在写行时冻结。')],True,props(MODEL+'/Tables/'+name,'说明')['items'][0]['value'])
    for pr in call('list_children',path=MODEL+'/Processes')['items']:
        if not pr['name'].startswith('VSM_'):continue
        root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/'+pr['name'])['xml']);changed=False
        steps={s.get('ID'):s for s in root.find('Steps')}
        for s in steps.values():
            if s.get('Type')!='AddRow':continue
            tn=s.find("Properties/Property[@Name='TableName']").text
            ex=s.find('Exit');target=steps.get(ex.get('NextID')) if ex is not None else None
            if tn not in outputs or target is None or target.get('Type')!='Assign':raise RuntimeError('Output metadata hook requires following Assign: '+pr['name'])
            rowsnode=target.find("Properties/Property[@Name='Assignments']/Rows")
            if rowsnode is None:rowsnode=ET.SubElement(ET.SubElement(target.find('Properties'),'Property',Name='Assignments'),'Rows')
            existing={x.text for x in target.iter('Value')}
            for n,v in [('Version','VSM_ModelVersion'),('Replication','Run.ReplicationNumber'),('RandomnessDisabled','Math.If(Run.RandomnessDisabled,1,0)')]:
                if tn+'.'+n in existing:continue
                pair=ET.SubElement(rowsnode,'Properties');prop(pair,'AssignmentsStateVariableName',tn+'.'+n,True);prop(pair,'AssignmentsNewValue',v);changed=True
        if changed:call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
    # The historical project seed identifier is mapped explicitly to a native replication number.
    # Simio does not expose a direct arbitrary master-seed setter through this MCP.
    call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(SpecificReplicationNumber=20261114,DisableRandomness=False,RunEndType='Infinite',StopAtEndOfRun=False)))
    print(call('get_diagnostics',modelPath=MODEL))

if __name__=='__main__':finalize()
