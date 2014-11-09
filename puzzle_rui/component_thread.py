from threading import Thread

def foo(bar):
    return bar+'\n'

class myThread(Thread):
    def __init__(self,group=None,target=None,name=None,args=(),kwargs={},Verbose=None):
        Thread.__init__(self,group,target,name,args,kwargs,Verbose)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,**self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return

'''
components = ['wordnet_1','wordnet_2','wordnet_3']
threads = {}
outputs = {}
for c in components:
    threads[c] = myThread(target=foo,args=(c,))
    threads[c].start()

for c in components:
    outputs[c] = threads[c].join()


for c in components:
    print outputs[c]
'''
