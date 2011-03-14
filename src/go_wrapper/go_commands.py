'''
Created on 11/03/2011

@author: Markus Binsteiner
'''

import datetime
import logging
import subprocess
import time

EXPIRED = "expired"
ERROR_ENDPOINT_NOT_ACTIVATED = "Endpoint not activated"
ERROR_ENDPOINT_NOT_AVAILABLE = "Endpoint not available"

def toDate(dateString):
    if dateString == None or dateString == 'n/a':
        return None
    return datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M:%SZ")


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class EndpointError(Error):
    """Exception raised for errors in endpoints. Usually raised when an endpoint is not activated.

    Attributes:
        ep -- the endpoint in question
        msg  -- explanation of the error
    """

    def __init__(self, ep, msg):
        self.ep = ep
        self.msg = msg
        
class ExecutionError(Error):
    """Exception raised for errors when executing a command.

    Attributes:
        cmd -- the command that was executed
        msg  -- explanation of the error (stderr)
    """

    def __init__(self, cmd, msg):
        self.cmd = cmd
        self.msg = msg       
        
class TaskError(Error):
    """Exception raised for errors with tasks

    Attributes:
        task -- the task in question
        msg  -- explanation of the error
    """

    def __init__(self, task, msg):
        self.task = task
        self.msg = msg      
        
class Transfer:
    
    def __init__(self, source_ep, source_path, target_ep, target_path, *options):
        self.source_ep = source_ep
        self.source_path = source_path
        self.target_ep = target_ep
        self.target_path = target_path
        self.options = options

    def __eq__(self, o):
        return self.source_ep == o.source_ep and self.source_path == o.source_path and self.target_ep == o.target_ep and self.target_path == o.target_path
        
    def __cmp__(self, o):
        return self.source_ep == o.source_ep and self.source_path == o.source_path and self.target_ep == o.target_ep and self.target_path == o.target_path
      
    def __hash__(self):
        return hash((self.source_ep, self.source_path, self.target_ep, self.target_path))

    def __str__(self):
        return 'Transfer of file '+self.source_path+' from: '+self.source_ep+' to: '+self.target_ep


LOG_FILENAME = 'go.debug'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

class Task:
    
    events = []
    
    def __init__(self, details):
        
        self.details = details
    
        self.taskId = details.get('Task ID')
        self.taskType = details.get('Task Type')
        self.parentTaskId = details.get('Parent Task ID')
        self.status = details.get('Status')
        self.requestTime = toDate(details.get('Request Time'))
        self.deadline = toDate(details.get('Deadline'))
        self.completionTime = toDate(details.get('Completion Time'))
        self.totalTasks = int(details.get('Total Tasks'))
        self.tasksSuccessful = int(details.get('Tasks Successful'))
        self.tasksExpired = int(details.get('Tasks Expired'))
        self.tasksCancelled = int(details.get('Tasks Canceled'))
        self.taksFailed = int(details.get('Tasks Failed'))
        self.tasksPending = int(details.get('Tasks Pending'))
        self.tasksRetrying = int(details.get('Tasks Retrying'))
        self.command = details.get('Command')
        self.files = int(details.get('Files'))
        self.filesSkipped = int(details.get('Files Skipped'))
        self.directories = int(details.get('Directories'))
        self.bytesTransferred = long(details.get('Bytes Transferred'))
        self.bytesChecksummed = long(details.get('Bytes Checksummed'))
        self.mbps = float(details.get('MBits/sec'))
        
        
    def print_details(self):
        
        print self.taskId
        print '--------------------------------------------'
        print '\perf. options: '+self.command
        print '\tbytes transferred: '+str(self.bytesTransferred)
        print '\tmbps: '+str(self.mbps)
        print '--------------------------------------------\n'
        
    def isfinished(self):
        
        print "Status: "+self.status
        
        if self.status == 'FAILED' or self.status == 'SUCCEEDED':
            return True
        else:
            return False

class Event:
    
    def __init__(self, csvline):
        
        tokens = csvline.split(',')
        self.id = tokens[0]
        self.parentId = tokens[1]
        self.time = tokens[2]
        self.code = tokens[3]
        self.description = tokens[4]
        self.details = tokens[5]
        
    def to_string(self):
        
        return 'Task ID\t:'+self.id+'\nParent Task ID\t: '+self.parentId+'\nTime\t: '+self.time+'\nCode\t: '+self.code+'\nDescription\t: '+self.description+'\nDetails\t: '+self.details
        
        
