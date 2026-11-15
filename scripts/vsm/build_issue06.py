"""Build Issue 06 incrementally through native Simio MCP. Run phases in order."""
from native import *

BEFORE = json.loads((EVIDENCE/'issue06-before-build-20261115.json').read_text(encoding='utf-8'))
def ensure(collection, name, kind):
    items = call('list_children', path=MODEL+'/'+collection)['items']
    if name not in [i['name'] for i in items]:
        call('create_model_item', path=MODEL+'/'+collection, name=name, type=kind)
    return MODEL+'/'+collection+'/'+name

def state(name, kind='Integer', initial='0', desc='', entity=False, time=False):
    root='/Project/ModelEntity' if entity else MODEL
    items=call('list_children',path=root+'/States')['items']
    p=root+'/States/'+name
    if name not in [x['name'] for x in items]: call('create_model_item',path=root+'/States',name=name,type=kind)
    setp(p,'描述',desc or '本次运行内部状态；初始化为0；仅由业务过程更新，不作为历史快照。')
    setp(p,'初始状态值',initial)
    if time: setp(p,'单位类型','Time')

def table(name, columns, output=True, desc=''):
    p=ensure('Tables',name,'Output' if output else 'Data')
    setp(p,'说明',desc)
    data=call('get_table_data',path=p,offset=0,limit=1)
    known=data['columns']
    ops=[dict(action='add',name=n,type=t,columnKind=k) for n,t,k,d,tm in columns if n not in known]
    if ops:call('modify_table_schema',path=p,operations=json.dumps(ops))
    for n,t,k,d,tm in columns:
        cp=p+'/Columns/'+n
        setp(cp,'描述',d)
        if tm:setp(cp,'单位类型','Time')
    return p

def col(n,t='Integer',d='',time=False,k='state'):
    return (n,t,k,d or '单位件；业务事件更新的本次运行状态；输出记录时冻结数值。',time)

def prop(parent,n,value,reference=False):
    p=ET.SubElement(parent,'Property',Name=n)
    if reference:ET.SubElement(p,'Value').text=str(value)
    else:p.text=str(value)
    return p

class Process:
    def __init__(self,name,description,trigger='',interface=None):
        self.root=ET.Element('Process',Name=name,BeginStepID='2',Scope='Public',Description=description)
        if interface:self.root.set('InterfaceProcessID',interface)
        pr=ET.SubElement(self.root,'Properties')
        for n,v in [('ReportStatistics','True'),('TriggeringEventName',trigger),('TokenClassName','Token'),('InitiallyEnabled','True'),('AllowStepTrace','True')]:prop(pr,n,v)
        self.steps=ET.SubElement(self.root,'Steps');self.last=None;self.nextid=2
    def step(self,kind,name,properties=None,exits=None,description='',connect=True):
        sid=self.nextid;self.nextid+=1
        s=ET.SubElement(self.steps,'Step',Type=kind,Name=name,ID=str(sid),Description=description or name+'；按当前业务事件顺序执行。')
        pr=ET.SubElement(s,'Properties')
        for n,v in (properties or {}).items():prop(pr,n,v,n in ['StateVariableName','SaveIndexFound','SaveNumberFound','ObjectOrElement','ProcessName'])
        if connect and self.last is not None:ET.SubElement(self.last,'Exit',Name='Exit',Type='Primary',NextID=str(sid))
        self.last=s
        if exits:
            for nm,tp,dest in exits:ET.SubElement(s,'Exit',Name=nm,Type=tp,NextID=str(dest))
        return s
    def assign(self,name,pairs,**kw):
        s=self.step('Assign',name,dict(StateVariableName=pairs[0][0],NewValue=pairs[0][1]),**kw)
        if len(pairs)>1:
            rows=ET.SubElement(ET.SubElement(s.find('Properties'),'Property',Name='Assignments'),'Rows')
            for n,v in pairs[1:]:
                pr=ET.SubElement(rows,'Properties');prop(pr,'AssignmentsStateVariableName',n,True);prop(pr,'AssignmentsNewValue',v)
        return s
    def execute(self,name,pr):return self.step('Execute',name,dict(ProcessName=pr,TokenWaitAction='WaitUntilProcessCompleted',CopyTableRowReferencesFromCreatedToken='True'))
    def addrow(self,table):return self.step('AddRow','新增'+table.replace('VSM_Out_',''),dict(ObjectType='Token',TableName=table))
    def send(self):
        xml=ET.tostring(self.root,encoding='unicode')
        r=call('set_process_xml',modelPath=MODEL,xml=xml)
        if isinstance(r,dict) and r.get('success') is False:raise RuntimeError(str(r))
        return r

def append_assign(name,pairs,stepname):
    xml=BEFORE['processes'][name]
    root=ET.fromstring(xml);steps=root.find('Steps')
    ids=[int(s.get('ID')) for s in steps];sid=max(ids)+1
    oldlast=steps[-1];ET.SubElement(oldlast,'Exit',Name='Exit',Type='Primary',NextID=str(sid))
    p=Process(name,'保留原有位置级记账，并同步来源台账；单位件，先流入后加工、离开时流出。')
    p.nextid=sid;p.assign(stepname,pairs,connect=False)
    steps.append(p.steps[0]);root.set('Description',p.root.get('Description'))
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))

STAGES=['Stamping','Weld1','Weld2','Assembly1','Assembly2','FGStaging']
L='VSM_SourceLedger'
Q='ModelEntity.VSM_QuantityState'
R='ModelEntity.VSM_SourceRow'

