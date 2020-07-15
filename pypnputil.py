import subprocess as sb
import re
import platform
import sys

class pnpdevice:

    def __init__(self,instanceid,description,className,classGUID,manufacturer,status,driverName,driver = None, hardware_ids = None,compatible_ids = None):
        self.instanceid = instanceid
        self.description = description
        self.className = className
        self.classGUID = classGUID
        self.manufacturer = manufacturer
        self.status = status
        self.driverName = driverName
        self.driver = driver
        self.hardware_ids = hardware_ids
        self.compatible_ids = compatible_ids

class pnpdriver:

    def __init__(self,publishName,originName,provider,className,classGUID,driverDate,driverVer,publisher,extendID=None):
        self.publishName  = publishName
        self.originName = originName
        self.provider   = provider
        self.className  = className
        self.classGUID  = classGUID
        self.driverDate = driverDate
        self.driverVer  = driverVer
        self.publusher  = publisher
        self.extendID   = extendID

class pnpinterface:

    def __init__(self,path,description,classGUID,refString,deviceInstanceID,status):
        self.path = path
        self.description = description
        self.classGUID = classGUID
        self.refString = refString
        self.deviceInstanceID = deviceInstanceID
        self.status = status
        
    
class pnputil:

    global process
    if '32bit' in platform.architecture():
        process = [r'%systemroot%\Sysnative\pnputil.exe']
    else:
        process = [r'pnputil.exe']
    
    @staticmethod
    def get_or_None(a_list):
        return a_list[0] if a_list else None

    @staticmethod
    def __device_parse__(string):
        devices = []
        strings = string.split('\n\n')
        for i in strings:
            if not 'Microsoft PnP' in i and i != None and i != '':
                instanceid      = pnputil.get_or_None(re.findall('Instance ID:\s*(.*)',i))
                description     = pnputil.get_or_None(re.findall('Device Description:\s*(.*)',i))
                className       = pnputil.get_or_None(re.findall('Class Name:\s*(.*)',i))
                classGUID       = pnputil.get_or_None(re.findall('Class GUID:\s*(.*)',i))
                manufacturer    = pnputil.get_or_None(re.findall('Manufacturer Name:\s*(.*)',i))
                status          = pnputil.get_or_None(re.findall('Status:\s*(.*)',i))
                driverName      = pnputil.get_or_None(re.findall('Driver Name:\s*(.*)',i))
                parent          = pnputil.get_or_None(re.findall('Parent:\s*(.*)',i))
                if instanceid or description or className or classGUID or manufacturer or status or driverName or parent:
                    device      = pnpdevice(instanceid,description,className,classGUID,manufacturer,status,driverName)
                    devices.append(device)
        return devices

    @staticmethod
    def __interface_parse__(string):
        interfaces = []
        strings = string.split('\n\n')
        for i in strings:
            if not 'Microsoft PnP' in i and i != None and i != '':
                path                = pnputil.get_or_None(re.findall('Interface Path:\s*()',i))
                description         = pnputil.get_or_None(re.findall('Interface Description:\s*(.*)',i))
                classGUID           = pnputil.get_or_None(re.findall('Interface Class GUID:\s*(.*)',i))
                refString           = pnputil.get_or_None(re.findall('Reference String:\s*(.*)',i))
                deviceInstanceID    = pnputil.get_or_None(re.findall('Device Instance ID:\s*(.*)',i))
                status              = pnputil.get_or_None(re.findall('Interface Status:\s*(.*)',i))
                if path or description or classGUID or refString or deviceInstanceID or status:
                    interface           = pnpinterface(path,description,classGUID,refString,deviceInstanceID,status)
                    interfaces.append(interface)
        return interfaces

    @staticmethod
    def __driver_parse__(string):
        drivers = []
        strings = string.split('\n\n')
        for i in strings:
            if not 'Microsoft PnP' in i and i != None and i != '':
                    publishName = pnputil.get_or_None(re.findall('Published Name:\s*(.*)',i))
                    originName  = pnputil.get_or_None(re.findall('Original Name:\s*(.*)',i))
                    provider    = pnputil.get_or_None(re.findall('Provider Name:\s*(.*)',i))
                    className   = pnputil.get_or_None(re.findall('Class Name:\s*(.*)',i))
                    classGUID   = pnputil.get_or_None(re.findall('Class GUID:\s*(.*)',i))
                    driverVer   = pnputil.get_or_None(re.findall('Driver Version:\s*(.*)',i))
                    driverDate = None
                    if driverVer:
                        driverDate,driverVer = driverVer.split('\n')
                    signerName = pnputil.get_or_None(re.findall('Signer Name:\s*(.*)',i))

                    if publishName or originName or provider or className or classGUID or driverVer or driverDate or signerName:
                        driver = pnpdriver(publishName,originName,provider,className,classGUID,driverDate,driverVer,signerName)
                        drivers.append(driver)
        return drivers

    @staticmethod
    def __catch_info_after_colon__(string):
        if string != None:
            string = str(string)
            return string[string.rfind(':')+1:]

    @staticmethod
    def __call_pnputil__(cmd):
        p = sb.Popen(cmd,shell=True,stdout=sb.PIPE,stderr=sb.PIPE,stdin=sb.PIPE,universal_newlines=True,errors='ignore')
        ret = p.poll()
        stdout,error = p.communicate()

        if ret == 0 or ret==None:
            
            if '/?' in stdout:
                print(f'input error {" ".join(cmd)}')
                return None
            else:
                return stdout
        else:
            print(f'input error {" ".join(cmd)}')
            return None


    @staticmethod
    def add_driver(path,subdirs=False,install=False,reboot=False):
        if path:
            cmd=[]
            cmd = process.copy()
            cmd.append('/add-driver')
            cmd.append(path)

            if subdirs:
                cmd.append('/subdirs')
            if install:
                cmd.append('/install')
            if reboot:
                cmd.append('/reboot')
            
            stdout = pnputil.__call_pnputil__(cmd)
            print(stdout)


    @staticmethod
    def delete_driver(path,uninstall=False,force=False,reboot=False):
        if path:
            cmd=[]
            cmd = process.copy()
            cmd.append('/delete-driver')
            cmd.append(path)

            if uninstall:
                cmd.append('/uninstall')
            if force:
                cmd.append('/force')
            if reboot:
                cmd.append('/reboot')
            
            stdout = pnputil.__call_pnputil__(cmd)
            print(stdout)

    @staticmethod
    def export_driver(src,dest):
        pass   

    @staticmethod
    def enum_drivers():
        drivers = None
        cmd=[]
        cmd = process.copy()
        cmd.append('/enum-drivers')
        stdout = pnputil.__call_pnputil__(cmd)
        if 'GUID' in stdout:
            print(stdout)
            drivers = pnputil.__driver_parse__(stdout)
        return drivers

    @staticmethod
    def enum_devices(connected=None,instanceid=None,ClassOrGUID=None,problem=None,ids=False,relations=False,drivers=False):
        devices = None
        cmd=[]
        cmd = process.copy()
        cmd.append('/enum-devices')
        if connected != None:
            if connected:
                cmd .append('/connected')
            else:
                cmd.append('/disconnected')
        if instanceid:
            cmd.append('/instanceid')
            cmd.append(instanceid)
        if ClassOrGUID:
            cmd.append('/class')
            cmd.append(ClassOrGUID)
        if problem:
            cmd.append('/problem')
            for p in problem:
                cmd.append(p)
        if ids:
            cmd.append('/ids')
        if relations:
            cmd.append('/relations')
        if drivers:
            cmd.append('/drivers')

        p = sb.Popen(cmd,shell=True,stdout=sb.PIPE,stderr=sb.PIPE,stdin=sb.PIPE,universal_newlines=True,errors='ignore')
        ret = p.poll()
        print(f'{cmd} = {ret}')
        if ret == 0 or ret==None:
            stdout,stderr = p.communicate()
            if '/?' in stdout:
                print(f'input error {" ".join(cmd)}')
                print(stderr)
            else:
                print(stderr)
                devices = pnputil.__device_parse__(stdout)
        return devices

    @staticmethod
    def disable_device(self,instanceid=None,reboot=False):
        pass

    @staticmethod
    def enable_device(self,instanceid=None,reboot=False):
        pass

    @staticmethod
    def remove_device(self,instanceid=None,subtree=True,reboot=False):
        pass

    @staticmethod
    def scan_device(instanceid=None,Async=False):
        pass

    @staticmethod
    def restart_device(instanceid=None,reboot=False):
        pass

    @staticmethod
    def enum_interafces(enabled=None,Class=None):
        interfaces = None
        cmd=[]
        cmd = process.copy()
        cmd.append('/enum-interfaces')

        if enabled != None:
            if enabled:
                cmd.append('/enabled')
            else:
                cmd.append('/disabled')
        
        if Class:
            cmd.append('/class')
            cmd.append(Class)

        stdout = pnputil.__call_pnputil__(cmd)
        # if stdout and 'GUID' in stdout:
        #     interfaces = pnputil.__interface_parse__(stdout)
        
        # return interfaces
        print(stdout)




