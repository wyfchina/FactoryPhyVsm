"""Run only after the user confirms saving, closing and reopening V0.12."""
import zipfile
import hashlib
from acceptance_run import *

def main():
    model_file=ROOT/'outputs/vsm-michigan-steel-baseline/models/VSM_MichiganSteel_V0.12_FlowDemandLedgerCandidate.spfx'
    if not model_file.is_file():raise RuntimeError('User-saved V0.12 package is not present; do not save on their behalf')
    with zipfile.ZipFile(model_file) as z:
        project=z.read('Project.xml').decode('utf-8-sig')
        assert 'VSM_V0.12_FlowDemandLedgerCandidate' in project
    ident=props(MODEL,'VSM_ModelVersion,VSM_BaselineStage')
    assert any(x['value']=='VSM_V0.12_FlowDemandLedgerCandidate' for x in ident['items'])
    before=hashlib.sha256(model_file.read_bytes()).hexdigest()
    stop();diag=call('get_diagnostics',modelPath=MODEL);assert diag['errorCount']==0
    out=run('issue06-V012-user-saved-reloaded-rep20261114',TABLES)
    result=check(out)
    ref=json.loads((EVIDENCE/'issue06-V012-final-random-rep20261114.json').read_text(encoding='utf-8'))
    assert out['tables']==ref['tables'],'Reload output differs from accepted current-session reference'
    assert hashlib.sha256(model_file.read_bytes()).hexdigest()==before
    receipt=dict(userSavedFile=str(model_file),modelSHA256=before,nativeIdentity=ident,diagnostics=diag,outputsMatchPreSave=True,checks=result,stop=call('stop_model',modelPath=MODEL),businessReview='Separate Wu acceptance required; this script never closes GitHub')
    (EVIDENCE/'issue06-persistence-readback.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PERSISTENCE REGRESSION PASSED',before)

if __name__=='__main__':main()
