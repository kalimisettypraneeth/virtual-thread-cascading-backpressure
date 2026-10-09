"""Check frozen ownership/order invariants. Synthetic tests are not runtime evidence."""
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def check(rows,scenario,mode):
    oracle=json.loads((HERE/'expected.json').read_text())
    rule=oracle['scenarios'][scenario]
    assert rows and [int(r[0]) for r in rows]==list(range(1,len(rows)+1)), 'sequence'
    assert all(len(r)==6 for r in rows), 'event shape'
    assert not any(r[1] in ('unresolved','late-cleanup','late-cleanup-error') for r in rows), 'unresolved work'
    assert rows[-1][1]=='case-finished', 'incomplete case'
    starts=[r for r in rows if r[1]=='request']
    assert len(starts)==2 and starts[0][5]==scenario and starts[1][5]=='followup:'+starts[0][2], 'linked followup'
    assert len({r[2] for r in starts})==2 and len({r[3] for r in starts})==2, 'unique ownership'
    for i,start in enumerate(starts):
        group=[r for r in rows if r[2]==start[2]]
        def one(kind):
            found=[r for r in group if r[1]==kind]
            assert len(found)==1, kind+' count'
            return found[0]
        def order(*events):
            seq=[int(one(e)[0]) for e in events]
            assert seq==sorted(seq) and len(set(seq))==len(seq),'event ordering'
        acquired=one('connection-acquired');pid=acquired[4]
        assert int(pid)>0, 'backend PID'
        assert all(r[3]==start[3] and r[4]==pid for r in group if r[1] not in ('request','lease-acquired','capacity-restored')), 'ownership links'
        order('lease-acquired','connection-acquired','outcome','connection-closed','server-inactive','lease-terminal','callback-counts','capacity-restored')
        terminal='success' if i else rule['terminal']
        assert one('lease-terminal')[5]==terminal,'terminal policy'
        counts={'success':'1,0,0','error':'0,1,0','cancel':'0,0,1'}
        assert one('callback-counts')[5]==counts[terminal], 'exactly one callback'
        assert one('outcome')[5]==('OK' if i else rule['sqlstate']), 'SQL outcome'
        assert one('capacity-restored')[5]=='2','capacity'
        if i or rule['active_required']:
            one('query-issued')
            if mode!='reactive':assert one('thread-identity')[5]==str(mode=='virtual').lower(),'thread identity'
        if not i and rule['active_required']:
            order('query-issued','server-active','outcome')
            assert one('query-issued')[5]==one('server-active')[5], 'active marker'
            fault='cancel-requested' if scenario=='server-cancel' else 'timeout-armed'
            order('server-active',fault,'outcome')
            if scenario=='server-cancel':assert one(fault)[5]=='true','server cancel'
        elif not i:
            one('before-query-cancel')
            assert not any(r[1] in ('query-issued','server-active','cancel-requested') for r in group),'pre-query conflation'
    assert int(next(r[0] for r in rows if r[1]=='capacity-restored' and r[2]==starts[0][2]))<int(starts[1][0]),'followup before restored'
    return {'status':'PASS','scope':'server-side interruption and sequential ownership only','requests':2}

def read(path):
    with Path(path).open() as f:return list(csv.reader(f,delimiter='\t'))