def schema_phase():
    columns=[col('SourceID','String',d='来源唯一编号；初始WIP独立于四张生产工单。',k='property'),col('Product','String',d='产品编码Left/Right。',k='property'),col('Kind','String',d='InitialWIP或Production；决定历史CT是否已知。',k='property'),col('Planned',k='property')]
    columns += [col(n) for n in ['Received','Manufactured','Shipped','Scrapped']]
    columns += [col(s+suffix) for s in STAGES for suffix in ['In','Out']]
    columns += [col(n,'Real',d='累计有效工时时刻，单位小时；未发生为-1。',time=True) for n in ['FirstRelease','LastShipment']]
    table(L,columns,False,'按11条初始库存和4张生产工单维护运行State；不覆盖初始输入，复位清零。位置In-Out为当前件数。')
    w=call('get_table_data',path=MODEL+'/Tables/VSM_InitialWIPTable',offset=0,limit=20)
    rows=[]
    for row in w['rows']:
        d=dict(zip(w['columns'],row));rows.append(dict(SourceID=d['WIPRecordId'],Product=d['ProductType'],Kind='InitialWIP',Planned=d['EntitiesPerArrival']))
    for period in [1,2]:
        for product,quantity in [('L',6000),('R',3200)]:rows.append(dict(SourceID=f'P{period}-{product}',Product='Left' if product=='L' else 'Right',Kind='Production',Planned=quantity))
    call('set_table_data',path=MODEL+'/Tables/'+L,rows=json.dumps(rows),startRow=0,clearExisting=True)
    table('VSM_InitialWIPTable',[col('SourceRow',k='property',d='直接来源台账行号1–11；避免每次流转全表搜索。')],False,'初始化权威输入；Process创建实体并写入来源行号、数量和目的地。')
    call('set_table_data',path=MODEL+'/Tables/VSM_InitialWIPTable',rows=json.dumps([dict(SourceRow=i) for i in range(1,12)]),startRow=0,clearExisting=False)
    for n,t,d,init,tm in [('VSM_SourceRow','Integer','所属来源台账的固定行号；初始化或释放时赋值。','0',False),('VSM_StockRow','Integer','进入成品时登记的库存输出行号；用于部分交付后的退出条件。','0',False),('VSM_StartTime','Real','新生产进入Stamping的有效工时时刻；初始WIP为-1，历史未知。','-1',True),('VSM_FinishTime','Real','离开Assembly2的有效工时时刻；未完成为-1；初始成品为0。','-1',True),('VSM_ServiceTime','Real','本工序冻结的独立单件加工时间之和，单位小时。','0',True),('VSM_SetupTime','Real','本工序冻结的产品变更换型时间，单位小时。','0',True)]:state(n,t,init,d,True,tm)
    table('VSM_Out_WIPSnapshot',[col('SnapshotTime','Real',time=True,d='记录快照的累计有效工时时刻，小时。'),col('SourceID','String',d='来源台账编号快照。'),col('Version','String',d='模型版本快照。'),col('Product','String',d='产品快照。'),col('Stage','String',d='盘点位置。'),col('InitialOrReleased'),col('Entered'),col('Exited'),col('CurrentUnits'),col('Shipped'),col('SourceBalance')],True,'每日及期末把来源台账State冻结为记录；CurrentUnits=Entered-Exited，SourceBalance应为0；复位清空。')
    table('VSM_Out_FlowTimes',[col('Event','String',d='Manufactured/期末删失事件类型。'),col('SourceID','String',d='来源快照。'),col('Product','String',d='产品快照。'),col('Units'),col('StartTime','Real',time=True,d='Stamping进入时刻；初始WIP历史未知用-1并标CTKnown=0。'),col('FinishTime','Real',time=True,d='Assembly2离开时刻；未完成=-1。'),col('ObservationTime','Real',time=True,d='记录时刻，小时。'),col('ManufacturingCT','Real',time=True,d='新生产制造周期；CTKnown=0时=-1。'),col('RemainingCT','Real',time=True,d='初始WIP从t0到完成的剩余周期；新生产=-1。'),col('CTKnown'),col('Censored')],True,'完成与期末删失记录；不把初始WIP剩余CT称为完整制造CT。按Units加权。')
    table('VSM_Out_BatchSummary',[col('SourceID','String',d='四张生产工单编号。')]+[col(n) for n in ['Planned','Released','Manufactured','Shipped','Unmanufactured','Unshipped','Complete']]+[col(n,'Real',time=True,d='有效工时时间，小时；未完成批次Makespan=-1。') for n in ['FirstRelease','LastShipment','Makespan']],True,'期末四张工单响应；仅全批实际发运后Complete=1且给出Makespan。')

