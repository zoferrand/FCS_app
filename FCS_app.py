import webview
from webview import FileDialog

import numpy as np 
import math as m
import matplotlib
matplotlib.use('Agg')  # Utilise le backend 'Agg' pour le rendu sans affichage
import matplotlib.pyplot as plt
import czifile
from czifile import CziFile
import xml.etree.ElementTree as ET
import multipletau as mp
import sys
import os
from scipy.optimize import curve_fit
import matplotlib.colors as mcolors 
from scipy.interpolate import interp1d



def plot_detector_array(folder,name,intensities):

    x=np.array([0,m.sqrt(3),m.sqrt(3)/2,-m.sqrt(3)/2,-m.sqrt(3),-m.sqrt(3)/2,m.sqrt(3)/2,3*m.sqrt(3)/2,2*m.sqrt(3),3*m.sqrt(3)/2,m.sqrt(3),0,-m.sqrt(3),-3*m.sqrt(3)/2,-2*m.sqrt(3),-3*m.sqrt(3)/2,-m.sqrt(3),0,m.sqrt(3),2*m.sqrt(3),5*m.sqrt(3)/2,5*m.sqrt(3)/2,2*m.sqrt(3),m.sqrt(3)/2,-m.sqrt(3)/2,-2*m.sqrt(3),-5*m.sqrt(3)/2,-5*m.sqrt(3)/2,-2*m.sqrt(3),-m.sqrt(3)/2,m.sqrt(3)/2,3*m.sqrt(3)/2])
    y=np.array([0,0,-3/2,-3/2,0,3/2,3/2,3/2,0,-3/2,-3,-3,-3,-3/2,0,3/2,3,3,3,3,3/2,-3/2,-3,-9/2,-9/2,-3,-3/2,3/2,3,9/2,9/2,9/2])
    
    fig, ax = plt.subplots(1, 1, figsize=(10,10))

    shw = ax.hexbin(x, y, C=intensities, gridsize=(5,3), cmap="plasma")
    bar = plt.colorbar(shw,shrink=0.5,ax=ax)
    bar.set_label('Normalized intensity')
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_yticks([])
    ax.set_yticks([], minor=True)
    ax.axis('off')
    
    plt.savefig("%s/%s.png"%(folder,name),dpi=600)
    
    plt.close()
    plt.clf()

