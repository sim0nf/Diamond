import diamond.collector, psutil, re
from time import time

class ProcessDetailsCollector(diamond.collector.Collector):

  def __init__(self, *args, **kwargs):
    super(ProcessDetailsCollector, self).__init__(*args, **kwargs)
    _matchers = self.config['matchers']
    if isinstance(_matchers, str):
      self.config['compiled_matchers'] = [re.compile(_matchers)]
    elif isinstance(_matchers, list):
      self.config['compiled_matchers'] = map(re.compile, _matchers)
    else:
      raise 'It should be either str or list.'

  def get_default_config_help(self):
    config_help = super(ProcessDetailsCollector, self).get_default_config_help()
    config_help.update({
    })
    return config_help

  def get_default_config(self):
    config = super(ProcessDetailsCollector, self).get_default_config()
    config.update({
      'path' : 'apps',
      'metrics' : [
        'cpu_percent',
        'memory_percent',
        'memory_info.rss',
        'memory_info.vms',
        'cpu_times.user',
        'cpu_times.system',
      ],
      'matchers': [],
    })
    return config

  def publisher(self, _process_metrics, _instance_var, _metric):
    m = _metric.split('.')
    name = "{0}.{1}".format(_instance_var, _metric)
    if len(m) == 2:
      value = getattr(_process_metrics[m[0]], m[1])
    elif len(m) == 1:
      value = _process_metrics[_metric]
    else:
      raise 'Bad metric `'+_metric+'`.'
    self.publish(name, value, precision=1)

  def collect(self):
    for ps in psutil.process_iter():
      print self.config['compiled_matchers']
      for _compiled_matcher in self.config['compiled_matchers']:
        _match = _compiled_matcher.search(' '.join(ps.cmdline))
        if _match is not None:
          _details = ps.as_dict()
          _prefix = '.'.join(map(str, _match.groups()))
          self.publish('{0}.uptime'.format(_prefix), int(time()-_details['create_time']))
          for m in self.config['metrics']: self.publisher(_details, _prefix, m)

