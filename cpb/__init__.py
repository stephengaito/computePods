# This is the ComputePodsBuilder (cpb) package

import click
import logging
import os
import platform
import sys
import yaml

#import cpb.build
import cpb.config
import cpb.create
#import cpb.destroy
#import cpb.enter
#import cpb.remove
#import cpb.run
#import cpb.start
#import cpb.stop
#import cpb.lists
from cpb.utils import *

########################################################################
# Handle configuration

defaultConfig = {
  'configYaml'              : "config.yaml",
  'imageYaml'               : "image.yaml",
  'cpfYaml'                 : "cpf.yaml",
  'cekitConfig'             : "cekit.ini",
  'certificateAuthorityDir' : "certAuthority",
  'podsDir'                 : "pods",
  'usersDir'                : "users",
  'verbose'                 : False
}


podDefaults = {
  'natsMsgs'           : 4222,
  'natsRouting'        : 6222,
  'natsMonitor'        : 8222,
  'syncThing'          : 22000, # both TCP and UDP
  'syncThingDiscovery' : 21027 # UDP
}

def loadConfig(configPath, verbose):
  # Start with the default configuration (above)
  config = defaultConfig
  
  # Add the global configuration (if any)
  configPath = os.path.abspath(os.path.expanduser(configPath))
  try:
    globalConfigFile = open(configPath)
    globalConfig = yaml.safe_load(globalConfigFile)
    globalConfigFile.close()
    if globalConfig is not None : 
      config.update(globalConfig)
  except :
    if verbose is not None and verbose :
      print("INFO: no global configuration file found: [{}]".format(configPath))

  # Now add in any local configuration 
  try:
    localConfigFile = open(config['configYaml'], 'r')
    localConfig = yaml.safe_load(localConfigFile)
    localConfigFile.close()
    if localConfig is not None : 
      config.update(localConfig)
  except :
    if verbose is not None and verbose :
      print("INFO: no local configuration file found: [{}]".format(config['configYaml']))

  # Now add in command line argument/options
  if verbose is not None :
    config['verbose'] = verbose
  if configPath is not None :
    config['configPath'] = configPath
  else:
    print("ERROR: a configPath must be specified!")
    sys.exit(-1)

  # Now sanitize any known configurable paths
  sanitizeFilePath(config, 'configPath', None)
  config['configDir'] = os.path.dirname(configPath)
  sanitizeFilePath(config, 'cekitConfig', config['configDir'])

  sanitizeFilePath(config, 'imageYaml', None)
  sanitizeFilePath(config, 'cpfYaml', None)
  config['curDir'] = os.path.abspath(os.getcwd())
  config['homeDir'] = os.path.expanduser("~")

  """
  # Now add in the image.yaml (if it exists)
  config['image'] = {}
  try:
    imageFile = open(config['imageYaml'], 'r')
    image = yaml.safe_load(imageFile)
    imageFile.close()
    if image is not None : 
      config['image'] = image
  except IOError : 
    if verbose is not None and verbose :
      print("INFO: could not load the image file: [{}]".format(config['imageYaml']))
  except Exception as e :
    if verbose is not None and verbose :
      print("INFO: could not load the image file: [{}]".format(config['imageYaml']))
      print("    > " + "\n    > ".join(str(e).split('\n')))
      print("  Did you remember to wrap all YAML values\n  with Jinja2 variables in quotes?")

  if 'run' not in config['image'] :
    config['image']['run'] = {}
    
  if 'user' not in config['image']['run'] :
    config['image']['run']['user'] = "root"

  if 'workdir' not in config['image']['run'] :
    config['image']['run']['workdir'] = "/root"
  """
  
  # Now add in the cpb.yaml (if it exists)
  config['cpf'] = {}
  try:
    cpfFile = open(config['cpfYaml'], 'r')
    cpf = yaml.safe_load(cpfFile)
    cpfFile.close()
    if cpf is not None : 
      config['cpf'] = cpf
  except IOError : 
    if verbose is not None and verbose :
      print("INFO: could not load the cpf file: [{}]".format(config['cpfYaml']))
  except Exception as e :
    if verbose is not None and verbose :
      print("INFO: could not load the cpf file: [{}]".format(config['cpfYaml']))
      print("\t" + "\n\t".join(str(e).split('\n')))

  # Now add in platform parameters
  thePlatform = {}
  thePlatform['system']    = platform.system()
  thePlatform['node']      = platform.node()
  thePlatform['release']   = platform.release()
  thePlatform['version']   = platform.version()
  thePlatform['machine']   = platform.machine()
  thePlatform['processor'] = platform.processor()
  config['platform']       = thePlatform
  
  # Setup logging
  if config['verbose'] :
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(levelname)s: %(message)s')

  return config

########################################################################
# Now deal with click commands

@click.group()
@click.option("-v", "--verbose",
  help="Provide more diagnostic output.",
  default=False, is_flag=True)
@click.option("--config", "config_file",
  help="The path to the global cpb configuration file.",
  default="~/.config/cpb/config.yaml", show_default=True)
@click.pass_context
def cli(ctx, config_file, verbose):
  """
    The cpb subcommands (listed below) come in a number of pairs:

      config : used to view the configuration parameters as seen by cpb,

      create/destroy : used to manage the "commons" area as well as image and cpb descriptions,

      build/remove : used to manage the podman images used by a running compute pod, 

      start/stop : used to manage the running compute pod on one machine, 

    For details on all other configuration parameters type:

        cpb <<cpbName>> config
  """
  ctx.ensure_object(dict)
  ctx.obj = loadConfig(config_file, verbose)

#cli.add_command(cpb.build.build)
cli.add_command(cpb.config.config)
cli.add_command(cpb.create.create)
#cli.add_command(cpb.destroy.destroy)
#cli.add_command(cpb.enter.enter)
#cli.add_command(cpb.lists.images)
#cli.add_command(cpb.lists.containers)
#cli.add_command(cpb.package)
#cli.add_command(cpb.remove.remove)
#cli.add_command(cpb.run.run)
#cli.add_command(cpb.stop.stop)