def ledger_phase():
    append_assign('VSM_InitializeWIP',[], '') if False else None
    root=ET.fromstring(BEFORE['processes']['VSM_InitializeWIP']);steps=root.find('Steps')
    # Insert grouped accounting after existing entity attributes, before Transfer.
    a=steps.find("Step[@ID='4']");a.find('Exit').set('NextID','6')
    p=Process('temp','初始化来源');p.nextid=6
    p.assign('登记初始库存来源',[(R,'VSM_InitialWIPTable.SourceRow'),(f'{L}[{R}].Received',f'{L}[{R}].Received + {Q}')],connect=False)
    ET.SubElement(p.steps[0],'Exit',Name='Exit',Type='Primary',NextID='5');steps.append(p.steps[0])
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
    for s in STAGES:
        append_assign('VSM_OnEnter'+s+'WIP',[(f'{L}[{R}].{s}In',f'{L}[{R}].{s}In + {Q}')]+([('ModelEntity.VSM_StartTime','TimeNow')] if s=='Stamping' else []),'登记来源位置流入')
        append_assign('VSM_OnExit'+s+'WIP',[(f'{L}[{R}].{s}Out',f'{L}[{R}].{s}Out + {Q}')],'登记来源位置流出')
    p=Process('VSM_OnProductionRelease','两轮生产释放：每轮先L6000后R3200；独立工单P1/P2；单位件；来源行号12–15。','Output@Source_ProductionRelease.Entered')
    p.assign('登记释放序号',[('VSM_ReleaseSequence','VSM_ReleaseSequence + 20')])
    cyc='Math.Floor((VSM_ReleaseSequence-1)/9200)'
    loc='VSM_ReleaseSequence - 9200*'+cyc
    p.assign('识别工单产品',[(R,f'12 + 2*{cyc} + Math.If({loc} <= 6000,0,1)'),(Q,'20'),('ModelEntity.VSM_ProductTypeState',f'{L}[{R}].Product'),('ModelEntity.VSM_ProductionBatchState',f'{L}[{R}].SourceID'),('ModelEntity.VSM_ReleaseTimeHoursState','TimeNow'),('ModelEntity.VSM_TrayIDState','Math.Floor((VSM_ReleaseSequence-1)/20)+1')])
    p.assign('登记工单下达',[(f'{L}[{R}].Received',f'{L}[{R}].Received+{Q}'),(f'{L}[{R}].FirstRelease','TimeNow'),('VSM_LeftReleasedCount',f'VSM_LeftReleasedCount + Math.If(ModelEntity.VSM_ProductTypeState == "Left",{Q},0)'),('VSM_RightReleasedCount',f'VSM_RightReleasedCount + Math.If(ModelEntity.VSM_ProductTypeState == "Right",{Q},0)')]);p.send()
    setp(MODEL+'/Objects/Source_ProductionRelease','Interarrival Time','552000','Seconds')
    print(call('get_diagnostics',modelPath=MODEL))

def snapshot_phase():
    state('VSM_SnapshotSource','Integer',desc='盘点过程内部来源行游标；1–15，按日低频遍历。')
    p=Process('VSM_WriteWIPSnapshot','把15个来源在6处的运行State冻结为输出行；低频日盘点；来源Received-Shipped-Scrapped-各处In+Out应为0。')
    p.assign('从首来源开始',[('VSM_SnapshotSource','1')])
    loopid=p.nextid
    ref=f'{L}[VSM_SnapshotSource]'
    balance=ref+'.Received - '+ref+'.Shipped - '+ref+'.Scrapped - ('+' + '.join(f'{ref}.{s}In - {ref}.{s}Out' for s in STAGES)+')'
    for s in STAGES:
        p.addrow('VSM_Out_WIPSnapshot')
        p.assign('冻结'+s+'盘点',[(f'VSM_Out_WIPSnapshot.{n}',v) for n,v in [('SnapshotTime','TimeNow'),('SourceID',ref+'.SourceID'),('Version','VSM_ModelVersion'),('Product',ref+'.Product'),('Stage','"'+s+'"'),('InitialOrReleased',ref+'.Received'),('Entered',ref+'.'+s+'In'),('Exited',ref+'.'+s+'Out'),('CurrentUnits',ref+'.'+s+'In - '+ref+'.'+s+'Out'),('Shipped',ref+'.Shipped'),('SourceBalance',balance)]])
    p.assign('转到下一来源',[('VSM_SnapshotSource','VSM_SnapshotSource+1')])
    p.step('Decide','继续盘点',dict(DecideType='ConditionBased',ConditionOrProbability='VSM_SnapshotSource <= 15'),[('True','Primary',loopid)])
    p.send()

def historical_run_setup():
    append_assign('VSM_OnShipment',[(f'{L}[{R}].Shipped',f'{L}[{R}].Shipped + {Q}')],'累计来源已发运')
    for s in ['Stamping','Weld2']:setp(MODEL+'/Objects/Server_'+s,'Failure Type','No Failures')
    state('VSM_ClockDay','Integer',desc='已经过的工作日数；整数日边界，不反复相加小数小时。')
    p=Process('VSM_DailyClock','t0及每个有效工作日末在正常同刻事件之后记录盘点；Math.Epsilon使用原生晚优先级，不推进业务时钟。')
    first=p.nextid;p.step('Delay','等待同刻流转完毕',dict(DelayTime='Math.Epsilon',DelayType='ForTime',DelayMultiplier='1'))
    p.execute('输出当日来源盘点','VSM_WriteWIPSnapshot')
    p.assign('进入下一工作日',[('VSM_ClockDay','VSM_ClockDay+1')])
    d=p.step('Decide','仍在本月',dict(DecideType='ConditionBased',ConditionOrProbability='VSM_ClockDay <= 20'))
    p.last=None
    delay=p.step('Delay','等待绝对日末',dict(DelayType='UntilTime',DelayEndTime='VSM_ClockDay * 55200 / 3600',DelayTime='0',DelayMultiplier='1'),connect=False)
    ET.SubElement(d,'Exit',Name='True',Type='Primary',NextID=delay.get('ID'))
    ET.SubElement(delay,'Exit',Name='Exit',Type='Primary',NextID=str(first));p.send()
    timer=MODEL+'/Elements/VSM_DemandClock'
    for n,v in [('Time Offset','0'),('Maximum Events','1'),('Triggered Process Name','VSM_DailyClock'),('Initially Enabled','True')]:setp(timer,n,v)
    call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(RunEndType='RunLength',EndTimeValue=1104000/3600,DisableRandomness=True,StopAtEndOfRun=False)))
    print(call('get_diagnostics',modelPath=MODEL))

F='VSM_Out_FGInventory'
D='VSM_DemandLedger'
A='VSM_Out_ShipmentAllocation'

