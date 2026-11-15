from build_issue06 import *
import hashlib

def main():
    p=ROOT/'outputs/vsm-michigan-steel-baseline/models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx'
    output=dict(capturedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),identity=call('get_active_model'),properties=props(MODEL,'VSM_ModelVersion,VSM_BaselineStage,说明'),runSetup=call('get_run_setup',modelPath=MODEL),diagnostics=call('get_diagnostics',modelPath=MODEL),userV011File=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),processes={},tables={},states={},objects={},elements={})
    translations={'WIPSnapshot':'盘点快照','FlowTimes':'周期记录','BatchSummary':'批次结果','FGInventory':'成品库存','ShipmentAllocation':'交付分配','DemandFulfillment':'需求结果','OperationLog':'工序记录','ResourceEvents':'设备事件','RunSummary':'运行摘要'}
    for pr in call('list_children',path=MODEL+'/Processes')['items']:
        if not pr['name'].startswith('VSM_'):continue
        root=ET.fromstring(call('get_process_xml',path=MODEL+'/Processes/'+pr['name'])['xml']);changed=False
        for s in root.find('Steps'):
            if s.get('Type')=='AddRow':
                old=s.get('Name');new=old
                for en,zh in translations.items():new=new.replace(en,zh)
                if old!=new:s.set('Name',new);s.set('Description',new+'；建立新输出行并绑定当前令牌/库存实体，后续Assign冻结事件时状态值。');changed=True
        if changed:call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
        output['processes'][pr['name']]=call('get_process_xml',path=MODEL+'/Processes/'+pr['name'])['xml']
    for ta in call('list_children',path=MODEL+'/Tables')['items']:
        name=ta['name'];output['tables'][name]=call('get_table_data',path=MODEL+'/Tables/'+name,offset=0,limit=100)
    for root in [MODEL,'/Project/ModelEntity']:
        output['states'][root]={x['name']:props(root+'/States/'+x['name']) for x in call('list_children',path=root+'/States')['items'] if x['name'].startswith('VSM_')}
    for s in STAGES:
        name='Server_FG_Staging' if s=='FGStaging' else 'Server_'+s
        output['objects'][name]=props(MODEL+'/Objects/'+name,'Processing Time,Initial Capacity,Failure Type,Uptime Between Failures,Time To Repair,BeforeProcessingAddOnProcess,AfterProcessingAddOnProcess,Entered,Exited,Transfer-Out Constraints,Transfer-Out Condition,说明')
    output['objects']['Source_ProductionRelease']=props(MODEL+'/Objects/Source_ProductionRelease','Interarrival Time,Entities Per Arrival,Maximum Arrivals')
    for el in call('list_children',path=MODEL+'/Elements')['items']:
        if el['name']=='VSM_DemandClock':output['elements'][el['name']]=props(MODEL+'/Elements/'+el['name'])
    output['diagnostics']=call('get_diagnostics',modelPath=MODEL)
    (EVIDENCE/'issue06-V012-native-design-manifest.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(dict(version='VSM_V0.12_FlowDemandLedgerCandidate',processes=len(output['processes']),tables=len(output['tables']),diagnostics=output['diagnostics'],userV011Unchanged=output['userV011File']['sha256'].upper()=='D9EBA4337CBFBD7AAF7E9D03A8295B4715D9C831146BE789B7BB28670BFC19CB'))

if __name__=='__main__':main()
