import json
import os
from glob import glob

def get_protocol_parameters(parameters):

	key_value_args = []

	for key, value in parameters.iteritems():
		if key == '-i' or key == '-o' or key == "chewBBACA_schema":
			continue
		else:
			key_value_args.append(str(key))

			if len(value.split(' ')) > 1:
				key_value_args.append("'" + str(value) + "'")
			else:
				key_value_args.append(str(value))

	return key_value_args


def process_innuca(key_value_args, parameters, user_folder, workflow):

	prev_application_steps = 'badstatus="404"; firstprocess="FirstProcess";'

	prev_application_steps += ' p_innuendo_input=$(python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -t input);'
	
	prev_application_steps += ' echo $p_innuendo_input;'

	prev_application_steps += ' if [ "$p_innuendo_input" = "$badstatus" ]; then exit 1; fi;'
	prev_application_steps += ' if [ "$p_innuendo_input" != "$firstprocess" ]; then exit 1; fi;'

	prev_application_steps += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -t set_pending;'

	#prev_application_steps += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 null -v2 null -v3 null -v4 null -v5 running -t output;'

	key_value_args.append('-i')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID'))

	key_value_args.append('-o')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID'))

	key_value_args.append('--json')

	#Log of the program run
	key_value_args.append('>')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_INNUca.txt'))

	config = {}
	execfile("config.py", config)

	#after_application_steps = '; python ' + config['FILETYPES_SOFTWARE']['INNUca'][0]['app_path'] + 'combine_reports.py -i ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID')
	after_application_steps = '; mkdir ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID;'
	#after_application_steps += ' ln -s $(cat ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/final_assembly.txt) ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca;' 
	after_application_steps += ' ln -s ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/samples_report.*.json ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_info.json;' 
	after_application_steps += ' ln -s ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/combine_samples_reports.*.json ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_stats.json;' 

	#MOVE ASSEMBly to job folder
	after_application_steps += ' ln -s $(cat '+os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID')+'/*/final_assembly.txt) '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_output.fasta;' 

	#ADD OUTPUT TO NGSONTO PROCESS
	#after_application_steps += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_output.fasta -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_innuca.txt')+ '-v5  -t output;'
	
	#STATUS DEFINITION

	status_definition = ' if [ $? -eq 0 ];then '
	status_definition += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_output.fasta -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_INNUca.txt')+ ' -v5 true -t output;'
	status_definition += ' else '
	status_definition += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_STEPID/run_output.fasta -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_INNUca.txt')+ ' -v5 false -t output;'
	status_definition += ' fi;'
	#status_definition_false = ' srun python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID/run_output.fasta -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_INNUca.txt')+ ' -v5 false -t output;'

	print after_application_steps
	return key_value_args, prev_application_steps, after_application_steps, status_definition


def process_chewbbaca(key_value_args, parameters, user_folder, workflow):
	#list of genomes
	#list of genes

	#READ CONFIG FILE
	config = {}
	execfile("config.py", config)
	schema_to_use = ""

	for key, value in parameters.iteritems():
		if key == "chewBBACA_schema":
			schema_to_use = value

	prev_application_steps = 'badstatus="404"; firstprocess="FirstProcess";'

	prev_application_steps += ' p_innuendo_input=$(python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -t input);'
	
	prev_application_steps += ' echo $p_innuendo_input;'
	prev_application_steps += ' echo SLURM_ARRAY_JOB_ID;'

	prev_application_steps += ' if [ "$p_innuendo_input" = "$badstatus" ]; then exit 1; fi;'
	prev_application_steps += ' if [ "$p_innuendo_input" = "$firstprocess" ]; then exit 1; fi;'

	prev_application_steps += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -t set_pending;'

	#prev_application_steps += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 null -v2 null -v3 null -v4 null -v5 running -t output;'

	prev_application_steps += ' find $p_innuendo_input > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenomes.txt; '


	#prev_application_steps += 'find ' + user_folder + '/SLURM_ARRAY_JOB_ID/*/*.fasta > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenomes.txt; '
	
	#if schema_to_use == "schema_coli_enterobase_V3":
		#prev_application_steps += 'find ' + 'dependencies/chewBBACA/'+schema_to_use+'/*.fasta > ' + 'dependencies/chewBBACA/' +schema_to_use+'/listGenes1.txt; '
		
	prev_application_steps += "cp dependencies/chewBBACA/"+schema_to_use+"/listGenes.txt "+ user_folder + "/SLURM_ARRAY_JOB_ID/listGenes.txt; ";

		#prev_application_steps += 'less dependencies/chewBBACA/' +schema_to_use+'/listGenes1.txt | rev | cut -d/ -f1 | rev > '+ user_folder + '/SLURM_ARRAY_JOB_ID/tocompare.txt; ';
		#prev_application_steps += "awk 'NR==FNR{a[$0]=1;next}!a[$0]' "+ user_folder + "/SLURM_ARRAY_JOB_ID/ToDeleteLoci.txt "+ user_folder + "/SLURM_ARRAY_JOB_ID/tocompare.txt > "+ user_folder + "/SLURM_ARRAY_JOB_ID/listGenes.txt; ";
 
		#prev_application_steps += "awk 'NR==FNR{a[$0]=1;next}!a[$0]' "+ user_folder + "/SLURM_ARRAY_JOB_ID/ToDeleteLoci.txt "+ 'dependencies/chewBBACA/' + '/'+schema_to_use+"/listGenes1.txt > "+ user_folder + "/SLURM_ARRAY_JOB_ID/listGenes.txt; "; 

	#else:
		#prev_application_steps += 'find ' + 'dependencies/chewBBACA/'+schema_to_use+'/*.fasta > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenes.txt; '

	prev_application_steps += ' mkdir ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID; '

	key_value_args.append('-i')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'listGenomes.txt'))

	key_value_args.append('-o')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/chewBBACA_SLURM_ARRAY_JOB_ID'))

	key_value_args.append('-b')
	key_value_args.append(config['BLAST_PATH'])

	key_value_args.append('-g')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID','listGenes.txt'))

	key_value_args.append('--cpu')
	key_value_args.append('6')

	#force proceed if already exist chewBBACA files before running
	key_value_args.append('--fc')

	key_value_args.append('--json')

	#Log of the program run
	key_value_args.append('>')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_chewBBACA.txt'))

	
	after_application_steps = ''

	#MOVE RESULTS to job folder
	after_application_steps += '; rm -rf dependencies/chewBBACA/campy_scheme_2017/genes/temp;'
	after_application_steps += ' mv ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/chewBBACA_SLURM_ARRAY_JOB_ID')+'/results_*/reportStatus.json '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_info.json;'
	after_application_steps += ' mv ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/chewBBACA_SLURM_ARRAY_JOB_ID')+'/results_*/results_alleles.json '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_output.json;'
	after_application_steps += ' mv ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/chewBBACA_SLURM_ARRAY_JOB_ID')+'/results_*/results_statistics.json '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_stats.json;'
	
	#ADD OUTPUT TO NGSONTO PROCESS
	#after_application_steps += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_output.json -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_chewbbaca.txt')+ ' -t output;'

	#STATUS DEFINITION
	status_definition = ' if [ $? -eq 0 ]; then '
	status_definition += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_output.json -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_chewBBACA.txt')+ ' -v5 true -t output;'
	status_definition += ' else '
	status_definition += ' python job_processing/get_program_input.py --project ' + workflow["project_id"] + ' --pipeline ' + workflow["pipeline_id"] + ' --process ' + workflow["process_id"] + ' -v1 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_info.json -v2 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_stats.json -v3 ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_STEPID/run_output.json -v4 ' +os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'log_output_chewBBACA.txt')+ ' -v5 false -t output;'
	status_definition += ' fi;'

	print after_application_steps
	return key_value_args, prev_application_steps, after_application_steps, status_definition
	


def process_parameters(parameters, user_folder, workflow):

	#READ CONFIG FILE
	config = {}
	execfile("config.py", config)

	options = {'INNUca':process_innuca, 'chewBBACA':process_chewbbaca}

	wf_params = json.loads(workflow['parameters'])
	if wf_params['used Software'] in config['APPLICATIONS_ARRAY']:
		software = wf_params['used Software']

	options = {'INNUca':process_innuca, 'chewBBACA':process_chewbbaca}

	key_value_args = get_protocol_parameters(parameters)
	key_value_args, prev_application_steps, after_application_steps, status_definition = options[software](key_value_args, parameters, user_folder, workflow)


	return key_value_args, prev_application_steps, after_application_steps, status_definition