def demand_schema():
    table(D,[col('DemandID','String',d='日需求唯一编号。',k='property'),col('Product','String',d='Left/Right。',k='property'),col('DueTime','Real',d='每日末到期的有效工时时刻；小时。',time=True,k='property'),col('DemandUnits',k='property')]+[col(n) for n in ['OnTime','Late','Allocated']],False,'40条按日交错L/R需求；运行State由FIFO分配过程更新。Demand-Allocated为未交件数。')
    rows=[]
    for day in range(1,21):
        for code,prod,q in [('L','Left',600),('R','Right',320)]:rows.append(dict(DemandID=f'D{day:02}-{code}',Product=prod,DueTime=str(day*55200/3600),DemandUnits=q))
    call('set_table_data',path=MODEL+'/Tables/'+D,rows=json.dumps(rows),startRow=0,clearExisting=True)
    table(F,[col('SourceRow'),col('SourceID','String',d='库存来源快照。'),col('Product','String',d='产品快照。'),col('OriginalUnits'),col('RemainingUnits',d='可用成品剩余件数运行State；分配扣减；为0后物理实体退出。该表是可变库存账本，其余历史快照不随之改变。'),col('NextRow',d='同产品FIFO链表下一行，0表示队尾；直接寻址。')]+[col(n,'Real',time=True,d='累计有效工时时间，小时；历史入线未知为-1。') for n in ['StartTime','FinishTime']],True,'成品可用库存运行账本：每实体一行，含FIFO链；RemainingUnits是当前值，非历史快照。与ShipmentAllocation共同追溯；复位清空。')
    table(A,[col('DemandID','String',d='被满足的需求编号。'),col('SourceID','String',d='供应来源编号。'),col('Product','String',d='产品编码。'),col('StockRow'),col('Units'),col('OnTime'),col('CTKnown')]+[col(n,'Real',time=True,d='有效工时时间，小时；历史未知的ManufacturingCT/EndToEnd为-1并标CTKnown=0。') for n in ['ShipmentTime','DueTime','ManufacturingCT','FGWait','EndToEnd','InitialRemainingDelivery']],True,'一次库存到需求的实际分配；部分交付分别记录各自件数/时间；冻结的历史记录，不重复累计实体原始20件。')
    table('VSM_Out_DemandFulfillment',[col('DemandID','String',d='需求编号。'),col('Product','String',d='产品。')]+[col(n) for n in ['DemandUnits','OnTime','LateByHorizon','Unfilled','FGAtHorizon','RateDefined']]+[col('DueTime','Real',time=True,d='有效工时到期时刻，小时。'),col('DueDateUnitFillRate','Real',d='准时件数/需求件数；RateDefined=0时=-1，不能称为0%或100%。')],True,'期末逐条需求结果；Demand=OnTime+LateByHorizon+Unfilled；零需求比率未定义。')
    for n,initial in [('VSM_StockRows','0'),('VSM_FGLeftHead','0'),('VSM_FGRightHead','0'),('VSM_FGLeftTail','0'),('VSM_FGRightTail','0'),('VSM_DemandLeftCursor','1'),('VSM_DemandRightCursor','2'),('VSM_AllocProduct','0'),('VSM_AllocDemand','0'),('VSM_AllocStock','0'),('VSM_AllocUnits','0'),('VSM_ResultRow','0')]:state(n,initial=initial,desc='本次运行FIFO或输出游标；初值'+initial+'；分配过程按直接行号同步更新，无等待与随机采样。')
    state('VSM_FGLeftAvailable',desc='当前Left可用成品件数，成品进入时增加、实际分配时扣减。')
    state('VSM_FGRightAvailable',desc='当前Right可用成品件数，成品进入时增加、实际分配时扣减。')

