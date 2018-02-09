'''
A new, and much simpler, makeVec.py, -nb 11/30

Go to ###########MODIFY############# to use

To define a vector, we use python dictionary syntax.
For example:

if 'mark' is not included, mark the following vectors 1
gain_high = {
    'csv' : 'mid_mat_high.csv',
    'TR' : 1,
    'rwd' : ["+$1.00","+$5.00"] # lists engage OR syntax (rwd can be 1 or 5)
}

gvnant_high = {
    'csv' : 'mid_mat_high.csv',
    'TR' : 1,
    'rwd' : ["+$1.00", "+$5.00"],
    'mark' : {
        '1' : {
            'hit' : 1
        }
        -1 : {
             'hit' : 2
        }
    }
}

Specify the path to the definition file in vec_defs below

Debugging recommendations:

'''
import os
import numpy as np
import pandas as pd
import pdb, pprint

class VectorParser:

    def __init__(self, filename):
        self.f = filename

    def parse(self):

        self.read_lines()
        # store all vector definition dictionaries in self.vect_dic
        # and store the names of those vectors in self.vec_names
        self.translate_lines()

        self.make_vecs()

    def read_lines(self):
        f = open(self.f)
        self.lines = f.readlines()
        f.close()

    def translate_lines(self):
        blocks = []
        current_block = []
        for line in self.lines:
            if not current_block and 'BEGIN_VEC' not in line:
                continue
            if 'END_VEC' in line:
                blocks.append(current_block)
                current_block = []
                continue
            current_block.append(line.strip('\t\n '))

        vec_names = []
        vec_dicts = {}

        for block in blocks:
            vd = {}
            if block[0]!='BEGIN_VEC':
                raise SyntaxError('Improperly formatted file')
            name = ''
            mark = {}
            marker = ''
            all_marks = {}
            for line in block[1:]:

                if 'INPUT' in line:
                    vd['csv'] = line.split(':')[1].strip(' \"')
                if 'OUTPUT' in line:
                    name = line.split(':')[1].strip(' \"').split('.')[0]
                if 'MARK' in line or '=' in line:
                    if 'MARK' in line:
                        mark = {}
                    words = line.split()
                    var_name = words[words.index('=')-1]
                    val_index = words.index('=')+1
                    var_value = line.split('=')[1]
                    var_value = var_value.split('AND')[0]
                    var_value = var_value.split('WITH')[0]
                    var_value = [x.strip('\"\'\n\t') for x in var_value.split(',')]
                    #pdb.set_trace()
                    # while words[val_index] != 'WITH' and words[val_index] != 'AND':
                    #     var_value.append(words[val_index])
                    #     val_index += 1
                    mark[var_name] = var_value
                if 'WITH' in line:
                    marker =  line.split('WITH')[-1].strip()
                    all_marks[marker] = mark
            vd['mark'] = all_marks
            vec_names.append(name)
            vec_dicts[name] = vd
        pp = pprint.PrettyPrinter(depth=6)
        pp.pprint(vec_dicts)
        self.vec_names = vec_names
        self.vec_dicts = vec_dicts


    def make_vecs(self):
        names = self.vec_names

        for name in names:
            vd = self.vec_dicts[name]
            #vd is now a dictionary such as {'rwd': ['+$1.00', '+$5.00'], 'csv': 'mid_mat_high.csv', 'TR': 1}
            # for each of these, we create a new 1d file
            # print name, vd
            csv = pd.read_csv(vd['csv'])
            outputs = {}
            for mark_as in vd['mark'].keys():
                # print "\nfor mark_as", mark_as, '...'
                master_boolean = np.array(csv['TR'] > 0) #all true
                condition = vd['mark'][mark_as]
                # print "condition:", condition
                for variable, accept_values in zip(condition.keys(),condition.values()):
                    accept_bools = [
                        np.array(csv[variable].astype(str)==accept.strip('\" '))
                        for accept in accept_values
                    ]
                    lesser_boolean = np.array(accept_bools)
                    lesser_boolean = np.sum(accept_bools, axis=0).astype(bool)
                    # print lesser_boolean
                    master_boolean = master_boolean * lesser_boolean
                # print "mark_as " + mark_as + ": " + str(master_boolean)
                # print("master_boolean = " + str(master_boolean))
                # print("for variable", variable, "accept_values", accept_values)
                outputs[mark_as] = master_boolean

            final = np.array(csv['TR']<0).astype(int) # all zeros
            use_int = True
            for mark_as in outputs.keys():
                if '$' not in mark_as:
                    final = final + int(mark_as) * outputs[mark_as]
                else:
                    use_int = False
                    final = csv[mark_as.split('$')[1]] * outputs[mark_as]
            # pdb.set_trace()

            if use_int:
                np.savetxt(name + '.1D', np.round(final,6).astype(int), delimiter='\n', fmt = '%i')
            else:
                np.savetxt(name + '.1D', final, delimiter='\n', fmt = "%s")





###########MODIFY#############
#use absolute path
vec_defs = '/Users/span/projects/stockmri/scripts/stock_vecs.txt'
######## End MODIFY #############

v = VectorParser(vec_defs)
v.parse()
