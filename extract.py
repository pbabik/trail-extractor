#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from colour import Color
from imposm.parser import OSMParser
import csv

path_to_osm = sys.argv[1]

ids_to_colors = {}

COLORS = ['red','blue','green','yellow','black','purple','orange']

def handle_color(tags):
    raw_color = None
    if tags.get('colour') is not None:
        raw_color = tags['colour']
    elif tags.get('color') is not None:
        raw_color = tags['color']
    if raw_color is None:
        for candidate in COLORS:
            for k,v in tags.iteritems():
                if k == 'kct_%s' % candidate: #Czech style tagging
                    raw_color = candidate
                elif k == 'osmc:symbol': #German style tagging
                    if candidate in v:
                        raw_color = candidate
    if raw_color is not None:
        try:
            c = Color(raw_color)
            return c.hex
        except ValueError:
            return None
    return None

def create_row(osmid,a_set):
    values = sorted(list(a_set))
    row = [osmid]
    for i in xrange(5):
        try:
            row.append(values[i])
        except IndexError:
            row.append(None)
    row.append(len(a_set))
    return row


#Reserved for future use

def handle_nodes(nodes):
    pass

def handle_coords(coords):
    pass

def handle_ways(ways):
    pass

def handle_relations(rels):
    for osmid,tags,refs in rels:
        if tags.get('type') == 'route':
            routecolor = handle_color(tags)
            if routecolor:
                for reftuple in refs:
                    ref = reftuple[0]
                    if ref not in ids_to_colors:
                        ids_to_colors[ref] = {'foot':set(),'bike':set(),'ski':set()}
                    if tags.get(u'route') in (u'hiking',u'foot'):
                        ids_to_colors[ref]['foot'].add(routecolor)
                    elif tags.get(u'route') in (u'bicycle',u'mtb'):
                        ids_to_colors[ref]['bike'].add(routecolor)
                    elif tags.get(u'route') in (u'ski',u'piste'):
                        ids_to_colors[ref]['ski'].add(routecolor)

p = OSMParser(relations_callback=handle_relations)
p.parse(path_to_osm)


foot_output = open('foot.csv','wb')
bike_output = open('bike.csv','wb')
ski_output = open('ski.csv','wb')

footwriter = csv.writer(foot_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
bikewriter = csv.writer(bike_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
skiwriter = csv.writer(ski_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)

footwriter.writerow(['osmid','c1','c2','c3','c4','c5','n_colors'])
bikewriter.writerow(['osmid','c1','c2','c3','c4','c5','n_colors'])
skiwriter.writerow(['osmid','c1','c2','c3','c4','c5','n_colors'])

for k,v in ids_to_colors.iteritems():
    if len(v['foot']) > 0:
        footcolors = create_row(k,v['foot'])
        footwriter.writerow(footcolors)
    if len(v['bike']) > 0:
        bikecolors = create_row(k,v['bike'])
        bikewriter.writerow(footcolors)
    if len(v['ski']) > 0:
        skicolors = create_row(k,v['ski'])
        skiwriter.writerow(footcolors)

foot_output.close()
bike_output.close()
ski_output.close()