def allocator():
    p=Process('VSM_AllocateDemand','按产品FIFO分配已经到期需求；允许部分交付；零时间串行执行，无Delay；旧积压优先，同刻供应TimeNow<=DueTime记准时。直接行号/链表寻址，不全表搜索。')
    p.assign('从左件开始分配',[('VSM_AllocProduct','1')])
    productid=p.nextid
    p.assign('读取产品游标',[('VSM_AllocDemand','Math.If(VSM_AllocProduct == 1,VSM_DemandLeftCursor,VSM_DemandRightCursor)'),('VSM_AllocStock','Math.If(VSM_AllocProduct == 1,VSM_FGLeftHead,VSM_FGRightHead)')])
    loop=p.nextid
    d1=p.step('Decide','需求行仍存在',dict(ConditionOrProbability='VSM_AllocDemand <= 40'))
    p.last=None;d2=p.step('Decide','需求已到期',dict(ConditionOrProbability=f'{D}[VSM_AllocDemand].DueTime <= TimeNow'),connect=False)
    d1e=ET.SubElement(d1,'Exit',Name='True',Type='Primary',NextID=d2.get('ID'))
    p.last=None;d3=p.step('Decide','本条已足额',dict(ConditionOrProbability=f'{D}[VSM_AllocDemand].Allocated >= {D}[VSM_AllocDemand].DemandUnits'),connect=False)
    ET.SubElement(d2,'Exit',Name='True',Type='Primary',NextID=d3.get('ID'))
    p.last=None;advance=p.assign('转到下日需求',[('VSM_AllocDemand','VSM_AllocDemand+2')],connect=False)
    ET.SubElement(d3,'Exit',Name='True',Type='Primary',NextID=advance.get('ID'));ET.SubElement(advance,'Exit',Name='Exit',Type='Primary',NextID=str(loop))
    p.last=None;d4=p.step('Decide','是否有可用库存',dict(ConditionOrProbability='VSM_AllocStock > 0'),connect=False)
    ET.SubElement(d3,'Exit',Name='False',Type='Alternate',NextID=d4.get('ID'))
    p.last=None
    cal=p.assign('确定部分交付数量',[('VSM_AllocUnits',f'Math.Min({D}[VSM_AllocDemand].DemandUnits-{D}[VSM_AllocDemand].Allocated,{F}[VSM_AllocStock].RemainingUnits)')],connect=False)
    ET.SubElement(d4,'Exit',Name='True',Type='Primary',NextID=cal.get('ID'))
    st=f'{F}[VSM_AllocStock]';de=f'{D}[VSM_AllocDemand]';sr=f'{L}[{st}.SourceRow]';u='VSM_AllocUnits';ont=f'TimeNow <= {de}.DueTime'
    p.assign('登记需求和来源交付',[(de+'.Allocated',de+'.Allocated+'+u),(de+'.OnTime',de+f'.OnTime+Math.If({ont},{u},0)'),(de+'.Late',de+f'.Late+Math.If({ont},0,{u})'),(st+'.RemainingUnits',st+'.RemainingUnits-'+u),(sr+'.Shipped',sr+'.Shipped+'+u),(sr+'.LastShipment','TimeNow'),(sr+'.FGStagingOut',sr+'.FGStagingOut+'+u),('VSM_ShippedUnitCount','VSM_ShippedUnitCount+'+u),('VSM_ShippedLeftUnitCount',f'VSM_ShippedLeftUnitCount+Math.If(VSM_AllocProduct == 1,{u},0)'),('VSM_ShippedRightUnitCount',f'VSM_ShippedRightUnitCount+Math.If(VSM_AllocProduct == 2,{u},0)'),('VSM_FGLeftAvailable',f'VSM_FGLeftAvailable-Math.If(VSM_AllocProduct == 1,{u},0)'),('VSM_FGRightAvailable',f'VSM_FGRightAvailable-Math.If(VSM_AllocProduct == 2,{u},0)'),('VSM_FGStagingWIP','VSM_FGStagingWIP-'+u),('VSM_FGStagingExitedUnits','VSM_FGStagingExitedUnits+'+u),('VSM_FGStagingLeftWIP',f'VSM_FGStagingLeftWIP-Math.If(VSM_AllocProduct == 1,{u},0)'),('VSM_FGStagingRightWIP',f'VSM_FGStagingRightWIP-Math.If(VSM_AllocProduct == 2,{u},0)')])
    p.addrow(A)
    p.assign('冻结本次部分交付',[(A+'.'+n,v) for n,v in [('DemandID',de+'.DemandID'),('SourceID',st+'.SourceID'),('Product',st+'.Product'),('StockRow','VSM_AllocStock'),('Units',u),('OnTime',f'Math.If({ont},1,0)'),('CTKnown',f'Math.If({st}.StartTime>=0,1,0)'),('ShipmentTime','TimeNow'),('DueTime',de+'.DueTime'),('ManufacturingCT',f'Math.If({st}.StartTime>=0,{st}.FinishTime-{st}.StartTime,-1)'),('FGWait','TimeNow-'+st+'.FinishTime'),('EndToEnd',f'Math.If({st}.StartTime>=0,TimeNow-{st}.StartTime,-1)'),('InitialRemainingDelivery',f'Math.If({st}.StartTime<0,TimeNow,-1)')]])
    p.assign('跳过耗尽库存',[('VSM_AllocStock',f'Math.If({st}.RemainingUnits == 0,{st}.NextRow,VSM_AllocStock)')])
    ET.SubElement(p.last,'Exit',Name='Exit',Type='Primary',NextID=str(loop));p.last=None
    save=p.assign('保存产品游标',[('VSM_DemandLeftCursor','Math.If(VSM_AllocProduct==1,VSM_AllocDemand,VSM_DemandLeftCursor)'),('VSM_DemandRightCursor','Math.If(VSM_AllocProduct==2,VSM_AllocDemand,VSM_DemandRightCursor)'),('VSM_FGLeftHead','Math.If(VSM_AllocProduct==1,VSM_AllocStock,VSM_FGLeftHead)'),('VSM_FGRightHead','Math.If(VSM_AllocProduct==2,VSM_AllocStock,VSM_FGRightHead)'),('VSM_AllocProduct','VSM_AllocProduct+1')],connect=False)
    for s in [d1,d2,d4]:ET.SubElement(s,'Exit',Name='False',Type='Alternate',NextID=save.get('ID'))
    p.step('Decide','继续右件分配',dict(ConditionOrProbability='VSM_AllocProduct <= 2'),[('True','Primary',productid)]);p.send()

