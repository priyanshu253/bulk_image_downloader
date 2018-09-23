# Import Dependencies
from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os
import argparse
import sys
import json


def get_soup(prm_sURL,prm_objHeaders):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(prm_sURL,headers=prm_objHeaders)),'html.parser')

def main(args):
	v_objParser = argparse.ArgumentParser(description='Mass Google Image Downloader')
	v_objParser.add_argument('-s', '--search', default='Google Images', type=str, help='Search Term')
	v_objParser.add_argument('-n', '--num_images', default=50, type=int, help='Number of Images to Download')
	v_objParser.add_argument('-d', '--directory', default='GoogleImages/', type=str, help='Directory Location to Save Files')

	args = v_objParser.parse_args()
	v_sQuery = args.search
	max_images = args.num_images
	save_directory = args.directory
	image_type = "Action"
	v_sQuery = v_sQuery.split()
	v_sQuery = '+'.join(v_sQuery)
	v_sURL = "https://www.google.co.in/search?q=" + v_sQuery + "&source=lnms&tbm=isch"
	v_objHeaders = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
	v_objSoup = get_soup(v_sURL,v_objHeaders)
	ActualImages = []
	for v_obj in v_objSoup.find_all("div", {"class":"rg_meta"}):
	    link , Type = json.loads(v_obj.text)["ou"]  ,json.loads(v_obj.text)["ity"]
	    ActualImages.append((link,Type))
	for v_iPos , (img , Type) in enumerate( ActualImages[0:max_images]):
	    try:
	        v_objReq = urllib2.Request(img, headers={'User-Agent' : v_objHeaders})
	        v_objRawImg = urllib2.urlopen(v_objReq).read()
	        if len(Type)==0:
	            v_objFile = open(os.path.join(save_directory , "img" + "_" + str(v_iPos) + ".jpg"), 'wb')
		    v_sFileName = "img" + "_" + str(v_iPos) + ".jpg"
	        else :
	            v_objFile = open(os.path.join(save_directory , "img" + "_" + str(v_iPos) + "." + Type), 'wb')
		    v_sFileName = "img" + "_" + str(v_iPos) + "." + Type
	        v_objFile.write(v_objRawImg)
	        v_objFile.close()
		print("Downloaded: " + v_sFileName)
	    except Exception as v_exException:
	        print("could not load : " + img)
	        print(v_exException)

if __name__ == '__main__':
    from sys import argv
    try:
        main(argv)
    except KeyboardInterrupt:
        pass
    sys.exit()
