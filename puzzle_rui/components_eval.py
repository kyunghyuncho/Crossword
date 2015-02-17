#chmod +x components_eval.py

# evaluate all components that are specified in component list file
# component list file have list of componets to be evaluated, described as below.
# 	component_path1	  1
# 	component_path2	  0
# 	component_path3	  1
# '1': include the given component,  '0': omit the given component
#
# Seungbum

import sys
import component_test
import os

# Modify component list to be evaluated based on 'include' and 'omit' lists
def mod_component_list(component_list_path, i_list, o_list):
	f = open(component_list_path, 'r')
	comp_list=[]
	while 1:
		line = f.readline()
		if not line: break
		arr=line.split()
		if len(line)>2 and arr[1]=='1':
			comp_list.append(arr[0])
	if i_list:
		for comp in i_list:
			try:
				index=comp_list.index(comp)  # exist -> do nothing
			except ValueError:
				comp_list.append(comp)
	if o_list:
		for comp in o_list:
			try:
				index=comp_list.index(comp)   # exist -> delete
				del comp_list[index]
			except ValueError:
				pass
	return comp_list			


def run_all_components(puz_file, component_list_path, eval=True):
	comp_list=mod_component_list(component_list_path, '', '')
	concat_output=''
	N_comp, avg_MRAR, avg_Precision, avg_Attempt_ratio = 0,0,0,0
	comps_eval={}
	for component_path in comp_list:
		comp_name=component_path.split('/')
		comp_name=comp_name[len(comp_name)-1]
		print "Try to solve", puz_file, "using", comp_name
		eval_result,output=component_test.run_test(puz_file, component_path)
		if eval_result != None:
			N_comp=N_comp+1.0
			avg_MRAR, avg_Precision, avg_Attempt_ratio = avg_MRAR+eval_result['MRAR'], avg_Precision+eval_result['Precision'], avg_Attempt_ratio+eval_result['Attempt_ratio']
			comps_eval[component_path]=eval_result
			for line in output[0].split('\n'):
				if line == "":
					continue
				concat_output=concat_output+line+'\t'+comp_name+'\n'
			print puz_file, eval_result
		else:
			print comp_name, ": No attempts to solve clues in",puz_file,"were made..."
	if N_comp != 0:
		avg_MRAR, avg_Precision, avg_Attempt_ratio = avg_MRAR/N_comp, avg_Precision/N_comp, avg_Attempt_ratio/N_comp
		avg_eval={'avg_MRAR':avg_MRAR, 'avg_Precision':avg_Precision, 'avg_Attempt_ratio':avg_Attempt_ratio}
		eval={'avg_eval':avg_eval, 'comps_eval':comps_eval}
		return concat_output, eval
	else:
		return concat_output, None


# Main function: run component_test.py for each component, and merge entire test results
def main(argv):
	argv=parsing_argv(argv)
	puz_dir=argv['puz_dir']
	comp_list=mod_component_list(argv['comp_list_path'], argv['i_list'], argv['o_list'])
	pathOut=argv['pathOut']
	print "evaluated component list:",comp_list,"\n"
	outputs={}
	total_result={}
	MRAR_sum=0
	N=0;	
	for component_path in comp_list:
		output=component_test.run_all(puz_dir, component_path)
		outputs[component_path]=output
		print "Component :",component_path,"\n", "Overall average",output,"\n"
	
	if pathOut:
		if os.path.isfile(pathOut):
			f=open(pathOut,'a')
		else: 
			f=open(pathOut,'w')
		f.write("==== Evaluation Result ====\n")
		f.write("puz_dir: "+puz_dir+"\n")
		f.write("Evaluated components list: "+str(comp_list)+"\n\n")
	print "==== Evaluation Result ===="
	print "Evaluated components list:",comp_list,"\n"
	for key in outputs.keys():
		temp_comp=outputs[key]
		MRAR_sum+=temp_comp['MRAR']
		N+=1
		if pathOut:
			f.write("Component: "+str(key)+"|| Overall average: "+str(temp_comp)+"\n")
		print "Component:",key,"||", "Overall average",temp_comp
	
	total_result['MRAR_total']=float(MRAR_sum)/N
	total_result['N_components']=N
	
	if pathOut:
		f.write("\nTotal Evaluation: "+str(total_result)+"\n\n\n")
		f.close()
	print "\nTotal Evaluation",total_result


# Parsing arguments
def parsing_argv(argv):
	comp_list_path=argv.pop()
	puz_dir=argv.pop()
	pathOut=''
	i_list=[]
	o_list=[]
	if len(argv)!=0:
		try:
			i=argv.index("-i")
		except ValueError:
			i=-1
		try:
			o=argv.index("-o")
		except ValueError:
			o=-1
		try:
			w=argv.index("-w")
			pathOut=argv[w+1]
			del argv[w:w+2]
		except ValueError:
			pass	
		if i !=-1 and o != -1:
			if i<=o:
				i_list = argv[i+1:o]
				o_list = argv[o+1:]
			else:
				o_list = argv[o+1:i]
				i_list = argv[i+1:]
		elif i !=-1 and o == -1:
			i_list = argv[i+1:]
		elif i ==-1 and o != -1:
			o_list = argv[i+1:]
	result = {"pathOut":pathOut, "puz_dir":puz_dir, "comp_list_path":comp_list_path, "i_list":i_list, "o_list":o_list}
	return result

def usage():
    print "usage: ./components_eval.py [-i component_name(s)] [-o component_name(s)] [-w pathOut] <puz_path(single file or directory)> <path_to_component_list_file> "
    print "-w\tevalutation result output path"
    print "-i\tinclude the specified component(s)"
    print "-o\tomit the specified component(s)"

if __name__ == "__main__":
	if len(sys.argv)>1:
		main(sys.argv[1:])
	else:
		usage()