def fg_arrival():
    # Keep established entry accounting and append the new inventory registration.
    root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_OnEnterFGStagingWIP')['xml'])
    old=list(root.find('Steps'));p=Process('VSM_OnEnterFGStagingWIP','进入成品后建立数量账本/FIFO链；初始成品从0可用；按剩余件数分配，全部交付后才退出物理实体。')
    p.steps.clear()
    for s in old:p.steps.append(s)
    p.nextid=max(int(s.get('ID')) for s in old)+1;p.last=old[-1]
    p.assign('登记成品可用量',[('VSM_StockRows','VSM_StockRows+1'),('ModelEntity.VSM_StockRow','VSM_StockRows'),('ModelEntity.VSM_FinishTime','Math.Max(ModelEntity.VSM_FinishTime,0)'),('VSM_FGLeftAvailable',f'VSM_FGLeftAvailable+Math.If(ModelEntity.VSM_ProductTypeState=="Left",{Q},0)'),('VSM_FGRightAvailable',f'VSM_FGRightAvailable+Math.If(ModelEntity.VSM_ProductTypeState=="Right",{Q},0)')])
    p.addrow(F)
    p.assign('冻结成品来源',[(F+'.'+n,v) for n,v in [('SourceRow',R),('SourceID',f'{L}[{R}].SourceID'),('Product','ModelEntity.VSM_ProductTypeState'),('OriginalUnits',Q),('RemainingUnits',Q),('NextRow','0'),('StartTime','ModelEntity.VSM_StartTime'),('FinishTime','ModelEntity.VSM_FinishTime')]])
    tail='Math.If(ModelEntity.VSM_ProductTypeState=="Left",VSM_FGLeftTail,VSM_FGRightTail)'
    d=p.step('Decide','存在前一库存行',dict(ConditionOrProbability=tail+'>0'))
    p.last=None;a=p.assign('连接产品FIFO队尾',[(f'{F}[{tail}].NextRow','VSM_StockRows')],connect=False)
    ET.SubElement(d,'Exit',Name='True',Type='Primary',NextID=a.get('ID'))
    mergeid=p.nextid
    p.assign('维护产品首尾指针',[('VSM_FGLeftHead','Math.If(ModelEntity.VSM_ProductTypeState=="Left" && VSM_FGLeftHead==0,VSM_StockRows,VSM_FGLeftHead)'),('VSM_FGRightHead','Math.If(ModelEntity.VSM_ProductTypeState=="Right" && VSM_FGRightHead==0,VSM_StockRows,VSM_FGRightHead)'),('VSM_FGLeftTail','Math.If(ModelEntity.VSM_ProductTypeState=="Left",VSM_StockRows,VSM_FGLeftTail)'),('VSM_FGRightTail','Math.If(ModelEntity.VSM_ProductTypeState=="Right",VSM_StockRows,VSM_FGRightTail)')])
    ET.SubElement(d,'Exit',Name='False',Type='Alternate',NextID=str(mergeid))
    p.execute('补交已到期需求','VSM_AllocateDemand');p.send()
    Process('VSM_OnExitFGStagingWIP','物理实体只在库存剩余为0时退出；数量已在分配时扣减，此处不得重复扣20件。').send()
    Process('VSM_OnShipment','Sink仅回收已经完全分配的空库存实体；实际件数/时间已由需求分配过程记账，禁止重复统计。').send()
    setp(MODEL+'/Objects/Server_FG_Staging','Initial Capacity','1000000')
    setp(MODEL+'/Objects/Server_FG_Staging','Transfer-Out Condition',f'ModelEntity.VSM_StockRow > 0 && {F}[ModelEntity.VSM_StockRow].RemainingUnits == 0')
    # The only changed physical route is Assembly2 -> FG -> Sink.
    links=call('list_children',path=MODEL+'/Links')['items']
    if any(x['name']=='Link_Assembly2ToShipping' for x in links):call('delete_item',path=MODEL+'/Links/Link_Assembly2ToShipping')
    for start,end,name in [('Output@Server_Assembly2','Input@Server_FG_Staging','Link_Assembly2ToFGStaging'),('Output@Server_FG_Staging','Input@Sink_Shipping','Link_FGStagingToShipping')]:
        if not any(x['name']==name for x in links):
            r=call('create_link',modelPath=MODEL,type='Connector',startNode=start,endNode=end)
            print('LINK',r)
            # MCP returns the concrete generated path; rename narrowly through instance Name.
            path=r.get('path') or r.get('link',{}).get('path')
            if path:setp(path,'产品名称',name)

def finish_hooks():
    root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_OnExitAssembly2WIP')['xml'])
    old=list(root.find('Steps'));p=Process('VSM_OnExitAssembly2WIP','Assembly2离开是制造完成边界；按实际件数记录来源完工和CT，然后去成品等待。')
    p.steps.clear()
    for s in old:p.steps.append(s)
    p.nextid=max(int(s.get('ID')) for s in old)+1;p.last=old[-1]
    p.assign('登记制造完成', [('ModelEntity.VSM_FinishTime','TimeNow'),(f'{L}[{R}].Manufactured',f'{L}[{R}].Manufactured+{Q}')])
    p.addrow('VSM_Out_FlowTimes')
    p.assign('冻结制造周期', [('VSM_Out_FlowTimes.'+n,v) for n,v in [('Event','"Manufactured"'),('SourceID',f'{L}[{R}].SourceID'),('Product','ModelEntity.VSM_ProductTypeState'),('Units',Q),('StartTime','ModelEntity.VSM_StartTime'),('FinishTime','TimeNow'),('ObservationTime','TimeNow'),('ManufacturingCT','Math.If(ModelEntity.VSM_StartTime>=0,TimeNow-ModelEntity.VSM_StartTime,-1)'),('RemainingCT','Math.If(ModelEntity.VSM_StartTime<0,TimeNow,-1)'),('CTKnown','Math.If(ModelEntity.VSM_StartTime>=0,1,0)'),('Censored','0')]])
    p.send()

def demand_clock():
    p=Process('VSM_DailyClock','每个有效工作日末先等待同刻正常完工/流转，再分配/盘点；第20日原生EndRun使当前时刻所有事件完成后结束，无额外时间偏移。')
    first=p.nextid
    p.step('Delay','等待同刻流转完毕',dict(DelayTime='Math.Epsilon',DelayType='ForTime',DelayMultiplier='1'))
    p.execute('分配到期需求','VSM_AllocateDemand');p.execute('输出当日来源盘点','VSM_WriteWIPSnapshot')
    p.assign('进入下一工作日',[('VSM_ClockDay','VSM_ClockDay+1')])
    d=p.step('Decide','仍有工作日',dict(ConditionOrProbability='VSM_ClockDay <= 20'));p.last=None
    delay=p.step('Delay','等待绝对日末',dict(DelayType='UntilTime',DelayEndTime='VSM_ClockDay * 55200 / 3600',DelayTime='0',DelayMultiplier='1'),connect=False)
    ET.SubElement(d,'Exit',Name='True',Type='Primary',NextID=delay.get('ID'));ET.SubElement(delay,'Exit',Name='Exit',Type='Primary',NextID=str(first));p.last=None
    final=p.execute('冻结期末结果','VSM_FinalOutputs');ET.SubElement(d,'Exit',Name='False',Type='Alternate',NextID=final.get('ID'))
    p.step('EndRun','完成本月当前事件');p.send()
    call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(RunEndType='Infinite',DisableRandomness=True,StopAtEndOfRun=False)))

