#!/usr/bin/env python
#Version 2
# created 11-12-09 Andrew Trujillo

#Note: wai stands for "where am i" which refers to the whereami afni comand

Usage = """This script is for creating tables in csv format from 3dclust output.
	   Example1: tableDump.py 3dclustOut.txt
	   Example2: tableDump.py 3dclustOut.txt mySpecialOutputName\n
Input: 3dclust output from afni\n
Optional Input:  a base filename for your output.  
The default is to use your cluster file name.\n
Output: a file called table_[yourfilename].csv which contains a csv 
file with the following headers and data for each cluster;
	   TTRegion: Closest Talairach Region to the coordinate focus point
	   TTmm: mm of suggested region to coordinate focus point
           CARegion: Closest CA_N27 Region to the coordinate focus point
           CAmm: mm of suggested region to coordinate focus point
	   X: x coordinate already corrected for publication
           Y: y coordinate already corrected for publication
           Z: z coordinate already corrected for publication
	   zScore: max z Score for the cluster 
	   Voxels: size of the cluster
           You will also get a file called wai_[yourfilename].csv which contains 
           the output from the afni whereami command."""

import string
import sys
import os
import re

#takes the contents of the wai file and extracts a list of names, and x, y and z coordinates.
def parseWai(wai):
	xList = []
	yList = []
	zList = []
	TTnameList = []
	TTmm = []
	waiList = wai.split("+++++++ nearby Atlas structures +++++++")
	waiList = waiList[1:]
	
	for i in range(len(waiList)):
		elm = waiList[i]
		lines = elm.split("\n")
		coords = lines[5].split("mm")
		#xList.insert(i, int(coords[0].strip(' \t\n,[]RLPSAI')))
		#yList.insert(i, int(coords[1].strip(' \t\n,[]RLPSAI')))
		#zList.insert(i, int(coords[2].strip(' \t\n,[]RLPSAI')))
		#if lines[9].startswith('***** Not near any region stored in databases *****'):
		#	TTnameList.insert(i, "No Region Found")
		#	TTmm.insert(i,"$")
		#else:
		#	ttraw = lines[9].strip('\n').split('\t')
		#	TTnameList.insert(i,ttraw[2])
		#	TTmm.insert(i,ttraw[1])
		
		# Ignore no region found areas:
		if not lines[9].startswith('***** Not near any region stored in databases *****'):
			ttraw = lines[9].strip('\n').split('\t')
			TTnameList.append(ttraw[2])
			TTmm.append(ttraw[1])
			xList.append(int(coords[0].strip(' \t\n,[]RLPSAI')))
			yList.append(int(coords[1].strip(' \t\n,[]RLPSAI')))
			zList.append(int(coords[2].strip(' \t\n,[]RLPSAI')))
		
		else:
			TTnameList.append('Unknown Region')
			TTmm.append('0.0')
			xList.append(int(coords[0].strip(' \t\n,[]RLPSAI')))
			yList.append(int(coords[1].strip(' \t\n,[]RLPSAI')))
			zList.append(int(coords[2].strip(' \t\n,[]RLPSAI')))
			
	masterList = [TTnameList,TTmm,xList,yList,zList]
	return masterList

def parseClust(clust):
	zScoreList = []
	voxelnumlst=[]
	clustList = clust.split("#---")[1].split("\n")
	clustList = clustList[1:]
	#print(clustList)
	voxVolLst=clust.split("#---")[0].split("#")
	voxVol=[]
	for b in range(len(voxVolLst)):
		if (len(voxVolLst[b]))>=23:
			if (voxVolLst[b][1:22]=='Single voxel volume ='):
				voxVolLstshort=voxVolLst[b].split(' ')
				voxVol=voxVolLstshort[4]
				voxVol=float(voxVol)

	for i in range(len(clustList) - 1):
		info = clustList[i].split()
		#print(info)
		zScoreList.append(info[12])
		#voxels=(float(info[0]))/voxVol
		#voxels=round(voxels)
		voxels=int(info[0])
		voxelnumlst.append(voxels)
	

	return [zScoreList, voxelnumlst]
	
	
	
	
def sortCSV(cmp1, cmp2, ind):
	if(cmp1 == ''):
		return 1
	if(cmp2 == ''):
		return -1

	cmp1Y = cmp1.split(',')[ind]
	cmp2Y = cmp2.split(',')[ind]
	cmp1Y = float(cmp1Y.strip(' +'))
	cmp2Y = float(cmp2Y.strip(' +'))
	return cmp(cmp2Y,cmp1Y)

def makeCSV(waiInfo, scoreInfo):
	out = []
	#print(waiInfo)
	for i in range(len(waiInfo[0])):
		region = str(waiInfo[0][i])
		mm = str(waiInfo[1][i])
		rX = str(waiInfo[2][i])
		rY = str(waiInfo[3][i])
		rZ = str(waiInfo[4][i])
		zScore = str(scoreInfo[0][i])
		vox = str(scoreInfo[1][i])
		
		curString = region+','+rX+','+rY+','+rZ+','+zScore+','+vox
		out.append(curString)
	
	out.sort(lambda x, y:sortCSV(x, y, 4))
	out.sort(lambda x, y:sortCSV(x, y, 5))
	out.insert(0, "TTRegion, X, Y, Z, zScore, Voxels")
	outString = '\n'.join(out)
	return outString 
	
##### Flow of control starts here ######

#start by getting the input
if (len(sys.argv) < 2 ):
        print Usage
else:
	File = sys.argv[1]
	if(len(sys.argv) > 2 ):
		outfile = sys.argv[2]
	else:
		outfile = File[:-3]
	
	#get the clusterfilename
	fid = open(File)
	clust = fid.read() #clusterdump
	clustList = clust.split('\n')
	if(clustList[len(clustList) - 2].strip() == "#** NO CLUSTERS FOUND ***"):
		csvFile = "Region, X, Y, Z, zScore\nNo Regions Found, 0, 0, 0, 0"
	else:
	
		#make the whereami file
		os.system("whereami -coord_file " + File + "[13,14,15] -tab > wai_" + outfile + '.txt')
		waifid = open("wai_" + outfile + '.txt')
		wai = waifid.read() #whereami file
		waifid.close()
	
		waiInfo = parseWai(wai)
		scoreInfo = parseClust(clust)
		csvFile = makeCSV(waiInfo, scoreInfo)
	
	outfid = open("table_bk_" + outfile + ".csv", "w")
	outfid.write(csvFile)
	print("File saved as table_"+outfile+ ".csv") 
