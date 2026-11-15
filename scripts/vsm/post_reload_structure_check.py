"""Read-only native design and parameter comparison after user reload."""
import hashlib
from native import *

def canonical_xml(s):
    root=ET.fromstring(s)
    for node in root.iter():
        if node.text and not node.text.strip():node.text=None
        if node.tail and not node.tail.strip():node.tail=None
    return ET.tostring(root,encoding='unicode')

def main():
    ref=json.loads((EVIDENCE/'issue06-V012-native-design-manifest.json').read_text(encoding='utf-8'))
    checks=[]
    for n,xml in ref['processes'].items():
        live=call('get_process_xml',path=MODEL+'/Processes/'+n)['xml']
        checks.append(dict(target='Processes/'+n,passed=canonical_xml(live)==canonical_xml(xml)))
    for n,t in ref['tables'].items():
        live=call('get_table_data',path=MODEL+'/Tables/'+n,offset=0,limit=100)
        expected=[(x['name'],x['columnKind'],x['type'],x['description']) for x in t['columnDetails']]
        actual=[(x['name'],x['columnKind'],x['type'],x['description']) for x in live['columnDetails']]
        checks.append(dict(target='Tables/'+n+'/schema',passed=actual==expected))
        properties=[x['name'] for x in t['columnDetails'] if x['columnKind']=='property']
        if properties:
            e=[{k:v for k,v in dict(zip(t['columns'],r)).items() if k in properties} for r in t['rows']]
            a=[{k:v for k,v in dict(zip(live['columns'],r)).items() if k in properties} for r in live['rows']]
            checks.append(dict(target='Tables/'+n+'/input',passed=a==e))
        for x in t['columnDetails']:
            if x['type']=='Discrete' and ('时间' in x['description'] or x['name'].endswith('Time') or x['name'] in ['DueTime','SnapshotTime']):
                q=props(MODEL+'/Tables/'+n+'/Columns/'+x['name'],'单位类型,描述')
                checks.append(dict(target='Tables/'+n+'/'+x['name']+'/TimeUnit',passed=any(v['name']=='单位类型' and v['value']=='Time' for v in q['items'])))
    for root,states in ref['states'].items():
        for n,p in states.items():
            live=props(root+'/States/'+n)
            e=[(x['name'],x['value']) for x in p['items']]
            a=[(x['name'],x['value']) for x in live['items']]
            checks.append(dict(target=root+'/States/'+n,passed=a==e))
    diag=call('get_diagnostics',modelPath=MODEL)
    f=ROOT/'outputs/vsm-michigan-steel-baseline/models/VSM_MichiganSteel_V0.12_FlowDemandLedgerCandidate.spfx'
    result=dict(checks=checks,diagnostics=diag,modelSHA256=hashlib.sha256(f.read_bytes()).hexdigest(),allPassed=all(x['passed'] for x in checks) and diag['errorCount']==0)
    (EVIDENCE/'issue06-persistence-structure-readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('structural checks',len(checks),'failed',[x for x in checks if not x['passed']], 'diagnostics',diag)
    assert result['allPassed']

if __name__=='__main__':main()
