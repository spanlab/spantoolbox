"""A script for converting AFNI maps of t-stats to tables of cluster info"""
# on a mac, you may need to run 
#!/usr/bin/env python
# NB 11/17
from __future__ import print_function
import os
import subprocess
import pdb
import time
import urllib2
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pprint import pformat, pprint
import pandas as pd

# you'll need to use pip to install selenium, pandas, lxml if not installed 
# you will need ot install https://sites.google.com/a/chromium.org/chromedriver/downloads
# and set its path
DRIVER_PATH = '/Users/span/spantoolbox/group_analysis/chromedriver'

def string_is_numeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

class wait_for_display(object):
    """ Helper function for scraping Neurosynth"""
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = EC._find_element(driver, self.locator)
            return element.value_of_css_property("display") == "none"
        except StaleElementReferenceException:
            return False

class Cluster(object):
    """ Object for storing cluster info and performing NS and WAI lookup"""

    def __init__(self, att_list):
        names = ['volume', 'cm_rl', 'cm_ap', 'cm_is', 'min_rl', 'max_rl', 
                 'min_ap', 'max_ap', 'min_is', 'max_is','mean', 'sem',
                  'zScore', 'mi_rl', 'mi_ap', 'mi_is']
        for at, name in zip(att_list, names):
            setattr(self, name, at)

    def __str__(self):
        return pformat(vars(self))

    def __repr__(self):
        return pformat(vars(self))

    def whereami(self):
        # Get WAI coords for COM
        cm_command = ['whereami', self.cm_rl, self.cm_ap, self.cm_is , #'50', '50', '90',
                      '-atlas', 'TT_Daemon', '-tab']
        cm_out = subprocess.check_output(cm_command).split('\n')
        self.cm_ttc, self.cm_mnic, self.cm_names = self.parse_wai_output(cm_out)

        # Get WAI coords for PEAK
        peak_command = ['whereami', self.mi_rl, self.mi_ap, self.mi_is,
                        '-atlas', 'TT_Daemon', '-tab']
        peak_out = subprocess.check_output(peak_command).split('\n')
        for i,x in enumerate(peak_out): print(i,x)
        self.peak_ttc, self.peak_mnic, self.peak_names = self.parse_wai_output(peak_out)

    def parse_wai_output(self, out):
        tt_coords= [x.strip(' \t\n,[]RLPSAI') for x in out[6].split("mm")][:3]
        mni_coords= [x.strip(' \t\n,[]RLPSAI') for x in out[7].split("mm")][:3]

        tt_names = []
        if out[10].startswith('***** Not near any region stored in databases *****'):
            tt_names = ['Unknown Region']
        else:
            for i, x in enumerate(out[10:]):
                x = [y.strip() for y in x.split('\t')]
                if x[0] == 'TT_Daemon':
                    tt_names.append(x[2])

        return tt_coords, mni_coords, '; '.join(tt_names)


    def neurosynth_lookup(self, driver):
        self.neurosynth_associations = []

        url = 'http://www.neurosynth.org/locations/' + '_'.join(self.peak_mnic) + '_6'
        driver.get(url)
        # wait for the associations to load
        try:
            wait = WebDriverWait(driver, 10, poll_frequency=0.1)
            element = wait.until(wait_for_display((By.ID, 'location_analyses_table_processing')))
        except TimeoutException:
            return

        # time.sleep(4)
        #<div id="location_analyses_table_processing" class="dataTables_processing" style="display: none;">Processing...</div>
        associations = driver.find_element_by_xpath('//*[@id="location-menu"]/li[3]/a')
        associations.click()
        table_html = driver.find_element_by_id('location_analyses_table').get_attribute('outerHTML')
        new_table = pd.read_html(table_html)[0]
        new_table.columns = ['Name', 'Z-score', 'Posterior', 'FC', 'MACoact']
        pprint(new_table)
        for i, row in new_table.iterrows():
            self.neurosynth_associations.append('; '.join([str(x) for x in row.tolist()]))



