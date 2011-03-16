#!/usr/bin/python

'''
Created on 11/03/2011

@author: markus
'''

import os.path
import sys

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(directory)

from datetime import datetime
from go_wrapper.go_commands import GlobusOnline, Transfer, EndpointError, \
    ExecutionError, TaskError
from pygooglechart import Axis
from timeit import itertools
import csv
import getopt
import pickle
import string



try:
    from pygooglechart import ScatterChart
except:
    pass

try:
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    import numpy as np
except:
    pass

BENCHMARKS_DIRECTORY = os.environ['HOME']+os.sep+'.go-benchmarks'

if not os.path.exists(BENCHMARKS_DIRECTORY):
    os.mkdir(BENCHMARKS_DIRECTORY)

TEST_TRANSFER_DIRECTORY = 'testtransfers'

CHART_SIZE = "chs=600x300"

EP_NZ = 'ng5'
EP_PADS = 'ci#pads'
EP_NZ_DF_AU = 'df_auckland'
EP_NZ_DF_CB = 'df'

SMALL = '/~/testfile.txt'
MB_100 = '/~/testfile_100mb'
GB_1 = '/~/testfile_1gb'
GB_30 = '/~/testfile_30gb'


def create_google_scatter_chart(file, x_values, y_values, z_values, x_label = 'x', y_label = 'y'):
    
    x_max = max(x_values)
    y_max = max(y_values)
    z_max = max(z_values)
    
    chart = ScatterChart(600, 300, x_range=(0, x_max), y_range=(0, y_max))
    
    chart.set_legend(['speed in mbps'])
    
    left_axis = range(0, y_max + 1, 4)
    left_axis[0] = ''
    left_axis[-1] = y_label
    chart.set_axis_labels(Axis.LEFT, left_axis)

    bottom_axis = range(0, x_max + 1, 4)
    bottom_axis[0] = ''
    bottom_axis[-1] = x_label
    chart.set_axis_labels(Axis.BOTTOM, bottom_axis)
    
    chart.add_data(x_values)
    chart.add_data(y_values)
    chart.add_data(z_values)
    
    return chart.get_url(None)
    
    
    #chart.download('/home/markus/scatter-circle.png')
    

def create_google_scatter_chart_link_old(x_values, y_values, z_values, x_label = 'x', y_label = 'y'):
    
    x_max = max(x_values)
    y_max = max(y_values)
    z_max = max(z_values)
    
    ranges = 'chxr='+'0,0,'+str(x_max)+'|1,0,'+str(y_max)
    
    x = ",".join(map(str, x_values))
    y = ",".join(map(str, y_values))
    z = ",".join(map(str, z_values))
    
    data_scale =  'chds=0,'+str(x_max)+',0,'+str(y_max)+',0,'+str(z_max)
    data = 'chd=t:'+x+'|'+y+'|'+z
    
    axis_labels = 'chxl=0:|4|8|12|16|20|24|28|32|1:|4|8|12|16|20|24|28|32|2:|'+x_label+'|3:|'+y_label
    axis_pos = 'chxp=0,4,8,12,16,20,24,28,32|1,4,8,12,16,20,24,28,32|2,'+str(100)+'|3,'+str(100)
    
    return 'http://chart.apis.google.com/chart?'+ranges+'&chxs=1,676767,10.5,0,l,676767&chxt=x,y,x,y&'+CHART_SIZE+'&cht=s&'+data_scale+'&'+data+'&chdl=Speed+in+mbps&chma=|5&chtt=Transfer+speed&'+axis_labels+'&'+axis_pos

class BenchmarkItem():
    
    
    def __init__(self, perf_p, perf_cc, perf_pp):

        self.perf_p = perf_p
        self.perf_cc = perf_cc
        self.perf_pp = perf_pp
        self.handles = {}
        self.tasks = {}
        
    def get_options(self):

        if self.perf_p == 0 and self.perf_cc == 0 and self.perf_pp == 0:
            return ''
        else:
            return '--perf-p='+str(self.perf_p) + ' --perf-cc='+str(self.perf_cc) + ' --perf-pp='+str(self.perf_pp)
        
    def run_item(self, go, series):

        self.handles[series] = go.transfer(series.transfer, self.get_options())
        
        go.wait(self.handles[series], 60)

        return self.handles[series]

    def get_handle(self, series):

        return self.handles[series]
    
    def get_task(self, benchmark, series):
        
        try:
            return self.tasks[series]
        except KeyError:
            self.tasks[series] = benchmark.go.details(self.handles[series])
            benchmark.save()
            
        return self.tasks[series]
    
    def get_perf_option(self, option_name):
        
        if 'perf-p' == option_name:
            return self.perf_p
        if 'perf-pp' == option_name:
            return self.perf_pp
        if 'perf-cc' == option_name:
            return self.perf_cc 
        
    
    def __str__(self):
        
        return str(self.handles)
    

