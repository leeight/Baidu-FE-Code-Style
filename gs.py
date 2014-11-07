import os
import sys
import traceback as tbck
import datetime
import threading

try:
  import Queue as queue
except ImportError:
  import queue

import sublime

PY3K = (sys.version_info[0] == 3)

def getwd():
  if PY3K:
    return os.getcwd()
  return os.getcwdu()

def basedir_or_cwd(fn):
  if fn and not fn.startswith('gs.view://'):
    return os.path.dirname(fn)
  return getwd()

def sel(view, i=0):
  try:
    s = view.sel()
    if s is not None and i < len(s):
      return s[i]
  except Exception:
    pass

  return sublime.Region(0, 0)

def apath(fn, cwd=None):
  if not os.path.isabs(fn):
    if not cwd:
      cwd = getwd()
    fn = os.path.join(cwd, fn)
  return os.path.normcase(os.path.normpath(fn))

def traceback(domain='GoSublime'):
  return '%s: %s' % (domain, tbck.format_exc())

def is_js_source_view(view=None, strict=True):
  if view is None:
    return False

  # selector_match = view.score_selector(sel(view).begin(), 'source.go') > 0
  # if selector_match:
  #   return True

  # if strict:
  #   return False

  fn = view.file_name() or ''
  return fn.lower().endswith('.js')

def active_valid_view(win=None, strict=True):
  if not win:
    win = sublime.active_window()
  if win:
    view = win.active_view()
    if view and is_js_source_view(view, strict):
      return view
  return None

def notice(domain, txt):
  error(domain, txt)

def error(domain, txt):
  txt = "%s: %s" % (domain, txt)
  # log(txt)
  # status_message(txt)

def end(task_id):
  with sm_lck:
    try:
      del(sm_tasks[task_id])
    except:
      pass

def begin(domain, message, set_status=True, cancel=None):
  global sm_task_counter

  if message and set_status:
    status_message('%s: %s' % (domain, message))

  with sm_lck:
    sm_task_counter += 1
    tid = 't%d' % sm_task_counter
    sm_tasks[tid] = {
      'start': datetime.datetime.now(),
      'domain': domain,
      'message': message,
      'cancel': cancel,
    }

  return tid

def status_message(s):
  global sm_text
  global sm_tm

  with sm_lck:
    sm_text = s
    sm_tm = datetime.datetime.now()

try:
  st2_status_message
except:
  sm_lck = threading.Lock()
  sm_task_counter = 0
  sm_tasks = {}
  sm_frame = 0
  sm_frames = (
    u'\u25D2',
    u'\u25D1',
    u'\u25D3',
    u'\u25D0'
  )
  sm_tm = datetime.datetime.now()
  sm_text = ''
  sm_set_text = ''

  st2_status_message = sublime.status_message
  sublime.status_message = status_message

  DEVNULL = open(os.devnull, 'w')
  LOGFILE = DEVNULL
