import copy,unittest
from check_events import check

def fixture(scenario='server-cancel',mode='platform'):
    rows=[]
    def emit(k,r='r1',c='c1',p='101',v='1'):rows.append([str(len(rows)+1),k,r,c,p,v])
    emit('runtime','none','none','0','synthetic')
    for i in range(2):
        r,c,p=('r1','c1','101') if i==0 else ('r2','c2','102')
        def e(k,v='1'):emit(k,r,c,p,v)
        e('request',scenario if i==0 else 'followup:r1');e('lease-acquired');e('connection-acquired')
        if scenario=='before-query' and i==0:e('before-query-cancel')
        else:
            e('query-issued','marker' if i==0 else 'SELECT1')
            if mode!='reactive':e('thread-identity',str(mode=='virtual').lower())
            if i==0:
                e('server-active','marker');e('cancel-requested' if scenario=='server-cancel' else 'timeout-armed','true')
        e('outcome','OK' if i else 'NONE' if scenario=='before-query' else '57014');e('connection-closed');e('server-inactive')
        terminal='success' if i else 'error' if scenario=='server-timeout' else 'cancel'
        e('lease-terminal',terminal);e('callback-counts',{'success':'1,0,0','error':'0,1,0','cancel':'0,0,1'}[terminal]);e('capacity-restored','2')
    emit('case-finished','none','none','0','synthetic');return rows

class Invariants(unittest.TestCase):
    def test_valid_synthetic_contract(self):
        for mode in ('platform','virtual','reactive'):
            for scenario in ('before-query','server-cancel','server-timeout'):check(fixture(scenario,mode),scenario,mode)
    def reject(self,fn):
        rows=fixture();fn(rows)
        for i,r in enumerate(rows,1):r[0]=str(i)
        with self.assertRaises(AssertionError):check(rows,'server-cancel','platform')
    def test_reject_missing_active(self):self.reject(lambda rs:rs.remove(next(r for r in rs if r[1]=='server-active')))
    def test_reject_duplicate_release(self):self.reject(lambda rs:rs.insert(10,copy.deepcopy(next(r for r in rs if r[1]=='connection-closed'))))
    def test_reject_double_callback(self):self.reject(lambda rs:next(r for r in rs if r[1]=='callback-counts').__setitem__(5,'0,0,2'))
    def test_reject_unresolved(self):self.reject(lambda rs:rs.insert(-1,['0','unresolved','r1','c1','101','late']))
    def test_reject_wrong_backend(self):self.reject(lambda rs:next(r for r in rs if r[1]=='server-active').__setitem__(4,'999'))
    def test_reject_missing_followup(self):self.reject(lambda rs:rs.__setitem__(slice(None),[r for r in rs if r[2]!='r2']))
    def test_reject_early_terminal(self):
        def mutate(rs):
            row=next(r for r in rs if r[1]=='lease-terminal');rs.remove(row);rs.insert(3,row)
        self.reject(mutate)
    def test_reject_false_cancel(self):self.reject(lambda rs:next(r for r in rs if r[1]=='cancel-requested').__setitem__(5,'false'))

if __name__=='__main__':unittest.main(verbosity=2)