class TransferSeries():
    
    started = None
    
    def __init__(self, source_ep, source_path, target_ep, options=[]):

        self.date_created = datetime.now()
        target = '/~/'+TEST_TRANSFER_DIRECTORY+'/'+string.replace(string.replace(str(self.date_created), ':', '_'), ' ','_')+'/target'
        if source_path.endswith('/'):
            target = target + '/'
        self.transfer = Transfer(source_ep, source_path, target_ep, target, options)
        
        self.items = []
        
        self.finished = False
 
      
    def run_series(self, benchmark):
        
        self.started = datetime.now()
        
        for i in benchmark.items:
            if not i.get_options():
                print 'Running test using default globus-online, no special performance options'
            else:
                print 'Running test using performance options: '+str(i.get_options())
            i.run_item(benchmark.go, self)
            self.items.append(i)
            benchmark.save()
            
        self.finished = datetime.now()
        benchmark.save()
            
    def __str__(self):
        
        return 'Transfer series (started '+self.started+'), '+str(len(self.items))+' items'
    
class Benchmark():
    


    def __init__(self, name, go, perf_p=[], perf_cc=[], perf_pp=[]):
        
        self.name = name
        self.go = go

        if os.path.exists(BENCHMARKS_DIRECTORY+os.sep+name):
            
            if perf_p or perf_cc or perf_pp:
                raise Exception('Benchmark "'+name+'" already exists, you can\'t specify performance options')
            
            with open(BENCHMARKS_DIRECTORY+os.sep+name, 'rb') as f:
                bm = pickle.load(f)
                self.perf_p = bm.perf_p
                self.perf_cc = bm.perf_cc
                self.perf_pp = bm.perf_pp
                self.items = bm.items
                self.series = bm.series
                return 
        else:
        
            if not perf_p and not perf_cc and not perf_pp:
                raise Exception('Benchmark "'+name+'" does not exist, you need to specify performance options (e.g. --perf-p=1,8,16 --perf-cc=1 --perf-pp=1,16,32)')
            
            if perf_p:
                self.perf_p = perf_p
            else:
                self.perf_p = [1]
            
            if perf_cc:
                self.perf_cc = perf_cc
            else:
                self.perf_cc = [1]
                
            if perf_pp:
                self.perf_pp = perf_pp
            else:
                self.perf_pp = [1]

            self.items = []
            self.series = []
            
            # first, we always run the "no-option" globus default, to have a comparison
            self.items.append(BenchmarkItem(0,0,0))
        
            combinantions = itertools.product(self.perf_p, self.perf_cc, self.perf_pp)
        
            for c in combinantions:
                item = BenchmarkItem(c[0], c[1], c[2])
                self.items.append(item)
            
            self.save()
            
    def save(self):

        with open(BENCHMARKS_DIRECTORY+os.sep+self.name, mode='wb') as f:
            pickle.dump(self, f)
           
    def add_series(self, s):
        
        print "Adding transfer series to benchmark "+self.name+"..."
        
        self.series.append(s)
        s.run_series(self)
        self.save()

    def get_series(self):

        return self.series
    
    def info(self):
        
        result = 'Name: '+self.name+'\n'
        result += '\tperf-p:\t\t'+' '.join(map(str, self.perf_p))+'\n'
        result += '\tperf-cc:\t'+' '.join(map(str, self.perf_cc))+'\n'
        result += '\tperf-pp:\t'+' '.join(map(str, self.perf_pp))+'\n'
        result += '\tSeries:'+'\n'
        
        if not self.series:
            
            result += '\t\tNo transfer series for this benchmark yet. Add one using something like: --source-endpoint=ci#pads --source-path=/~/testfile_1GB --target-endpoint=markus#ng5' 
        else:
            for s in self.series:
                result += '\t\tStarted: '+str(s.date_created)+'\n'
                result += '\t\tSource endpoint: '+s.transfer.source_ep+'\n'
                result += '\t\tSource path: '+s.transfer.source_path+'\n'
                result += '\t\tTarget endpoint: '+s.transfer.target_ep+'\n'
                
                for i in s.items:
                    opts = i.get_options()
                    if not opts:
                        opts = '(globus default)\t\t'
                    result += '\t\t\tOptions: '+opts+'\t(Speed: '+str(i.get_task(self, s).mbps)+' mbps)\n'
                
        return result
    
    def visualize(self, x_axis='perf-pp', y_axis='perf-p'):
        
        values_x = []
        values_y = []
        values_z = []
        
        links = {}
        
        for s in self.series:
            
            for i in s.items:
                task = i.get_task(self, s)
                
                x = i.get_perf_option(x_axis)
                values_x.append(x)
                y = i.get_perf_option(y_axis)
                values_y.append(y)
                z = task.mbps
                values_z.append(z)
                
            #link = create_google_scatter_chart_link_old(values_x, values_y, values_z, x_axis, y_axis)
            link = create_google_scatter_chart_link_old(values_x, values_y, values_z, x_axis, y_axis)
            #create_3d_graph(values_x, values_y, values_z, x_axis, y_axis)
            
            links[s] = link
            
        return links
        
        
    def create_csv(self, file):
        
        c = csv.writer(open(file, "wb"))
        c.writerow(['series','perf-p','perf-cc','perf-pp','mpbs'])
        
        for s in self.series:
        
            for i in s.items:
                c.writerow([str(s.date_created), str(i.perf_p), str(i.perf_cc), str(i.perf_pp), str(i.get_task(self, s).mbps)])


