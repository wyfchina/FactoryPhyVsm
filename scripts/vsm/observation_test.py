from acceptance_run import *
import datetime

def main():
    stop();names=['VSM_WriteWIPSnapshot']+['VSM_Complete'+s for s in STAGES[:-1]]+['VSM_'+s+e for s in ['Stamping','Weld2'] for e in ['Failed','Repaired']]
    saved={n:call('get_process_xml',path=MODEL+'/Processes/'+n)['xml'] for n in names}
    try:
        for n,xml in saved.items():
            root=ET.fromstring(xml);root.find('Steps').clear();root.attrib.pop('BeginStepID',None)
            call('set_process_xml',modelPath=MODEL,xml=ET.tostring(root,encoding='unicode'))
        out=run('issue06-M05-observation-disabled',[L,D,A,F,'VSM_Out_RunSummary','VSM_Out_FlowTimes','VSM_Out_BatchSummary'])
        ref=json.loads((EVIDENCE/'issue06-V012-final-random-rep20261114.json').read_text(encoding='utf-8'))
        assert out['tables']=={k:ref['tables'][k] for k in out['tables']}
        result=dict(businessOutputsIdentical=True,referenceStatus=ref['status'],observationDisabledStatus=out['status'],disabledObservers=names)
        (EVIDENCE/'issue06-observation-neutrality.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        stop()
        for n,xml in saved.items():call('set_process_xml',modelPath=MODEL,xml=xml)
    print('M05 PASSED; observers restored')

if __name__=='__main__':main()
