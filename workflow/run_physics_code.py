# STRATEGY: USE PYUAL ONLY TO CALL ACTORS,
# FOR THE REST USE PYTHON IMAS API'S DIRECTLY
# --------------------------------------------
def not_timed_HL(par_path):
 
  import imas,os,sys,copy
  sys.path.append('interface')
  sys.path.append('workflow')
  sys.path.append(os.getcwd())
  from lxml import etree
  import xml.etree.ElementTree as ET
  
  
    # IMPORT PARAMETERS FROM XML --------------------------------------
  
  tree = ET.parse(par_path+'/input_workflow.xml')
  root = tree.getroot()

  param = {}
  
  print('----- WORKFLOW PARAMETERS ----')

  for elem in root.iter():
    if len(elem) == 0:
      try:
        param[elem.tag] = int(elem.text)
      except:
        try:
          param[elem.tag] = float(elem.text)
        except:
          param[elem.tag] = elem.text

      param['input_path'] = par_path
      print(elem.tag, ' = ', param[elem.tag])
     
  # LOCAL DATABASE ENVIRONMENT
  user_in     = param['user']
  local_user  = os.getenv('USER')
  tokamakname = param['machine'] # assumed to be the same for remote/local DB
  tokamakname_out = param['machine_out']
  version     = os.getenv('IMAS_VERSION')[0]
  
  # IMPORT MODULE(S) FOR SPECIFIC PHYSICS CODE(S)
  actor_path = os.path.join(os.getenv('KEPLER'), 'imas/src/org/iter/imas/python')
  list_of_actors = ['ligka','helena_imas']
  for name in list_of_actors:
    sys.path[:0] = [os.path.join(actor_path,name)]
    globals()[name] = getattr(__import__(name), name)

  
  
  # If the local database for the required tokamak does not exist yet: create it    
  if not os.path.exists(os.getenv('HOME')+'/public/imasdb/'+tokamakname):
    print('--> Create local database '+os.getenv('HOME')+'/public/imasdb/'+tokamakname)
    os.popen("imasdb "+tokamakname).read()
  
  
  #user = os.getenv('USER')
  #tokamakname = 'ligka_python'
  #version = os.getenv('IMAS_VERSION')[0]

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  print('=> Open input datafile')
  input = imas.ids(param['shot_nr'],param['run_in'],0,0)
  input.open_env(user_in,tokamakname,version)

  # READ INPUT IDS'S FROM LOCAL ATABASE
  print('=> Read input IDSs')
  input.equilibrium.get()
  input.core_profiles.get()
  input.close()
  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(param['shot_nr'],param['run_out'],0,0)

  # EXECUTE PHYSICS CODE(HELENA+LIGKA)
  print('=> Execute physics code')
  output.equilibrium = helena_imas(input.equilibrium)
  print('HELENA FINISHED, STARTING LIGKA')
  output.mhd_linear = ligka(output.equilibrium,input.core_profiles,'input/z_ligka.xml')
  print('LIGKA FINISHED')
  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Export output IDSs to local database =>',tokamakname_out)
  output.create_env(local_user,tokamakname_out,version)
  output.mhd_linear.put()
  output.close()
  print('Done exporting.')