#!/usr/bin/env python

import os, sys
import Queue
import getpass
import re
from threading import Thread
from string import find, split, join, atof

# svmtrain and gnuplot executable

is_win32 = (sys.platform == 'win32')
if not is_win32:
       svmtrain_exe = "../svm-train"
       gnuplot_exe = "/usr/bin/gnuplot"
else:
       # example for windows
       svmtrain_exe = r"..\windows\svmtrain.exe"
       gnuplot_exe = r"c:\tmp\gnuplot\bin\pgnuplot.exe"

# global parameters and their default values

fold = 5
c_begin, c_end, c_step = -5,  15, 2
g_begin, g_end, g_step =  3, -15, -2
global dataset_pathname, dataset_title, pass_through_string
global out_filename, png_filename

# experimental

telnet_workers = []
ssh_workers = []
nr_local_worker = 1

# process command line options, set global parameters
def process_options(argv=sys.argv):

    global fold
    global c_begin, c_end, c_step
    global g_begin, g_end, g_step
    global dataset_pathname, dataset_title, pass_through_string
    global svmtrain_exe, gnuplot_exe, gnuplot, out_filename, png_filename
    
    usage = """\
Usage: grid.py [-log2c begin,end,step] [-log2g begin,end,step] [-v fold] 
[-svmtrain pathname] [-gnuplot pathname] [-out pathname] [-png pathname]
[additional parameters for svm-train] dataset"""

    if len(argv) < 2:
        print usage
        sys.exit(1)

    dataset_pathname = argv[-1]
    dataset_title = os.path.split(dataset_pathname)[1]
    out_filename = '%s.out' % dataset_title
    png_filename = '%s.png' % dataset_title
    pass_through_options = []

    i = 1
    while i < len(argv) - 1:
        if argv[i] == "-log2c":
            i = i + 1
            (c_begin,c_end,c_step) = map(atof,split(argv[i],","))
        elif argv[i] == "-log2g":
            i = i + 1
            (g_begin,g_end,g_step) = map(atof,split(argv[i],","))
        elif argv[i] == "-v":
            i = i + 1
            fold = argv[i]
        elif argv[i] in ('-c','-g'):
            print "Option -c and -g are renamed."
            print usage
            sys.exit(1)
        elif argv[i] == '-svmtrain':
            i = i + 1
            svmtrain_exe = argv[i]
        elif argv[i] == '-gnuplot':
            i = i + 1
            gnuplot_exe = argv[i]
        elif argv[i] == '-out':
            i = i + 1
            out_filename = argv[i]
        elif argv[i] == '-png':
            i = i + 1
            png_filename = argv[i]
        else:
            pass_through_options.append(argv[i])
        i = i + 1

    pass_through_string = join(pass_through_options," ")
    assert os.path.exists(svmtrain_exe),"svm-train executable not found"    
    assert os.path.exists(gnuplot_exe),"gnuplot executable not found"
    gnuplot = os.popen(gnuplot_exe,'w')


def range_f(begin,end,step):
    # like range, but works on non-integer too
    seq = []
    while 1:
        if step > 0 and begin > end: break
        if step < 0 and begin < end: break
        seq.append(begin)
        begin = begin + step
    return seq

def permute_sequence(seq):
    n = len(seq)
    if n <= 1: return seq

    mid = int(n/2)
    left = permute_sequence(seq[:mid])
    right = permute_sequence(seq[mid+1:])

    ret = [seq[mid]]
    while left or right:
        if left: ret.append(left.pop(0))
        if right: ret.append(right.pop(0))

    return ret

def redraw (db,tofile=0):
    if len(db) == 0: return
    begin_level = round(max(map(lambda(x):x[2],db))) - 3
    step_size = 0.5
    if tofile:
        gnuplot.write("set term png transparent small\n")
        gnuplot.write("set output \"%s\"\n" % png_filename.replace('\\','\\\\'))
        #gnuplot.write("set term postscript color solid\n")
        #gnuplot.write("set output \"%s.ps\"\n" % dataset_title)
    else:
        if is_win32:
            gnuplot.write("set term windows\n")
        else:
            gnuplot.write("set term x11\n")
    gnuplot.write("set xlabel \"lg(C)\"\n")
    gnuplot.write("set ylabel \"lg(gamma)\"\n")
    gnuplot.write("set xrange [%s:%s]\n" % (c_begin,c_end))
    gnuplot.write("set yrange [%s:%s]\n" % (g_begin,g_end))
    gnuplot.write("set contour\n")
    gnuplot.write("set cntrparam levels incremental %s,%s,100\n" % (begin_level,step_size))
    gnuplot.write("set nosurface\n")
    gnuplot.write("set view 0,0\n")
    gnuplot.write("set label \"%s\" at screen 0.4,0.9\n" % dataset_title)
    gnuplot.write("splot \"-\" with lines\n")
    def cmp (x,y):
        if x[0] < y[0]: return -1
        if x[0] > y[0]: return 1
        if x[1] > y[1]: return -1
        if x[1] < y[1]: return 1
        return 0
    db.sort(cmp)
    prevc = db[0][0]
    for line in db:
        if prevc != line[0]:
            gnuplot.write("\n")
            prevc = line[0]
        gnuplot.write("%s %s %s\n" % line)
    gnuplot.write("e\n")
    gnuplot.flush()


