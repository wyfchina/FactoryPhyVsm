from build_issue06 import *

def install():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)
    table('VSM_Out_RunSummary',[col('ObservationTime','Real',time=True,d='期末累计有效工时时刻，小时。')]+[col(n,d='原生实体计数或按件计数；Native前缀以实体为单位，其余数量以件计。') for n in ['NativeCreated','NativeDestroyed','NativeInSystem','InitialUnits','ReleasedUnits','ShippedUnits','CurrentUnits','Balance']]+[col(s+'Allocated',d='期末设备原生已分配容量；1表示仍有合法未完工作，0表示已释放。') for s in STAGES],True,'同刻物流事件处理后冻结的期末原生实体/资源和件数计数；两种计数单位不能相互替代。')
    p=Process('VSM_WriteRunSummary','日末分配及同刻物理退出处理完成后记录原生实体/资源和全局件数State；仅观测，不改变流转。')
    p.addrow('VSM_Out_RunSummary')
    init='VSM_InitialLeftUnitCount+VSM_InitialRightUnitCount';released='VSM_LeftReleasedCount+VSM_RightReleasedCount';current='+'.join('VSM_'+s+'WIP' for s in STAGES)
    p.assign('冻结原生计数和件数',[('VSM_Out_RunSummary.'+n,v) for n,v in [('ObservationTime','TimeNow'),('NativeCreated','DefaultEntity.Population.NumberCreated'),('NativeDestroyed','DefaultEntity.Population.NumberDestroyed'),('NativeInSystem','DefaultEntity.Population.NumberInSystem'),('InitialUnits',init),('ReleasedUnits',released),('ShippedUnits','VSM_ShippedUnitCount'),('CurrentUnits',current),('Balance',init+'+'+released+'-VSM_ShippedUnitCount-('+current+')')]+[(s+'Allocated',('Server_FG_Staging' if s=='FGStaging' else 'Server_'+s)+'.Capacity.Allocated') for s in STAGES]]);p.send()
    root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_FinalOutputs')['xml'])
    steps=root.find('Steps');first=steps[0];sid=max(int(s.get('ID')) for s in steps)+1
    pr=Process('temp','summary');pr.nextid=sid;pr.execute('记录原生实体资源守恒','VSM_WriteRunSummary')
    ET.SubElement(pr.steps[0],'Exit',Name='Exit',Type='Primary',NextID=first.get('ID'));steps.append(pr.steps[0]);root.set('BeginStepID',str(sid))
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
    root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_DailyClock')['xml']);steps=root.find('Steps')
    allocate=next(s for s in steps if s.get('Name')=='分配到期需求');ex=allocate.find('Exit');dest=ex.get('NextID');sid=max(int(s.get('ID')) for s in steps)+1
    pr=Process('temp','same time');pr.nextid=sid;pr.step('Delay','等待已交实体退出',dict(DelayTime='Math.Epsilon',DelayType='ForTime',DelayMultiplier='1'))
    ET.SubElement(pr.steps[0],'Exit',Name='Exit',Type='Primary',NextID=dest);steps.append(pr.steps[0]);ex.set('NextID',str(sid))
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
    print(call('get_diagnostics',modelPath=MODEL))

if __name__=='__main__':install()
