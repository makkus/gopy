'''
Created on 11/03/2011

@author: markus
'''
from go_wrapper.go_commands import GlobusOnline, Transfer, EndpointError, \
    ExecutionError, TaskError

def transferSmall(go):
        
        t1 = Transfer('ci#pads', '/~/testfile.txt', 'ng5', '/~/testfile.txt')
        t2 = Transfer('ci#pads', '/~/testfile.txt', 'ng5', '/~/testfile2.txt')
        id = go.transfer([t1, t2], "--perf-p=6", "--perf-cc=6")
    
        print id
        
def transferBig(go):

        
        t = Transfer('ci#pads', '/~/testfile_30GB', 'ng5', '/~/test2')
        id = go.transfer(t, "--perf-p=6" , "--perf-cc=6")
    
        print id        
    
def ls(go):
    
    folderlist = go.ls("ci#pads")
    print folderlist
    

def details(go):
    
    task = go.details('93037786-4b84-11e0-aaca-123139054450')
    
    print task.taskId
    print task.taskType
    print task.requestTime
    print task.completionTime
    
    print task.isfinished()
    
    
    
def join(go):
    
    go.join('93037786-4b84-11e0-aaca-123139054450')

go = GlobusOnline('markus')


def get_active_tasks(go):
    
    taskIds = go.get_active_tasks()
    
    print taskIds

try: 

    #details(go)
    #join(go)
    #transferBig(go)
    transferSmall(go)
    
    get_active_tasks(go)


except EndpointError as ee:
    print "Error: "+ee.msg+": "+ee.ep
except ExecutionError as ee:
    print "Execution error for \'"+ee.cmd+"\': "+ee.msg
except TaskError as te:
    print "Task error for \'"+te.task+"\': "+te.msg