def final_outputs():
    p=Process('VSM_FinalOutputs','期末输出需求、批次和未完工删失记录；使用运行State冻结，不改物流，不抽随机数。')
    p.execute('补齐期末需求','VSM_AllocateDemand')
    p.assign('从首需求开始',[('VSM_ResultRow','1')]);loop=p.nextid
    p.addrow('VSM_Out_DemandFulfillment');r=f'{D}[VSM_ResultRow]'
    p.assign('冻结需求期末结果',[('VSM_Out_DemandFulfillment.'+n,v) for n,v in [('DemandID',r+'.DemandID'),('Product',r+'.Product'),('DemandUnits',r+'.DemandUnits'),('OnTime',r+'.OnTime'),('LateByHorizon',r+'.Late'),('Unfilled',r+'.DemandUnits-'+r+'.Allocated'),('FGAtHorizon',f'Math.If({r}.Product=="Left",VSM_FGLeftAvailable,VSM_FGRightAvailable)'),('RateDefined',f'Math.If({r}.DemandUnits>0,1,0)'),('DueTime',r+'.DueTime'),('DueDateUnitFillRate',f'Math.If({r}.DemandUnits>0,{r}.OnTime/Math.Max({r}.DemandUnits,1),-1)')]])
    p.assign('下一需求结果',[('VSM_ResultRow','VSM_ResultRow+1')])
    d=p.step('Decide','还有需求结果',dict(ConditionOrProbability='VSM_ResultRow<=40'),[('True','Primary',loop)]);p.last=None
    a=p.assign('从首生产工单开始',[('VSM_ResultRow','12')],connect=False);ET.SubElement(d,'Exit',Name='False',Type='Alternate',NextID=a.get('ID'));loop=p.nextid
    p.addrow('VSM_Out_BatchSummary');r=f'{L}[VSM_ResultRow]'
    p.assign('冻结工单响应',[('VSM_Out_BatchSummary.'+n,v) for n,v in [('SourceID',r+'.SourceID'),('Planned',r+'.Planned'),('Released',r+'.Received'),('Manufactured',r+'.Manufactured'),('Shipped',r+'.Shipped'),('Unmanufactured',r+'.Received-'+r+'.Manufactured'),('Unshipped',r+'.Received-'+r+'.Shipped'),('Complete',f'Math.If({r}.Shipped=={r}.Planned,1,0)'),('FirstRelease',r+'.FirstRelease'),('LastShipment',f'Math.If({r}.Shipped>0,{r}.LastShipment,-1)'),('Makespan',f'Math.If({r}.Shipped=={r}.Planned,{r}.LastShipment-{r}.FirstRelease,-1)')]])
    p.assign('下一工单结果',[('VSM_ResultRow','VSM_ResultRow+1')]);last=p.step('Decide','还有工单结果',dict(ConditionOrProbability='VSM_ResultRow<=15'),[('True','Primary',loop)]);p.last=None
    search=p.step('Search','期末遍历未完工实体',dict(CollectionType='EntityPopulation',EntityType='DefaultEntity',MatchCondition='Candidate.ModelEntity.VSM_FinishTime < 0 && Candidate.ModelEntity.VSM_SourceRow > 0',SearchType='Forward',Limit='Infinity',TokenWaitAction='WaitUntilNewTokenProcessingCompleted'),connect=False)
    ET.SubElement(last,'Exit',Name='False',Type='Alternate',NextID=search.get('ID'));p.last=None
    add=p.addrow('VSM_Out_FlowTimes');ET.SubElement(search,'Exit',Name='Found',Type='Alternate',NextID=add.get('ID'))
    p.assign('冻结期末未完工样本',[('VSM_Out_FlowTimes.'+n,v) for n,v in [('Event','"UnmanufacturedAtHorizon"'),('SourceID',f'{L}[{R}].SourceID'),('Product','ModelEntity.VSM_ProductTypeState'),('Units',Q),('StartTime','ModelEntity.VSM_StartTime'),('FinishTime','-1'),('ObservationTime','TimeNow'),('ManufacturingCT','-1'),('RemainingCT','-1'),('CTKnown','Math.If(ModelEntity.VSM_StartTime>=0,1,0)'),('Censored','1')]])
    p.send()

def quantity_phase():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)
    state('VSM_EntityUnitQuantity',initial='20',desc='一个标准计算实体代表的件数；正式模型20，10件尾批仍按输入表单列；逐件参照验证可改1且须同时重配初始WIP表。非真实托盘容量。')
    p=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_OnProductionRelease')['xml'])
    for propnode in p.iter('Property'):
        if propnode.get('Name')=='NewValue' and propnode.text=='VSM_ReleaseSequence + 20':propnode.text='VSM_ReleaseSequence + VSM_EntityUnitQuantity'
        if propnode.get('Name')=='AssignmentsNewValue' and propnode.text=='20':propnode.text='VSM_EntityUnitQuantity'
        if propnode.get('Name')=='AssignmentsNewValue' and propnode.text=='Math.Floor((VSM_ReleaseSequence-1)/20)+1':propnode.text='Math.Floor((VSM_ReleaseSequence-1)/VSM_EntityUnitQuantity)+1'
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(p,encoding='unicode'))
    setp(MODEL+'/Objects/Source_ProductionRelease','Entities Per Arrival','9200 / VSM_EntityUnitQuantity')
    final_outputs()
    print(call('get_diagnostics',modelPath=MODEL))

