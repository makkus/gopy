'''
Created on 11/03/2011

@author: markus
'''
from datetime import datetime
from go_wrapper.go_commands import GlobusOnline, Transfer, EndpointError, \
    ExecutionError, TaskError
from timeit import itertools
import os.path
import pickle


BENCHMARKS_DIRECTORY = '/home/markus/go-benchmarks/'
TEST_TRANSFER_DIRECTORY = 'testtransfers'

EP_NZ = 'ng5'
EP_PADS = 'ci#pads'
EP_NZ_DF_AU = 'df_auckland'
EP_NZ_DF_CB = 'df'

SMALL = '/~/testfile.txt'
MB_100 = '/~/testfile_100mb'
GB_1 = '/~/testfile_1gb'
GB_30 = '/~/testfile_30gb'


class BenchmarkItem():
    
    
    def __init__(self, benchmark, perf_p, perf_cc, perf_pp):

        self.benchmark = benchmark
        self.perf_p = perf_p
        self.perf_cc = perf_cc
        self.perf_pp = perf_pp
        self.handles = {}
        
    def get_options(self):

        if self.perf_p == 0 and self.perf_cc == 0 and self.perf_pp == 0:
            return ''
        else:
            return '--perf-p='+str(self.perf_p) + ' --perf-cc='+str(self.perf_cc) + ' --perf-pp='+str(self.perf_pp)
        
    def run_item(self, go, t):

        self.handles[t] = go.transfer(t, self.get_options())
        self.benchmark.save()
        
        go.wait(self.handles[t])

        return self.handles[t]

    def get_handle(self, transfer):

        return self.handles[transfer]

class Benchmark():
    

    def __init__(self, name, perf_p=[], perf_cc=[], perf_pp=[]):
        
        self.name = name

        if os.path.exists(BENCHMARKS_DIRECTORY+name):
            with open(BENCHMARKS_DIRECTORY+name, 'rb') as f:
                bm = pickle.load(f)
                self.perf_p = bm.perf_p
                self.perf_cc = bm.perf_cc
                self.perf_pp = bm.perf_pp
                self.items = bm.items
                return 
        else:
        
            self.perf_p = perf_p
            self.perf_cc = perf_cc
            self.perf_pp = perf_pp

            self.items = []
        
            combinantions = itertools.product(self.perf_p, self.perf_cc, self.perf_pp)
        
            for c in combinantions:
                item = BenchmarkItem(self, c[0], c[1], c[2])
                self.items.append(item)
            
            self.save()
            
    def save(self):

        with open(BENCHMARKS_DIRECTORY+self.name, mode='wb') as f:
            pickle.dump(self, f)
           
    def get_series(self, t):
        
        result = []
        
        for i in self.items:
            
            if i.handles[t]:
                result.append(i)
                
        return result

    def get_transfers(self):
        
        result = set()
        
        for i in self.items:
            
            for t in i.handles.keys():
                result.add(t)
                
        return result
      
    def run_series(self, go, t):

        self.started = datetime.now()
        
        for i in self.items:
            i.handles[t] = None
        
        self.save()
        
        for i in self.items:
            print 'Running test using performance options: '+str(i.get_options())
            i.run_item(go, t)
            
            
        self.save()


if __name__ == "__main__":

    go = GlobusOnline('markus')
    
    
    try: 
        #t = Transfer(EP_PADS, MB_100, EP_NZ, MB_100)
        #t = Transfer(EP_PADS, MB_100, EP_NZ, MB_100)
        #t = Transfer(EP_NZ, MB_100, EP_NZ_DF_CB, MB_100)
        t = Transfer(EP_NZ, SMALL, EP_NZ_DF_AU, SMALL)
        
        #bm = Benchmark('test_bm', [1,8,16], [1], [1,16,32])
        bm = Benchmark('test_bm', [1,16], [1], [1,32])

        #bm.run_series(go, t)
        
        for t in bm.get_transfers():
            print t.__str__()
            for bi in bm.get_series(t):
                
                print str(go.details(bi.get_handle(t)).mbps) + '\thandle: '+bi.get_handle(t) + '\t\t' +  '(options: '+bi.get_options()+')'



    except EndpointError as ee:
        print "Error: "+ee.msg+": "+ee.ep
    except ExecutionError as ee:
        print "Execution error for \'"+ee.cmd+"\': "+ee.msg
    except TaskError as te:
        print "Task error for \'"+te.task+"\': "+te.msg
    

