import diamond.collector
import subprocess
import os
import string
import re

class NscdCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(NscdCollector, self).get_default_config_help()
        config_help.update({
            'bin': 'Path to nscd binary',
        })
        return config_help

    def get_default_config(self):
        config = super(NscdCollector, self).get_default_config()
        config.update({
            'bin':     '/usr/sbin/nscd',
            'path':    'nscd'
        })
        return config

    def collect(self):
      if (not os.access(self.config['bin'], os.X_OK)):
        return

      p = subprocess.Popen([self.config['bin'], '-g'],
                             stdout=subprocess.PIPE).communicate()[0][:-1]

      keys = {
        'cache hits on positive entries':       'positive_hits',
        'cache hits on negative entries':       'negative_hits',
        'cache misses on positive entries':     'positive_misses',
        'cache misses on negative entries':     'negative_misses',
        'number of delays on rdlock':           'rdlock_delays',
        'number of delays on wrlock':           'wrlock_delays',
        'memory allocations failed':            'failed_memory_allocations',
        'used data pool size':                  'used_data_pool_size'
      }

      cache = ''
      for i,line in enumerate(p.split("\n")):
        match = re.match("(.*) cache:$", line)
        if match:
          cache = match.group(1)

        match = re.match("\s*(\d+)  (.*)$", line)
        if match:
          value = match.group(1)
          key = match.group(2)

          if key in keys:
            self.publish(cache+'.'+keys[key], value)