def demand_phase():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)
    demand_schema();allocator();finish_hooks();fg_arrival();final_outputs();demand_clock()
    print(call('get_diagnostics',modelPath=MODEL))

def service_phase():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)
    state('VSM_EnableSetups',initial='1',desc='换型机制开关：1启用产品变更换型、首件不加准备；0用于确定性回归。')
    state('VSM_OperationStartTime','Real',entity=True,time=True,desc='当前工序分配设备容量的有效工时时刻；每次开始覆盖。')
    table('VSM_Out_OperationLog',[col('Resource','String',d='设备名称。'),col('SourceID','String',d='来源编号。'),col('Product','String',d='产品。'),col('Units')]+[col(n,'Real',time=True,d='有效工时时刻或持续时间，小时；ServiceTime及SetupTime为开始时冻结的样本，完成时原样输出。') for n in ['StartTime','FinishTime','ServiceTime','SetupTime','ElapsedTime']],True,'每次工序完成记录；ElapsedTime包含加工、换型及加工期间故障维修；不重新抽样。换型作为同一设备原生Processing Time的冻结组成，与加工一起支持原生故障暂停/续作。')
    table('VSM_Out_ResourceEvents',[col('Resource','String',d='设备名称。'),col('Event','String',d='Failed或Repaired。'),col('EventTime','Real',time=True,d='累计有效工时时刻，小时。')],True,'原生故障/维修完成事件；仅观测，不更改容量、维修或随机流。')
    for ix,(s,mean,setup) in enumerate([('Stamping',1,1),('Weld1',39,.167),('Weld2',46,.167),('Assembly1',62,0),('Assembly2',40,0)]):
        last='VSM_'+s+'LastProduct';state(last,'String','',desc='该设备上一次开始加工的产品；初始空，不加首件换型；仅L/R变更时计换型。')
        count='VSM_'+s+'SetupCount';state(count,desc='该设备产品L/R变更的累计换型次数，首件不计。')
        p=Process('VSM_Prepare'+s,'设备容量已分配后，先冻结每件独立指数加工样本总和，再按前后产品冻结换型时间；随后更新设备产品，原生Server负责占用、故障暂停及剩余时间恢复。')
        p.assign('冻结本工序时间',[('ModelEntity.VSM_OperationStartTime','TimeNow'),('ModelEntity.VSM_ServiceTime',f'Math.SumOfSamples(Random.Exponential({mean},{101+ix}),{Q}) / 3600'),('ModelEntity.VSM_SetupTime',f'Math.If(VSM_EnableSetups==1 && {last}!="" && {last}!=ModelEntity.VSM_ProductTypeState,{setup},0)')])
        p.assign('登记本次设备产品',[(count,count+'+Math.If(ModelEntity.VSM_SetupTime>0,1,0)'),(last,'ModelEntity.VSM_ProductTypeState')]);p.send()
        p=Process('VSM_Complete'+s,'工序完成只记录冻结时间与实际经过时间，故障/恢复不会重新抽样。')
        p.addrow('VSM_Out_OperationLog')
        p.assign('冻结工序运行证据',[('VSM_Out_OperationLog.'+n,v) for n,v in [('Resource','"Server_'+s+'"'),('SourceID',f'{L}[{R}].SourceID'),('Product','ModelEntity.VSM_ProductTypeState'),('Units',Q),('StartTime','ModelEntity.VSM_OperationStartTime'),('FinishTime','TimeNow'),('ServiceTime','ModelEntity.VSM_ServiceTime'),('SetupTime','ModelEntity.VSM_SetupTime'),('ElapsedTime','TimeNow-ModelEntity.VSM_OperationStartTime')]]);p.send()
        ob=MODEL+'/Objects/Server_'+s
        setp(ob,'BeforeProcessingAddOnProcess','VSM_Prepare'+s)
        setp(ob,'AfterProcessingAddOnProcess','VSM_Complete'+s)
        setp(ob,'Processing Time','ModelEntity.VSM_ServiceTime + ModelEntity.VSM_SetupTime','Hours')
        setp(ob,'说明',f'{s}：单件均值{mean}秒，SCV=1；开始时独立抽样累加实际件数并冻结。前后产品变化换型{setup}小时，首件不加。换型和纯加工合并占用同一原生设备；故障暂停后继续剩余时间。统计ElapsedTime包含维修，SetupTime单列；不单独显示原生Setup资源状态。')
    for s,mttf,stream in [('Stamping',5.666666666666667,201),('Weld2',4,211)]:
        ob=MODEL+'/Objects/Server_'+s
        setp(ob,'Failure Type','Calendar Time Based')
        setp(ob,'Uptime Between Failures',f'Random.Exponential({mttf},{stream})','Hours')
        setp(ob,'Time To Repair',f'Random.Exponential(1,{stream+1})','Hours')
        for ev in ['Failed','Repaired']:
            name='VSM_'+s+ev;p=Process(name,'原生故障事件观测；记录时刻，不改变资源容量、恢复流程或随机流。');p.addrow('VSM_Out_ResourceEvents')
            p.assign('记录设备'+('故障' if ev=='Failed' else '修复'),[('VSM_Out_ResourceEvents.Resource','"Server_'+s+'"'),('VSM_Out_ResourceEvents.Event','"'+ev+'"'),('VSM_Out_ResourceEvents.EventTime','TimeNow')]);p.send();setp(ob,ev,name)
    call('set_run_setup',modelPath=MODEL,settingsJson=json.dumps(dict(DisableRandomness=False)))
    print(call('get_diagnostics',modelPath=MODEL))

if __name__=='__main__':
    {'schema':schema_phase,'ledger':ledger_phase,'snapshot':snapshot_phase,'historical':historical_run_setup,'demand':demand_phase,'service':service_phase,'quantity':quantity_phase}[sys.argv[1]]()
