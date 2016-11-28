import os,sys
import configparser
import glob

if os.path.isdir('../config'):
    print('Directory Exists')
else:
    print('FATAL ERROR: Config directory not found.')
    exit(1)

config = configparser.ConfigParser()
#dirname=os.path.dirname(os.path.realpath(sys.argv[0]))
#print(dirname)

if len(glob.glob('../config/*.ini')) == 0:
    print('FATAL ERROR: No configuration files found.')
    exit(1)

for conf in glob.glob('../config/*.ini'):
    config.read(conf)

#config.read('../config/camera.ini')
#config.read('../config/event.ini')
#config.read('../config/hardware.ini')
#config.read('../config/printer.ini')
#config.read('../config/program.ini')
print(config.sections())
# config.get(), config.getint(), config.getfloat() and config.getboolean()

# Output the configuration, use fallback option to provide defaults.

# Program.ini
## General Section
print('General:PreviewAlpha=' + config.get('General','PreviewAlpha',fallback='120'))
print('General:WorkDir=' + config.get('General','WorkDir'))
print('General:SessionDir=' + config.get('General','SessionDir'))
print('General:DCIM=' + config.get('General','DCIM'))

## Interface Section
print('Interface:Mode=' + config.get('Interface','Mode'))
print('Interface:ZoneWidth=' + config.get('Interface','ZoneWidth'))

## Keyboard Section
print('Keyboard:OnScreen=' +config.get('Keyboard','OnScreen'))

## Demo Section
print('Demo:Enabled=' + config.get('Demo','Enabled'))
print('Demo:IdleTime=' + config.get('Demo','IdleTime'))
print('Demo:CycleTime=' + config.get('Demo','CycleTime'))

## PhotoSession Section
print('PhotoSession:NumPhotos=' + config.get('PhotoSession','NumPhotos'))

## Montage Section
print('Montage:MontageSpacing_W=' + config.get('Montage','MontageSpacing_W'))
print('Montage:MontageSpacing_H=' + config.get('Montage','MontageSpacing_H'))
print('Montage:Montage_W=' + config.get('Montage','Montage_W'))
print('Montage:Montage_H=' + config.get('Montage','Montage_H'))

# camera.ini
## Camera Section
print('Camera:Camera=' + config.get('Camera','Camera',fallback='rpi_v2'))
print('Camera:Rotation=' + config.get('Camera','Rotation',fallback='0'))
print('Camera:Framerate=' + config.get('Camera','Framerate',fallback='15'))
print('Camera:hflip=' + config.get('Camera','hflip',fallback='True'))

# event.ini
print('Event:Logo=' + config.get('Event', 'Logo'))
print('Effects:sketch' + config.get('Effects','sketch'))
print('Effects:posterise' + config.get('Effects','posterise'))
print('Effects:emboss' + config.get('Effects','emboss'))
print('Effects:negitive' + config.get('Effects','negitive'))
print('Effects:colorswap' + config.get('Effects','colorswap'))
print('Effects:hatch' + config.get('Effects','hatch'))
print('Effects:watercolor' + config.get('Effects','watercolor'))
print('Effects:cartoon' + config.get('Effects','cartoon'))
print('Effects:washedout' + config.get('Effects','washedout'))
print('Effects:solarize' + config.get('Effects','solarize'))
print('Effects:oilpaint' + config.get('Effects','oilpaint'))

# hardware.ini
print('Display:Width=' + config.get('Display', 'Width'))
print('Display:Height=' + config.get('Display', 'Height'))

# printer.ini
print('Printer:Enabled=' + config.get('Printer', 'Enabled'))