"""Project-local native Simio MCP adapter; never saves the user's model."""
import json
import pathlib
import runpy
import sys
import datetime
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'outputs/vsm-michigan-steel-baseline/evidence'
mod = runpy.run_path(r'C:\Users\吴一帆\.codex\skills\simio-mcp\scripts\simio_mcp.py')
client = mod['SimioMcpClient']('http://localhost:51310', timeout=120)
client.initialize()

def call(tool_name, **args):
    r = client.call_tool(tool_name, args)
    if r.get('error') or r.get('result', {}).get('isError'):
        raise RuntimeError(json.dumps(r, ensure_ascii=False))
    result = mod['unwrap_tool_text'](r)
    with (EVIDENCE / 'issue06-native-operations.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'tool': tool_name, 'args': args, 'result': result}, ensure_ascii=False) + '\n')
    return result

def props(path, names=None):
    a = {'path': path}
    if names: a['propertyNames'] = names
    return call('get_properties', **a)

def setp(path, name, value, units=None):
    a = dict(path=path, propertyName=name, value=str(value))
    if units: a['units'] = units
    r = call('set_property', **a)
    if isinstance(r, dict) and r.get('success') is False: raise RuntimeError(str(r))
    return r

MODEL = '/Project/Model'

if __name__ == '__main__':
    print(json.dumps(call(sys.argv[1], **json.loads(sys.argv[2] if len(sys.argv)>2 else '{}')), ensure_ascii=False, indent=2))