class Api:
    
    def __init__(self):
        self.main_window = None
        # self.analysis_window = None
        
        # self.analysis_wind_opened = False 
    
    def open_file_dialog(self):
        
        window = webview.windows[0]
        
        file_types = ('CZI Files (*.czi)', 'All files (*.*)')
        result = window.create_file_dialog(FileDialog.OPEN, file_types=file_types)
        
        if result:
            return result[0]
        return None

    def open_file(self, path):
        
        os.makedirs("Opening_file_window", exist_ok=True)
        
        self.opening_file_window = webview.create_window(" ", "Opening_file_window/opening_file_window.html", width=800, height=480)
        
        print(f"Python is processing file: {path}")
        
        self.get_metadata(path)
        
        img = czifile.imread(path)
        img = np.squeeze(img)
        img = img[:,0,:,:]
        img = np.reshape(img,(self.size_H,self.size_X*self.size_T))
        detector_intensities = np.nanmean(img,axis=1)
        plot_detector_array(folder="Opening_file_window",name='Detector_array',intensities=detector_intensities)

        self.size_T = self.size_X*self.size_T
        
        time_points = np.array([(i*self.pixel_time) for i in range(self.size_T)])

        root = ET.Element("root")
        ET.SubElement(root,"size_X").text = "%s"%(self.size_X)
        ET.SubElement(root,"size_T").text = "%s"%(self.size_T)
        ET.SubElement(root,"pixel_time").text = "%s"%(self.pixel_time)
        ET.SubElement(root,"gain").text = "%s"%(self.gain)
        ET.SubElement(root,"laser_power").text = "%s"%(self.laser_power)
        ET.SubElement(root,"bits").text = "%s"%(self.bits)
        ET.SubElement(root,"point_or_line").text = "%s"%(self.point_or_line)
        tree = ET.ElementTree(root)
        tree.write("Opening_file_window/metadata.xml")
        
        self.img_central_pix = img[0]
        self.img_first_ring = np.nanmean(img[:7],axis=0)
        self.img_second_ring = np.nanmean(img[:18],axis=0)
        self.img_whole = np.nanmean(img[:],axis=0)

        tot_int_pix_c = np.nanmean(self.img_central_pix,axis=0)
        tot_int_pix_f = np.nanmean(self.img_first_ring,axis=0)
        tot_int_pix_s = np.nanmean(self.img_second_ring,axis=0)
        tot_int_pix_w = np.nanmean(self.img_whole,axis=0)
        self.all_int = [tot_int_pix_c,tot_int_pix_f,tot_int_pix_s,tot_int_pix_w]
        
        plt.plot(time_points[::1000],self.img_whole[::1000],color='#e15984')
        plt.xlabel("Time (s)")
        plt.ylabel("Intensity")
        plt.savefig("Opening_file_window/Int_fluctuations.png",dpi=600)
        plt.close()
        plt.clf()
            
        del img
        
        self.opening_file_window.destroy()
        
        self.open_analysis_window()
        
    def get_metadata(self,path):

        print('Getting Metadata ...')

        with CziFile(path) as czi:
            metadata_xml = czi.metadata()

        root = ET.fromstring(metadata_xml)

        image_xml = root.find(".//Image")
        if image_xml is not None:
            size_X = image_xml.findtext("SizeX")
            size_T = image_xml.findtext("SizeT")
            size_H = image_xml.findtext("SizeH")

        image_xml = root.find(".//Channel")
        if image_xml is not None:
            pixel_time = image_xml.findtext("LaserScanInfo/PixelTime")
            gain = image_xml.findtext("DetectorSettings/Gain")
            
        image_xml = root.find(".//AcquisitionBlock")
        if image_xml is not None:
            bits = image_xml.findtext("AcquisitionModeSetup/BitsPerSample")
            
        image_xml = root.find(".//LightSourcesSettings")
        if image_xml is not None: 
            laser_power = image_xml.findtext("LightSourceSettings/Attenuation")

        image_xml = root.find(".//AcquisitionModeSetup")
        if image_xml is not None:
            point_or_line = image_xml.findtext("AcquisitionMode")

        self.size_X = int(size_X)
        self.size_T = int(size_T)
        self.size_H = int(size_H)
        self.pixel_time = float(pixel_time)
        self.gain = round(float(gain))
        self.bits = round(float(bits))
        self.laser_power = int((1-float(laser_power))*100)
        self.point_or_line = point_or_line

    def open_analysis_window(self):
        
        # if window_to_close=="main_window":
        #     window_to_close=main_window
        if self.main_window==None:
            self.main_window=main_window
        
        os.makedirs("Analysis_window", exist_ok=True)
        
        self.main_window.load_url("Analysis_window/FCS_app_analysis.html")
        
        # window_to_close.destroy()
        
        
        # self.analysis_window = webview.create_window("FCS app", "Analysis_window/FCS_app_analysis.html", width=window_to_close.width, height=window_to_close.height, resizable=True, js_api=self)
        
        # self.analysis_wind_opened = True
        
        
        
    def open_main_window(self):
        
        if self.main_window==None:
            self.main_window=main_window
            
        self.main_window.load_url("FCS_app.html")
        
        # if window_to_close=="analysis_window":
        #     window_to_close=self.analysis_window 
            
        # window_to_close.hide()
            
        # self.main_window = webview.create_window("FCS app", "FCS_app.html", width=window_to_close.width, height=window_to_close.height, resizable=True, js_api=self)
        
        
            
        


main_window = webview.create_window("FCS app", "FCS_app.html", width=1500, height=1200, resizable=True, js_api=Api())
webview.start(gui="qt", debug=False)