class GlobusOnline:

    endpointCache = {}
    sleepTime = 4
    lastDetails = {}
    
    def __init__(self, username):
        self.username = username
    
    def ls(self, endpoint, dir="/~/", parameters=''):
        
        self.checkEndpointActivated(endpoint)
        
        commandline = 'ls '+ parameters + ' ' + endpoint + dir; 
        return self.execute(commandline)
        
    def checkEndpointActivated(self, endpoint):
        
        if not self.endpointCache:
            self.populateEndpointCache()
            
        timeleft = self.endpointCache.get(endpoint)
        
        if not timeleft:
            raise EndpointError(endpoint, ERROR_ENDPOINT_NOT_AVAILABLE)
        
        if EXPIRED == timeleft:
            raise EndpointError(endpoint, ERROR_ENDPOINT_NOT_ACTIVATED)
    
    def populateEndpointCache(self):
        
        logging.debug("Populating endpoint cache")
        
        result = self.execute("endpoint-list")
        
        for line in result.split("\n"):
            
            if not line:
                continue
            
            ep = line.split()[0]
            timeleft = line.split()[1]
            
            if timeleft == '-':
                timeleft = EXPIRED
                
            self.endpointCache[ep] = timeleft
        
    def transfer(self, transferlist, *options):
        
        logging.debug('Creating tranfer...')
        
        if not isinstance(transferlist, list):
            transferlist = [transferlist]
            
        for transfer in transferlist:
            self.checkEndpointActivated(transfer.source_ep)
            self.checkEndpointActivated(transfer.target_ep)
        
        transferLines = None
        
        for transfer in transferlist:
            
            transferLine = transfer.source_ep+transfer.source_path + ' ' + transfer.target_ep+transfer.target_path + ' ' + " ".join(transfer.options)
            if not transferLines:
                transferLines = transferLine
            else:
                transferLines = transferLines+"\n"+transferLine 
        
        optionsString = ''
        
        if options:
            for option in options:
                optionsString = optionsString +option+' '
                
        result = self.execute('transfer '+optionsString, transferLines)
        
        id = result.split()[2]
    
        logging.debug("Created transfer with id: "+id)
        
        return id
    
    def execute(self, commandline, stdin=''):
        
        commandline = "ssh "+self.username+"@cli.globusonline.org "+commandline
        
        logging.debug("Executing: "+commandline)
        
        cmdTokens = commandline.split()
        
        if stdin:
            child = subprocess.Popen(cmdTokens, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = child.communicate(input=stdin)
    
        else:
            child = subprocess.Popen(cmdTokens, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = child.communicate()
        
    
        
        logging.debug("Result (stdout):\n-------------------\n"+result[0]+"\n")
        logging.debug("Result (stderr):\n-------------------\n"+result[1]+"\n")
    
        if result[1]:
            raise ExecutionError(commandline, result[1])
    
        return result[0]
    
    def wait(self, id):
        
        if isinstance(id, Task):
            id = id.taskId
        
        self.execute("wait -q "+id)
            
        
    def details(self, id):
        
        try:
            result = self.execute("details "+id)
        except ExecutionError as ee:
        
            if 'Error: No such task id' in ee.msg:
                raise TaskError(id, 'No such task id '+id)
        
        details = {}
        
        for line in result.split('\n'):
            
            if not line:
                continue
            
            key = line.split(':', 1)[0].strip()
            value = line.split(':', 1)[1].strip() 
            
            details[key] = value

        self.lastDetails[id] = Task(details)

        return self.lastDetails[id]
        
        
    def get_active_tasks(self):
        
        result = []
        
        for line in self.status().split('\n'):
            if line.startswith('Task ID'):
                id = line.split(":")[1].strip()
                result.append(id) 
        
        self.lastActiveTask = result
    
        return self.lastActiveTask
    
    def status(self):
        
        self.lastStatus = self.execute('status')
        
        return self.lastStatus
        
    def events(self, id):
        
        self.lastEvents[id] =  self.execute("events "+id)
        
        return self.lastEvents[id]
        
    def setUsername(self, un):
        self.username = un