def usage():
    
    print 'Usage: benchmark.py (-l|-u <globus_online_username> -n <benchmark_name>) [OPTION...]'
    print
    print 'Benchmarks have names, when creating a new benchmark you need to specify the perf-p, perf-cc and perf-pp options you want the benchmark to cycle through. Once benchmark is created those options can\'t be changed anymore.'
    print 
    print '-h\t--help\t\t\t\t\tthis help'
    print '-d\t--debug\t\t\t\t\tturns debug on (not implemented yet)'
    print '-u\t--username=GLOBUS_ONLINE_USERNAME\tthe globus online username'
    print '-l\t--list\t\t\t\t\tlists all available benchmark names'
    print '-n\t--name=BENCHMARK_NAME\t\t\tthe name of the benchmark'
    print '-i\t--info\t\t\t\t\tdisplaying information about a benchmark'
    print '-s\t--source-endpoint=SOURCE_ENDPOINT\tthe name of the source endpoint to be used in this series (also requires -p and -t)'
    print '-p\t--source-path\t\t\t\tthe path to the input file/folder to be used in this series (also requires -s and -t)'
    print '-t\t--target-endpoint=SOURCE_ENDPOINT\tthe name of the target endpoint (also requires -p and -s)'
    print '\t--perf-p\t\t\t\tperf-p options (comma-seperated) to use in this benchmark (can only be specified if benchmark with the specified name does not exist yet)'
    print '\t--perf-cc\t\t\t\tperf-cc options (comma-seperated) to use in this benchmark (can only be specified if benchmark with the specified name does not exist yet)'
    print '\t--perf-pp\t\t\t\tperf-pp options (comma-seperated) to use in this benchmark (can only be specified if benchmark with the specified name does not exist yet)'
    print '-c\t--csv-file\t\t\t\texports the specified benchmark into a csv file'
    print '-v\t--visualize\t\t\t\tprints a url to a google charts image for all the transfer series in this benchmark'


def main(argv):
    
    try:                                
        opts, args = getopt.getopt(argv, "hdu:s:t:p:n:c:vli", ["help", "debug", "username=", "source-endpoint=", "target-endpoint=", "source-path=", "name=", "perf-pp=", "perf-cc=", "perf-p=", "csv-file=", "visualize", "list", "info"]) 
    except getopt.GetoptError:           
        usage()
        sys.exit(2)  
        
    perf_pp = []
    perf_p = []
    perf_cc = []
    
    username = None
    source_path = None
    source_ep = None
    target_ep = None
    name = None
    visualize = False
    csv_file = None
    list = False
    info = False
        
    for opt, arg in opts:                
        if opt in ("-h", "--help"):      
            usage()                     
            sys.exit()                  
        elif opt == '-d':                
            global _debug               
            _debug = 1                  
        elif opt in ("-u", "--username"): 
            username = arg
        elif opt in ("-s", "--source-endpoint"):
            source_ep = arg
        elif opt in ("-t", "--target-endpoint"):
            target_ep = arg
        elif opt in ("-p", "--source-path"):
            source_path = arg
        elif opt in ("--perf-pp"):
            perf_pp = arg.split(',')
        elif opt in ("--perf-cc"):
            perf_cc = arg.split(',')
        elif opt in ("--perf-p"):
            perf_p = arg.split(',')
        elif opt in ("-c", "--csv-file"):
            csv_file = arg
        elif opt in ("-v", "--visualize"):
            visualize = 1
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-l", "--list"):
            list = 1
        elif opt in ("-i", "--info"):
            info = 1
            
    if list:
        for bm in os.listdir(BENCHMARKS_DIRECTORY):
            print bm
        sys.exit(0)
    
    
    if not username:
        print "No username specified."
        usage()
        sys.exit(2)
        
    if not name:
        print "No benchmark name specified."
        usage()
        sys.exit(2)
    
    go = GlobusOnline(username)
    
    
    try: 
        
        try:
            bm = Benchmark(name, go, perf_p, perf_cc, perf_pp)
        except Exception as e:
            print e
            sys.exit(1)
        
        if source_path and source_ep and target_ep:
            se = TransferSeries(source_ep, source_path, target_ep)
            bm.add_series(se)

        if info:
            print bm.info()
        
               
        if visualize:
            for s,u in bm.visualize().items():
                print 'Chart URL for series '+str(s.date_created)+': \n'+u+'\n'

        if csv_file:
            bm.create_csv(csv_file)
        
        
        

    except EndpointError as ee:
        print "Error: "+ee.msg+": "+ee.ep
    except ExecutionError as ee:
        print "Execution error for \'"+ee.cmd+"\': "+ee.msg
    except TaskError as te:
        print "Task error for \'"+te.task+"\': "+te.msg
    



if __name__ == "__main__":
    
    main(sys.argv[1:])