def calculate_jobs():
    c_seq = permute_sequence(range_f(c_begin,c_end,c_step))
    g_seq = permute_sequence(range_f(g_begin,g_end,g_step))
    nr_c = float(len(c_seq))
    nr_g = float(len(g_seq))
    i = 0
    j = 0
    jobs = []

    while i < nr_c or j < nr_g:
        if i/nr_c < j/nr_g:
            # increase C resolution
            line = []
            for k in range(0,j):
                line.append((c_seq[i],g_seq[k]))
            i = i + 1
            jobs.append(line)
        else:
            # increase g resolution
            line = []
            for k in range(0,i):
                line.append((c_seq[k],g_seq[j]))
            j = j + 1
            jobs.append(line)
    return jobs

class WorkerStopToken:  # used to notify the worker to stop
        pass

class Worker(Thread):
    def __init__(self,name,job_queue,result_queue):
        Thread.__init__(self)
        self.name = name
        self.job_queue = job_queue
        self.result_queue = result_queue
    def run(self):
        while 1:
            (cexp,gexp) = self.job_queue.get()
            if cexp is WorkerStopToken:
                self.job_queue.put((cexp,gexp))
                # print 'worker %s stop.' % self.name
                break
            try:
                rate = self.run_one(2.0**cexp,2.0**gexp)
                if rate is None: raise "get no rate"
            except:
                # we failed, let others do that and we just quit
                self.job_queue.put((cexp,gexp))
                print 'worker %s quit.' % self.name
                break
            else:
                self.result_queue.put((self.name,cexp,gexp,rate))

class LocalWorker(Worker):
    def run_one(self,c,g):
        cmdline = '%s -c %s -g %s -v %s %s %s' % \
          (svmtrain_exe,c,g,fold,pass_through_string,dataset_pathname)
        result = os.popen(cmdline,'r')
        for line in result.readlines():
            if find(line,"Cross") != -1:
                return atof(split(line)[-1][0:-1])

class SSHWorker(Worker):
    def __init__(self,name,job_queue,result_queue,host):
        Worker.__init__(self,name,job_queue,result_queue)
        self.host = host
        self.cwd = os.getcwd()
    def run_one(self,c,g):
        cmdline = 'ssh -x %s "cd %s; %s -c %s -g %s -v %s %s %s"' % \
          (self.host,self.cwd,
           svmtrain_exe,c,g,fold,pass_through_string,dataset_pathname)
        result = os.popen(cmdline,'r')
        for line in result.readlines():
            if find(line,"Cross") != -1:
                return atof(split(line)[-1][0:-1])

class TelnetWorker(Worker):
    def __init__(self,name,job_queue,result_queue,host,username,password):
        Worker.__init__(self,name,job_queue,result_queue)
        self.host = host
        self.username = username
        self.password = password        
    def run(self):
        import telnetlib
        self.tn = tn = telnetlib.Telnet(self.host)
        tn.read_until("login: ")
        tn.write(self.username + "\n")
        tn.read_until("Password: ")
        tn.write(self.password + "\n")

        # XXX: how to know whether login is successful?
        tn.read_until(self.username)
        # 
        print 'login ok', self.host
        tn.write("cd "+os.getcwd()+"\n")
        Worker.run(self)
        tn.write("exit\n")               
    def run_one(self,c,g):
        cmdline = '%s -c %s -g %s -v %s %s %s' % \
          (svmtrain_exe,c,g,fold,pass_through_string,dataset_pathname)
        result = self.tn.write(cmdline+'\n')
        (idx,matchm,output) = self.tn.expect(['Cross.*\n'])
        for line in split(output,'\n'):
            if find(line,"Cross") != -1:
                return atof(split(line)[-1][0:-1])

def main():

    # set parameters

    process_options()

    # put jobs in queue

    jobs = calculate_jobs()
    job_queue = Queue.Queue(0)
    result_queue = Queue.Queue(0)

    for line in jobs:
        for (c,g) in line:
            job_queue.put((c,g))

    # hack the queue to become a stack --
    # this is important when some thread
    # failed and re-put a job. If we still
    # use FIFO, the job will be put
    # into the end of the queue, and the graph
    # will only be updated in the end

    def _put(self,item):
        if sys.hexversion >= 0x020400A1:
            self.queue.appendleft(item)
        else:
            self.queue.insert(0,item)

    import new
    job_queue._put = new.instancemethod(_put,job_queue,job_queue.__class__)

    # fire telnet workers

    if telnet_workers:
        nr_telnet_worker = len(telnet_workers)
        username = getpass.getuser()
        password = getpass.getpass()
        for host in telnet_workers:
            TelnetWorker(host,job_queue,result_queue,
                     host,username,password).start()

    # fire ssh workers

    if ssh_workers:
        for host in ssh_workers:
            SSHWorker(host,job_queue,result_queue,host).start()

    # fire local workers

    for i in range(nr_local_worker):
        LocalWorker('local',job_queue,result_queue).start()

    # gather results

    done_jobs = {}
    result_file = open(out_filename,'w',0)
    db = []
    best_rate = -1

    for line in jobs:
        for (c,g) in line:
            while not done_jobs.has_key((c,g)):
                (worker,c1,g1,rate) = result_queue.get()
                done_jobs[(c1,g1)] = rate
                result_file.write('%s %s %s\n' %(c1,g1,rate))
                result_file.flush()
                print "[%s] %s %s %s" % (worker,c1,g1,rate),
                if (rate > best_rate) or (rate==best_rate and g1==best_g1 and c1<best_c1):
                    best_rate = rate
                    best_c1,best_g1=c1,g1
                    best_c = 2.0**c1
                    best_g = 2.0**g1
                print " (best c=%s, g=%s, rate=%s)" % \
                    (best_c, best_g, best_rate)
            db.append((c,g,done_jobs[(c,g)]))
        redraw(db)
        redraw(db,1)

    job_queue.put((WorkerStopToken,None))
    print "%s %s %s" % (best_c, best_g, best_rate)
main()
