import os
import subprocess as sb
import re

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
    process = ['pnputil']
    
    @staticmethod
    def __device_parse__(string):
        devices = []
        strings = string.split('\n\n')
        for i in strings:
            if not 'Microsoft PnP' in i and i != None and i != '':
                lines = i.split('\n')
                instanceid = pnputil.__catch_info_after_colon__(lines[0]).strip()
                description = pnputil.__catch_info_after_colon__(lines[1]).strip()
                className = pnputil.__catch_info_after_colon__(lines[2]).strip()
                classGUID = pnputil.__catch_info_after_colon__(lines[3]).strip()
                manufacturer = pnputil.__catch_info_after_colon__(lines[4]).strip()
                status = pnputil.__catch_info_after_colon__(lines[5]).strip()
                driverName = pnputil.__catch_info_after_colon__(lines[6]).strip()
                device = pnpdevice(instanceid,description,className,classGUID,manufacturer,status,driverName)
                devices.append(device)
        return devices

    @staticmethod
    def __interface_parse__(string):
        interfaces = []
        strings = string.split('\n\n')
        for i in strings:
            if not 'Microsoft PnP' in i and i != None and i != '':
                lines = i.split('\n')
                path = pnputil.__catch_info_after_colon__(lines[0]).strip()
                description = pnputil.__catch_info_after_colon__(lines[1]).strip()
                classGUID = pnputil.__catch_info_after_colon__(lines[2]).strip()
                refString = pnputil.__catch_info_after_colon__(lines[3]).strip()
                deviceInstanceID = pnputil.__catch_info_after_colon__(lines[4]).strip()
                status = pnputil.__catch_info_after_colon__(lines[5]).strip()
                interface = pnpinterface(path,description,classGUID,refString,deviceInstanceID,status)
                interfaces.append(interface)
        return interfaces

    def __driver_parse__(string):
        drivers = []
        strings = string.split('\n\n')
        for i in strings:
            if not 'Microsoft PnP' in i and i != None and i != '':
                lines = i.split('\n')
                if len(lines) <= 7:
                    publishName = pnputil.__catch_info_after_colon__(lines[0]).strip()
                    originName = pnputil.__catch_info_after_colon__(lines[1]).strip()
                    provider = pnputil.__catch_info_after_colon__(lines[2]).strip()
                    className = pnputil.__catch_info_after_colon__(lines[3]).strip()
                    classGUID = pnputil.__catch_info_after_colon__(lines[4]).strip()
                    extendID = None
                    if '{' in lines[5]:
                        extendID = pnputil.__catch_info_after_colon__(lines[5])
                        driverDate,driverVer = pnputil.__catch_info_after_colon__(lines[6]).strip().split(' ')
                        signerName = pnputil.__catch_info_after_colon__(lines[7]).strip()
                    else:
                        driverDate,driverVer = pnputil.__catch_info_after_colon__(lines[5]).strip().split(' ')
                        signerName = pnputil.__catch_info_after_colon__(lines[6]).strip()
                    driver = pnpdriver(publishName,originName,provider,className,classGUID,driverDate,driverVer,signerName,extendID)
                    drivers.append(driver)
        return drivers

    @staticmethod
    def __catch_info_after_colon__(string):
        if string != None:
            string = str(string)
            return string[string.rfind(':')+1:]

    @staticmethod
    def __call_pnputil__(cmd):
        p = sb.Popen(cmd,shell=True,stdout=sb.PIPE,universal_newlines=True)
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

        p = sb.Popen(cmd,shell=True,stdout=sb.PIPE,universal_newlines=True)
        ret = p.poll()

        if ret == 0 or ret==None:
            stdout = p.communicate()[0]
            if '/?' in stdout:
                print(f'input error {" ".join(cmd)}')
            else:
                print(stdout)
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
        
        if '.inf' in path.lower():
            self.path = path
            with open(self.path,'r',errors='ignore') as f:
                self.inf = f.read().replace('\x00','').lower()
                self.Class = re.findall('class\s*=\s*(\w+)',self.inf)[0]
                self.classGUID = re.findall('classguid\s*=\s*(.{1,300}})',self.inf)[0]
                self.driverDate,self.driverVer = re.findall('driverver\s*=\s*(.{1,50})\s*;',self.inf)[0].replace(';','').strip().split(',')
                self.supporthwids = list(set(re.findall(r'(pci\\ven.*)\s,',self.inf)))
                devices = pnputil.enum_devices(ClassOrGUID=self.Class)
                devices = [device for device in devices for shwid in self.supporthwids if device.instanceid.lower().find(shwid) > -1]
                if len(devices) == 1:
                    self.currenthwid   = devices[0].instanceid
                    self.currentDriver = devices[0].driverName
        else:
            raise ValueError

    def install(self):
        pnputil.add_driver(self.path,install=True)

    def uninstall(self):
        pnputil.delete_driver(self.path,uninstall=True,force=True)

    def fullreplace(self):
        if self.currentDriver:
            pnputil.delete_driver(self.currentDriver,uninstall=True,force=True)
            pnputil.add_driver(self.path,install=True)
        
    
        




if __name__ == "__main__":
    f = infDriver(r'D:\Work\HP_Project\driverSwitcher\netwtw08.inf')
    f.replace()
    pass