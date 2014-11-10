import sys
import subprocess
import json
import os
import threading
import copy

import sublime
import sublime_plugin

st2 = (sys.version_info[0] == 2)
dist_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dist_dir)

import gs
import gsq

DOMAIN = 'BaiduFECodeStyleLint'
CL_DOMAIN = 'BaiduFECodeStyleCompLint'
CL_DOMAIN_FORMAT = 'BaiduFECodeStyleCompFormat'


settings = None

def plugin_loaded():
  global settings
  settings = sublime.load_settings("Baidu FE Code Style.sublime-settings")

if st2:
  plugin_loaded()

class FileRef(object):
  def __init__(self, view):
    self.view = view
    self.state = 0
    self.errors = []

def highlight_regions(fr):
  regions = []
  regions0 = []
  domain0 = DOMAIN+'-zero'
  for r in fr.errors:
    row = r.get('line') or 0
    col = r.get('column') or 0
    line = fr.view.line(fr.view.text_point(row-1, 0))
    pos = line.begin() + col
    if pos >= line.end():
      pos = line.end()
    if pos == line.begin():
      regions0.append(sublime.Region(pos, pos))
    else:
      regions.append(sublime.Region(pos, pos))

  if regions:
    fr.view.add_regions(DOMAIN, regions, 'comment', 'dot', sublime.DRAW_EMPTY_AS_OVERWRITE)
  else:
    fr.view.erase_regions(DOMAIN)

  if regions0:
    fr.view.add_regions(domain0, regions0, 'comment', 'dot', sublime.HIDDEN)
  else:
    fr.view.erase_regions(domain0)

def update_status_message(fr):
  sel = gs.sel(fr.view).begin()
  row, _ = fr.view.rowcol(sel)

  msg = ''
  if len(fr.errors) > 0:
    msg = '%s (%d)' % (DOMAIN, len(fr.errors))
    for item in fr.errors:
      line = item.get('line') or 0
      if line == (row + 1) and item.get('message'):
        msg = '%s: %s' % (msg, item.get('message'))

  if fr.state != 0:
    msg = u'\u231B %s' % msg

  fr.view.set_status(DOMAIN, msg)

def highlight(fr):
  cleanup(fr.view)

  if fr.state == 1:
    fr.state = 0
    highlight_regions(fr)

  update_status_message(fr)

def cleanup(view):
  view.set_status(DOMAIN, '')
  view.erase_regions(DOMAIN)
  view.erase_regions(DOMAIN+'-zero')


def ref(fn, validate=True):
  with sem:
    if validate:
      for fn in list(file_refs.keys()):
        fr = file_refs[fn]
        if not fr.view.window() or fn != fr.view.file_name():
          delref(fn)
    return file_refs.get(fn)

def delref(fn):
  with sem:
    if fn in file_refs:
      del file_refs[fn]

def do_comp_lint(fn, node_bin, fecs_bin):
  global settings, st2
  fr = ref(fn, False)
  if not fr:
    return

  errors = []
  try:
    args = [node_bin, fecs_bin, '--silent', '--reporter=baidu', '--format=json', fn]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if len(err.strip()) > 0:
      sublime.error_message(err)
      return
    if st2:
      result = json.loads(out)
    else:
      result = json.loads(out.decode('utf-8'))
    if len(result) > 0:
      errors = result[0]['errors']
  except Exception as e:
    sublime.error_message(str(e))
    return

  def cb():
    fr.errors = errors
    fr.state = 1
    highlight(fr)
  sublime.set_timeout(cb, 0)

def do_comp_format(fn, stdin, node_bin, fecs_bin):
  global settings
  fr = ref(fn, False)
  if not fr:
    return

  formated = ''
  try:
    args = [node_bin, fecs_bin, 'format', '--stream', '--silent']
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    formated, err = proc.communicate(stdin.encode('utf-8'))
    if len(err.strip()) > 0:
      sublime.error_message(err)
      return
  except Exception as e:
    sublime.error_message(str(e))
    return

  def cb():
    edit = fr.view.begin_edit()
    region = sublime.Region(0, fr.view.size())
    fr.view.replace(edit, region, formated.decode('utf-8'))
    fr.view.end_edit(edit)
  sublime.set_timeout(cb, 0)

def watch():
  view = sublime.active_window().active_view()
  if view is not None:
    fn = view.file_name()
    if fn and fn.lower().endswith('.js'):
      fn = os.path.abspath(fn)
      fr = ref(fn, False)
      if fr is not None:
        update_status_message(fr)

  sublime.set_timeout(watch, 500)


def is_valid_settings():
  global settings
  env = settings.get('env')
  if env is None:
    return ('', '', False)

  node_bin = env.get('node_bin')
  fecs_bin = env.get('fecs_bin')
  is_valid = os.path.exists(node_bin) and os.path.exists(fecs_bin)

  return (node_bin, fecs_bin, is_valid)

def run_lint(view):
  node_bin, fecs_bin, is_valid = is_valid_settings()
  if not is_valid:
    return

  fn = view.file_name()
  if not fn.lower().endswith('.js'):
    return
  fn = os.path.abspath(fn)
  if fn:
    file_refs[fn] = FileRef(view)
    gsq.dispatch(CL_DOMAIN, lambda: do_comp_lint(fn, node_bin, fecs_bin), '')

def run_format(view):
  node_bin, fecs_bin, is_valid = is_valid_settings()
  if not is_valid:
    return

  fn = view.file_name()
  if not fn.lower().endswith('.js'):
    return
  fn = os.path.abspath(fn)
  if fn:
    file_refs[fn] = FileRef(view)
    content = view.substr(sublime.Region(0, view.size()))
    gsq.dispatch(CL_DOMAIN_FORMAT, lambda: do_comp_format(fn, content, node_bin, fecs_bin), '')

def is_js_buffer(view):
  fName = view.file_name()
  vSettings = view.settings()
  syntaxPath = vSettings.get('syntax')
  syntax = ""
  ext = ""

  if (fName != None): # file exists, pull syntax type from extension
    ext = os.path.splitext(fName)[1][1:]
  if(syntaxPath != None):
    syntax = os.path.splitext(syntaxPath)[0].split('/')[-1].lower()

  return ext in ['js', 'json'] or "javascript" in syntax or "json" in syntax

class FecsLintEvent(sublime_plugin.EventListener):
  def on_post_save(self, view):
    run_lint(view)

class FecsLintCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    run_lint(self.view)

  def is_visible(self):
    return is_js_buffer(self.view)

class FecsFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    run_format(self.view)

  def is_visible(self):
    return is_js_buffer(self.view)

try:
  th
except:
  th = None
  sem = threading.Semaphore()
  file_refs = {}

watch()
