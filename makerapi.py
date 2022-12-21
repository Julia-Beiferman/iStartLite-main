from pyhubitat import MakerAPI

token = '05bd79b6-5309-455b-9b8c-8ae67212afea'
url = 'http://192.168.0.101/apps/api/673'

ph = MakerAPI(token, url)
devices = ph.list_devices() #returns dictionary of devices
print(devices)

for i in range (0,3):
    print(i)