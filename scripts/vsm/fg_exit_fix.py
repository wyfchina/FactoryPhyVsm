from build_issue06 import *

def install():
    if call('get_run_status',modelPath=MODEL)['isInRunMode']:call('stop_model',modelPath=MODEL)
    ensure('Events','VSM_InventoryAllocated','Event')
    # Event instances expose localized generic descriptions.
    ep=MODEL+'/Events/VSM_InventoryAllocated'
    rr=props(ep);dn=next(x['name'] for x in rr['items'] if x['name'] in ['描述','说明','Description'])
    setp(ep,dn,'一次FIFO分配完成后的通知；各成品等待令牌以自身库存行RemainingUnits==0过滤，不轮询或全表搜索。')
    p=Process('VSM_AwaitFGAllocation','成品已完成零时间处理后，先检查自身库存行，再等待分配事件；只在自身剩余件数为0时结束等待，由Server原生流程释放容量并进入Sink。先检查再等待，防止通知先发生而漏唤醒。')
    d=p.step('Decide','本库存是否尚未交完',dict(ConditionOrProbability='VSM_Out_FGInventory.RemainingUnits > 0'))
    p.last=None;w=p.step('Wait','等待本库存交完',dict(EventName='VSM_InventoryAllocated',EventCondition='VSM_Out_FGInventory.RemainingUnits == 0',TokenWaitAction='WaitUntilAnyEvent'),connect=False)
    ET.SubElement(d,'Exit',Name='True',Type='Primary',NextID=w.get('ID'));p.send()
    ob=MODEL+'/Objects/Server_FG_Staging'
    setp(ob,'AfterProcessingAddOnProcess','VSM_AwaitFGAllocation')
    setp(ob,'Transfer-Out Constraints','Default')
    setp(ob,'说明','可用成品暂存：零加工、足够大容量，不代表制造资源。库存实体绑定自身Output库存行，AfterProcessing按事件等待剩余件数归零；部分交付继续保留，全部分配后由原生Server释放容量再入Sink。实际件数只在分配时记账，Sink仅回收空实体。')
    root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_AllocateDemand')['xml']);steps=root.find('Steps')
    if not any(s.get('Type')=='Fire' for s in steps):
        d=next(s for s in steps if s.get('Name')=='继续右件分配');sid=max(int(s.get('ID')) for s in steps)+1
        p=Process('tmp','fire');p.nextid=sid;p.step('Fire','通知库存分配完成',dict(EventName='VSM_InventoryAllocated'))
        steps.append(p.steps[0]);ET.SubElement(d,'Exit',Name='False',Type='Alternate',NextID=str(sid))
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
    root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/VSM_OnEnterFGStagingWIP')['xml'])
    for s in root.find('Steps'):
        if s.get('Type')=='AddRow' and s.find("Properties/Property[@Name='TableName']").text==F:s.find("Properties/Property[@Name='ObjectType']").text='AssociatedObject'
    call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
    print(call('get_diagnostics',modelPath=MODEL))

if __name__=='__main__':install()