class infDriver(pnputil):
    def __init__(self,path):
        if path.lower().index('.inf') > -1:
            self.path = path
            with open(self.path,'r',errors='ignore') as f:
                self.inf = f.read().replace('\x00','').lower()
                self.Class = pnputil.get_or_None(re.findall('class\s*=\s*(\w+)',self.inf))

                self.classGUID = pnputil.get_or_None(re.findall('classguid\s*=\s*(.{1,300}})',self.inf))
                devices = pnputil.enum_devices()
                verdate = pnputil.get_or_None(re.findall('driverver\s*=\s*(.{1,50})\s*;',self.inf))
                self.driverDate = None
                self.driverVer  = None
                if verdate:
                    self.driverDate,self.driverVer = verdate.replace(';','').strip().split(',')

                self.supporthwids = list(set(re.findall(r'(pci\\ven.*)\s,',self.inf)))

                self.currenthwid = None
                self.currentDriver = None

                if devices:
                    devices = [device for device in devices for shwid in self.supporthwids if device.instanceid.lower().find(shwid) > -1]
                    self.currenthwid   = pnputil.get_or_None(devices).instanceid
                    self.currentDriver = pnputil.get_or_None(devices).driverName

        else:
            print('not an inf file')
            raise Exception

    def install(self):
        pnputil.add_driver(self.path,install=True)

    def uninstall(self):
        pnputil.delete_driver(self.path,uninstall=True,force=True)

    def fullreplace(self):
        if self.currentDriver:
            pnputil.delete_driver(self.currentDriver,uninstall=True,force=True)
        pnputil.add_driver(self.path,install=True)
    def show(self):
        info = f'''
        path            {self.path}
        class           {self.Class}
        class guid      {self.classGUID}
        driver date     {self.driverDate}
        driver Ver      {self.driverVer}

        currenthwid     {self.currenthwid}
        currentdriver   {self.currentDriver}
        '''
        print(info)

        
    
        




if __name__ == "__main__":
    args = sys.argv
    inf = infDriver(args[1])
    # inf = infDriver(r'D:\Work\HP_Project\pnputil_py\testinf\netwtw08.inf')
    if inf:
        print(f'found driver {inf.path}')
        args = input('''
        -i      for install
        -u      for uninstall
        -r      for clean current driver and replace this driver
        -s      show inf information
        ''')
        if args == '-i':
            inf.install()
        elif args == '-u':
            inf.uninstall()
        elif args == '-r':
            inf.fullreplace()
        elif args == '-s':
            inf.show()

        

    
