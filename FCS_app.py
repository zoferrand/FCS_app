import webview
from webview import FileDialog
import shutil
import io, base64
import re

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


def on_main_closed():
    print("Main window closed. Exiting app...")
    os._exit(0)  # force exit (optional, ensures Python quits)

def plot_detector_array(folder,name,intensities):

    x=np.array([0,m.sqrt(3),m.sqrt(3)/2,-m.sqrt(3)/2,-m.sqrt(3),-m.sqrt(3)/2,m.sqrt(3)/2,3*m.sqrt(3)/2,2*m.sqrt(3),3*m.sqrt(3)/2,m.sqrt(3),0,-m.sqrt(3),-3*m.sqrt(3)/2,-2*m.sqrt(3),-3*m.sqrt(3)/2,-m.sqrt(3),0,m.sqrt(3),2*m.sqrt(3),5*m.sqrt(3)/2,5*m.sqrt(3)/2,2*m.sqrt(3),m.sqrt(3)/2,-m.sqrt(3)/2,-2*m.sqrt(3),-5*m.sqrt(3)/2,-5*m.sqrt(3)/2,-2*m.sqrt(3),-m.sqrt(3)/2,m.sqrt(3)/2,3*m.sqrt(3)/2])
    y=np.array([0,0,-3/2,-3/2,0,3/2,3/2,3/2,0,-3/2,-3,-3,-3,-3/2,0,3/2,3,3,3,3,3/2,-3/2,-3,-9/2,-9/2,-3,-3/2,3/2,3,9/2,9/2,9/2])
    
    fig, ax = plt.subplots(1, 1, figsize=(10,10))

    shw = ax.hexbin(x, y, C=intensities, gridsize=(5,3), cmap="plasma")
    bar = plt.colorbar(shw,shrink=0.5,ax=ax)
    bar.set_label('Normalized intensity')
    bar.ax.yaxis.label.set_size(22)
    bar.ax.tick_params(labelsize=18)
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
          
    def open_file_dialog(self):
        
        window = webview.windows[0]
        
        file_types = ('CZI Files (*.czi)', 'All files (*.*)')
        result = window.create_file_dialog(FileDialog.OPEN, file_types=file_types)
        
        if result:
            return result[0]
        return None

    def open_file(self, path):
        
        self.path = path
        self.exp_name = self.path.split('/')[-1].split('.')[0]
        
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
        
        self.time_points = np.array([(i*self.pixel_time) for i in range(self.size_T)])
        self.old_tp = self.time_points.copy()
        self.old_size_T = self.size_T

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
        self.old_img_w = self.img_whole.copy()

        tot_int_pix_c = np.nanmean(self.img_central_pix,axis=0)
        tot_int_pix_f = np.nanmean(self.img_first_ring,axis=0)
        tot_int_pix_s = np.nanmean(self.img_second_ring,axis=0)
        tot_int_pix_w = np.nanmean(self.img_whole,axis=0)
        self.all_int = [tot_int_pix_c,tot_int_pix_f,tot_int_pix_s,tot_int_pix_w]
        
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.plot(self.time_points[::1000], self.img_whole[::1000], color='#e15984')
        ax.set_xlabel("Time (s)",fontsize=14)
        ax.set_ylabel("Intensity",fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
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
        
        if self.main_window==None:
            self.main_window=main_window
        
        os.makedirs("Analysis_window", exist_ok=True)
        
        self.main_window.load_url("Analysis_window/FCS_app_analysis.html")
        
    def open_main_window(self):
        
        if self.main_window==None:
            self.main_window=main_window
            
        self.main_window.load_url("FCS_app.html")
        
    def open_zoom_plot_detector(self):
        
        os.makedirs("Analysis_window/Zoom_plot_detector", exist_ok=True)
        
        self.opening_plot_detector_window = webview.create_window(" ", "Analysis_window/Zoom_plot_detector/zoom_plot_detector.html", width=1200, height=1200, js_api=self)
     
    def get_tp_numb(self):
        
        return self.size_T
            
    def open_zoom_plot_rawdata(self):
        
        os.makedirs("Analysis_window/Zoom_plot_rawdata", exist_ok=True)
        
        with open("Analysis_window/Zoom_plot_rawdata/zoom_plot_rawdata.html","r") as f:
            html_text = f.read()
        # \s* takes into account any number of space
        # \d+ general term to recognise any number
        # \g<1> tells to keep the first element inside of the big paranthesis and to replace it with what comes after it
        html_text = re.sub(r'(<div class="text_total_tp" id="text_total_tp"><strong>Total time points:</strong>\s*)\d+',rf"\g<1>{self.size_T}",html_text)
        html_text = re.sub(r'(<strong>10</strong> seconds -> <strong>\s*)\d+(</strong> time points)',rf"\g<1>{round(10/self.pixel_time)}\g<2>",html_text)
        html_text = re.sub(r'(max=")\d+(")',rf"\g<1>{self.size_T}\g<2>",html_text)
        html_text = re.sub(r'(id="textbox_last_tp" value=")\d+(")',rf"\g<1>{self.size_T}\g<2>",html_text)
        
        with open("Analysis_window/Zoom_plot_rawdata/zoom_plot_rawdata.html","w") as w:
            w.write(html_text)
        
        self.opening_plot_rawdata_window = webview.create_window(" ", "Analysis_window/Zoom_plot_rawdata/zoom_plot_rawdata.html", width=1200, height=1200, js_api=self)
           
    def save_file(self,path,name):
        
        file_name = name.split('.')[0]
        file_extension = name.split('.')[1]
        
        file_types = ('All files (*.*)',)
        result = self.main_window.create_file_dialog(FileDialog.SAVE, file_types=file_types, save_filename='%s_%s.%s'%(file_name,self.exp_name,file_extension))
        if result:
            # result is a list with one element -> the chosen path
            destination = result[0]
            shutil.copy(path, destination)  # copy file to user-chosen location
        
            result.destroy()
        return destination
    
    def update_crop_values(self,first_crop,last_crop):
        
        first_crop = int(first_crop)
        last_crop = int(last_crop)
        
        fig, ax = plt.subplots(figsize=(9, 6))
     
        # Your plot
        ax.plot(self.old_tp[::1000], self.old_img_w[::1000], color='#e15984')
        ax.axvline(x=first_crop*self.pixel_time, color="#9a113c")
        ax.axvline(x=last_crop*self.pixel_time, color='#9a113c')
        ax.set_xlabel("Time (s)",fontsize=14)
        ax.set_ylabel("Intensity",fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)

        # Save to buffer instead of file
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=600)
        buf.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        
        # Return the string to JavaScript
        return img_base64
    
    def plot_cropped_data(self,first_crop,last_crop):
        
        first_crop = int(first_crop)
        last_crop = int(last_crop)
        
        self.time_points = self.time_points[first_crop:last_crop]
        self.img_whole = self.img_whole[first_crop:last_crop]
        
        fig, ax = plt.subplots(figsize=(9, 6))
     
        # Your plot
        ax.plot(self.time_points[::1000], self.img_whole[::1000], color='#e15984')
        ax.set_xlabel("Time (s)",fontsize=14)
        ax.set_ylabel("Intensity",fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        fig.savefig("Opening_file_window/Int_fluctuations.png", dpi=600)

        # Save to buffer instead of file
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=600)
        buf.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        
        # Return the string to JavaScript
        return img_base64
    
    def plot_uncut_data(self):
        
        fig, ax = plt.subplots(figsize=(9, 6))
     
        # Your plot
        ax.plot(self.old_tp[::1000], self.old_img_w[::1000], color='#e15984')
        ax.set_xlabel("Time (s)",fontsize=14)
        ax.set_ylabel("Intensity",fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        fig.savefig("Opening_file_window/Int_fluctuations.png", dpi=600)

        # Save to buffer instead of file
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=600)
        buf.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        
        # Return the string to JavaScript
        return img_base64
    
    def correlate_spot(self):
        print('Do not forget to delete self.old_tp and self.old_img_w !!!!!!!!')
    
        
main_window = webview.create_window("FCS app", "FCS_app.html", width=1500, height=1200, resizable=True, js_api=Api())
main_window.events.closed += on_main_closed
webview.start(gui="qt", debug=False)