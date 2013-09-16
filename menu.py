#!/usr/bin/env python

import collections
import urllib2
import xml.dom.minidom

from HTMLParser import HTMLParser

MENU_RSS_URL = 'http://legacy.cafebonappetit.com/rss/menu/633'

class MenuParser(HTMLParser):
  '''
  Menu parser
  '''

  def __init__(self):
    self.parsed_menu = collections.defaultdict(list)
    self._cur_course = None
    self._change_cur_course = False
    self._cur_entree = None
    self._change_cur_entree = False
    self._append_cur_entree = False
    HTMLParser.__init__(self)

  def handle_starttag(self, tag, attrs):
    if tag == 'h3':
      self._change_cur_course = True
    elif tag == 'h4':
      self._change_cur_entree = True
    elif tag == 'p':
      self._append_cur_entree = True

  def handle_data(self, data):
    if self._change_cur_course is True:
      if self._cur_course is not None:
        self.parsed_menu[self._cur_course].append(' '.join(self._cur_entree))
      self._cur_course = data
      self._cur_entree = None
      self._change_cur_course = False
    elif self._change_cur_entree is True:
      if self._cur_entree is not None:
        self.parsed_menu[self._cur_course].append(' '.join(self._cur_entree))
      self._cur_entree = [data.strip()]
      self._change_cur_entree = False
    elif self._append_cur_entree:
      self._cur_entree.append(data.strip())
      self._append_cur_entree = False

def get_menu():
  '''
  Return list of days, menus
  menus: course->entrees->list(entree)
  '''
  full_menu = []
  menu = urllib2.urlopen(MENU_RSS_URL)
  menu_dom = xml.dom.minidom.parse(menu)
  for item in menu_dom.getElementsByTagName('item'):
    menu_parser = MenuParser()
    title = item.getElementsByTagName('title').item(0)
    day = title.firstChild.data
    description = item.getElementsByTagName('description').item(0)

    day_menu = description.firstChild.data
    menu_parser.feed(day_menu)
    full_menu.append((day, menu_parser.parsed_menu))
  return full_menu

def main():
  '''
  Fetch the menu!
  '''
  menu = get_menu()
  for day, courses in menu:
    print day
    for course, entrees in sorted(courses.iteritems()):
      print course
      print '-' * 10
      for entree in sorted(entrees):
        print entree


if __name__ == '__main__':
  main()