class ClusterTable(object):
    """Class for generating clusters tables from t-stat maps in map_dir"""

    def __init__(self, maps, map_dir, t_index=1, neurosynth=True):
        super(ClusterTable, self).__init__()
        """store the names and path of the maps to cluster tstats in "names" 
           at t-index (should be one for ttest++ output)"""
        self.maps = maps
        self.map_dir = map_dir
        # create list of tuples for storing (z, clustdict_for_z)
        self.clust_tuples= []
        self.t_index = t_index
        self.neurosynth = neurosynth
        if self.neurosynth:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')        
            self.driver = webdriver.Chrome(
                DRIVER_PATH, 
                chrome_options=options
            )

    def __del__(self):
        if self.neurosynth:
            try:
                self.driver.quit()
            except RuntimeError:
                pass

    def gen_clusters(self, zstat, write_1D=False):
        """call 3dclust with threshold stat, store in dict[map]=clusters
           if write_1d is True, write 3dclust output to a 1d in working dir
           if neurosynth == True, then perform lookup on every cluster"""
        zdict = dict()
        for m in self.maps:
            cmd = self.clust_command(m, zstat)
            output = subprocess.check_output(cmd)
            if write_1D:
                outname = '_'.join([m, str(zstat), 'clusters']) + '.1D'
                with open(outname, 'w') as f:
                    f.write(output)
            zdict[m] = self.parse_3dclust_output(output)
        self.clust_tuples.append((zstat, zdict))

    def clust_command(self, map_name, zstat):
        """returns command to 3dclust, see docs if you need them"""
        full_map_path = os.path.join(self.map_dir, map_name + '+tlrc.BRIK')
        clust_command = ['3dclust', '-nosum',  '-1dindex', '1', '-1tindex',
                         str(self.t_index), '-2thresh', 
                         str(float(-zstat)), str(float(zstat)), 
                         '-dxyz=1', '0', '3', full_map_path]
        print(' '.join(clust_command))
        return clust_command

    def parse_3dclust_output(self, out):
        """function for parsing 3dclust output for running WAI and NS lookup"""
        clusters = []
        past_header = False
        for l in out.split('\n'):
            if all([string_is_numeric(x) for x in l.split()]):
                past_header = True
            if past_header:
                c = Cluster(l.split())
                use_neurosynth = self.neurosynth
                try:
                    c.whereami()
                    if self.neurosynth:
                        c.neurosynth_lookup(self.driver)
                except AttributeError:
                    pass
                print(c)
                clusters.append(c)
                #return clusters
        return clusters


    def _write_csv(self, clusters, name, header_format):
        with open(name, 'w') as f:
            header = ",".join(header_format.values())
            print(header, file=f)

            for c in clusters:
                try:
                    l = []
                    for h in header_format.keys():
                        x = getattr(c,h)
                        if isinstance(x, list):
                            x = ','.join(x)
                        l.append(x)
                    print(','.join(l), file=f)
                except:
                    pass






    def write_csvs(self, header):
        '''For every z value: for each map: write clusters to csv'''
        for z, clusters_for_maps in self.clust_tuples:
            for m in clusters_for_maps.keys():
                cluster_list = clusters_for_maps[m]
                outfile = '_'.join([m, str(z)]) + '.csv'
                self._write_csv(cluster_list, outfile, header)


    



if __name__ == '__main__':
    map_dir = os.getcwd()
    # map names should correspond to files ending in +tlrc.BRIK/HEAD in map_dir
    maps = ['inflection']

    #Create the table object
    ct = ClusterTable(maps, map_dir, neurosynth=True)

    # generate the clusters
    z_value = 2.805 # for 2 tailed p < .005, use 3.3 for < .001
    ct.gen_clusters(z_value, write_1D=False) 

    # specify the output format: this is the mapping between vars and csv column
    # names. Comment out lines you don't want and change the right side to change
    # the csv column name (obviously don't use commas). Leave the left as is.

    header_format = OrderedDict([
        ('cm_names' , 'TT_Regions_CM'),        # tlrc map names for cm,  ; separated
        ('peak_names', 'TT_Regions_Peak'),     #     ""    ""   for peak ; separated
        ('peak_mnic' , 'PMNI_X,PMNI_Y,PMNI_Z'), # MNI coords RAI for peak, x, y, z
        ('peak_ttc' , 'PTT_X,PTT_Y,PTT_Z'),    # tlrc coords RAI for peak
        ('cm_mnic'  , 'CMNI_X,CMNI_Y,CMNI_Z'),  # MNI coords RAI for cm
        ('cm_ttc'    , 'CMTT_X,CM_TTY,CM_TTZ'), # tlrc coords RAI for cm
        ('volume'   , 'Voxels'),                # size in voxels of cluster,
        ('zScore'   , "Peak_zScore"),           # Z_score (i.e. the peak value, max_int in 3dclust)
        ('neurosynth_associations' , ','.join(['NS_' + str(x) for x in range(1,11)]))  # NS_1,...,NS_10, for the peak
    ])

    #write the csvs
    ct.write_csvs(header_format)


