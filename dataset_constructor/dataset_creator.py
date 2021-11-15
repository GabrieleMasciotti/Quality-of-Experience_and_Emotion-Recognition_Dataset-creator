from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showinfo
import os
import sys
import time
from datetime import datetime
import pandas as pd
import multiprocessing
import _thread
from threading import Event
from sensing_core.sensing.device.gsrplus import ShimmerGSRPlus

global stopShimmerSensor
stopShimmerSensor = Event()

global img
global howTo

def OpenFace_processFunction():
	os.system('/home/gabriele/OpenFace/build/bin/FeatureExtraction -device /dev/video0 -out_dir ./OpenFace_extracted_features -of extracted_features.csv -verbose')

def ShimmerSensor_processFunction():
	dt = pd.DataFrame()
	device = ShimmerGSRPlus()
	device.connect()
	for n, reads in device.stream():
		if stopShimmerSensor.is_set():
			break
		if n > 0:
			dt = dt.append(reads,ignore_index=True)
	print('Shimmer3GSR+Unit data extraction terminated. Producing csv output file...')
	dt.to_csv("Shimmer3GSR+Unit_extractedDatas")

def show_instructions():
	instr = Toplevel()
	instr.resizable(False,False)
	instr.wm_title("Instructions to proceed with data collection")
	instr.iconphoto(False, PhotoImage(file='./images/settings.png'))
	image_label = Label(instr,image=img)
	image_label.grid(row=0, column=0)
	l = Label(instr, text="These are some instructions to read before proceeding to collect data for the creation of the QoE and ER dataset.",font=('Ubuntu',12))
	l.grid(row=1, column=0)
	ll = Label(instr, text="Remember that this program is created for Ubuntu operating system.\n",font=('Ubuntu',12))
	ll.grid(row=2, column=0)
	l1 = Label(instr, text="--> OpenFace features extraction.\nInstall the OpenFace software carefully following the provided instructions, then adjust the features extractor path in the 21st line of the dataset_creator.py script.\nATTENTION: you have to use FeatureExtraction extractor. If you would like to use a different extractor (for example to extract features from more than a single face)\nthen change the name in the aforementioned path and in the 180th line to shutdown properly.\nThe program will record a video of your face using pc webcam, and will extract from it some features which you will find in the final dataset.\nFor this reason you should make sure you are using a device with a camera which is named /dev/video0 (the name used by the operating system).\nIf you have a camera with a different name, you can easily change the name inside the dataset_creator.py script in the 21st line.\nTo check available cameras type the following command on a shell: v4l2-ctl --list-devices\n",font=('Ubuntu',12))
	l1.grid(row=3, column=0)
	l2 = Label(instr, text="--> Bluetooth settings.\nIn order to collect datas from the Shimmer3 GSR+ Sensor you have to use a device with bluetooth. Turn on bluetooth and pair the Shimmer Sensor by typing the\ndefault code 1234.\nThen you will need to open a shell and look for the Sensor MAC address. To do so, type ' bluetoothctl ', and then ' paired-devices '.\nNow you should be able to see the Shimmer MAC. Copy it and press Ctrl-D to quit from bluetoothctl. Lastly, type ' sudo rfcomm bind 0 <the MAC you just copied> 1 '\nto complete Shimmer Sensor bluetooth connection configuration.\n",font=('Ubuntu',12))
	l2.grid(row=4, column=0)
	l3 = Label(instr, text="--> Wear the Shimmer3 GSR+ Sensor.\nYou should always wear the straps with the sensor ends facing down touching your fingers in the edge of the non-dominant hand palm, as shown in the picture below.",font=('Ubuntu',12))
	l3.grid(row=5, column=0)
	how_label = Label(instr,image=howTo)
	how_label.grid(row=6, column=0)
	l4 = Label(instr, text="\nNow with that, you are ready to start!\n",font=('Ubuntu',12))
	l4.grid(row=7, column=0)
	style = Style()
	style.configure('W.TButton', font = ('calibri', 12, 'bold'),foreground = 'green')
	b = Button(instr, text="Got it!", style = 'W.TButton', command=instr.destroy)
	b.grid(row=8, column=0)

class welcome(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        
        l = Label(self, text="Welcome to the QoE and ER dataset constructor.\n",font=('Ubuntu',13))
        l.pack()
        
        l2 = Label(self, text="Before proceeding please read the instructions shown in instruction menu.\n",font=('Ubuntu',13))
        l2.pack()
        
        l3 = Label(self, text="After carefully reading the instructions, click the start button to begin collecting data and construct your complete dataset!\n",font=('Ubuntu',13))
        l3.pack()
        
        l4 = Label(self, text='				')
        l4.pack(side=LEFT, fill=BOTH, expand=False)
        
        l5 = Label(self, text='				')
        l5.pack(side=RIGHT, fill=BOTH, expand=False)
        
        style = Style()
        style.configure('W.TButton', font = ('calibri', 12, 'bold'),foreground = 'green')
        self.button_start = Button(self, text="Start dataset creation", style = 'W.TButton', command=wel.destroy)
        self.button_start.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.button_instructions = Button(self, text="Instructions for the user", style = 'W.TButton', command=show_instructions)
        self.button_instructions.pack(side=RIGHT, fill=BOTH, expand=True)

class extraction(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        
        l = Label(self, text="Features collection request accepted. The program is now collecting datas from your face and from the sensor you are wearing.\n",font=('Ubuntu',13))
        l.pack()
        
        l2 = Label(self, text="Please keep an eye on the terminal to control if errors occur within the start of data extraction and\nensure to remain in the webcam frame continuing to wear the sensor correctly in order to get a great dataset.\n",font=('Ubuntu',13))
        l2.pack()
        
        l3 = Label(self, text="Press the button below to terminate the acquisition and produce the dataset.\n",font=('Ubuntu',13))
        l3.pack()
        
        style = Style()
        style.configure('W.TButton', font = ('calibri', 12, 'bold', 'underline'),foreground = 'red')
        self.button_terminate = Button(self, text="Terminate data acquisition", style = 'W.TButton', command=extr.destroy)
        self.button_terminate.pack()


class construction(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        
        l = Label(self, text="Dataset construction in progress. Please wait...\n",font=('Ubuntu',13))
        l.pack()
        
        l2 = Label(self, text="This may take several minutes depending on how long the just recorded video of your face is.\n",font=('Ubuntu',13))
        l2.pack()
        
        l3 = Label(self, text="Aborting the process by clicking the button below will terminate the program immediately producing a partially complete dataset.\n",font=('Ubuntu',13))
        l3.pack()
        
        style = Style()
        style.configure('W.TButton', font = ('calibri', 12, 'bold', 'underline'),foreground = 'red')
        self.button_abort = Button(self, text="Abort dataset construction", style = 'W.TButton', command=constr.destroy)
        self.button_abort.pack()
        

def close_program():
	print("Dataset creation aborted.")
	sys.exit()

wel = Tk()
wel.title('QoE and ER dataset constructor')
wel.resizable(False,False)
image = PhotoImage(file='./images/wel.png')
img = PhotoImage(file='./images/settings.png')
howTo = PhotoImage(file='./images/how_to_wear.png')
image_label = Label(wel,image=image)
image_label.pack()

wel.iconphoto(False, PhotoImage(file='./images/wel.png'))

app = welcome(wel)



wel.protocol("WM_DELETE_WINDOW", close_program)
wel.mainloop()

OpenFace_process = multiprocessing.Process(target=OpenFace_processFunction)	#process to execute OpenFace system command

extr = Tk()
extr.title('Features extraction in progress...')
extr.resizable(False,False)
image = PhotoImage(file='./images/recording.png')
image_label = Label(extr,image=image)
image_label.pack()

extr.iconphoto(False, PhotoImage(file='./images/recording.png'))

app = extraction(extr)

_thread.start_new_thread(ShimmerSensor_processFunction, ())		#starting ShimmerSensor connection and extraction

OpenFace_process.start()		#starting OpenFace software

globalTimeStamp = time.time()


os.system('ps')

extr.mainloop()

#THE USER ENDED DATA EXTRACTION

os.system('killall -2 FeatureExtraction')	#stopping OpenFace process

stopShimmerSensor.set()	#stopping ShimmerSensor data extraction

OpenFace_process.kill()
OpenFace_process.join()
OpenFace_process.close()

print('\n\n 	----------DATA COLLECTION TERMINATED!----------	')
print('\n\n ######## dataset construction in progress ######## \n\n')

features = pd.read_csv("./OpenFace_extracted_features/extracted_features.csv")
features = features.dropna()

#updating OpenFace timestamps
for i in range(features.shape[0]):
	features.at[i,'timestamp'] = features['timestamp'][i] + globalTimeStamp

features = features.set_index('frame')
features.to_csv('extracted_features_time.csv')


global constr
constr = Tk()
global stopConstruction
stopConstruction = Event()



def dataset_construction_function():
	features = pd.read_csv("extracted_features_time.csv")
	features['timestamp'] = features['timestamp'].astype(str)
	shimmer_datas = pd.read_csv("Shimmer3GSR+Unit_extractedDatas")

	#shimmer features file cleanup
	shimmer_datas['timestamp'] = shimmer_datas.timestamp.str.replace('[' , '',regex=True)
	shimmer_datas['timestamp'] = shimmer_datas.timestamp.str.replace(']' , '',regex=True)

	shimmer_datas['PPG'] = shimmer_datas.PPG.str.replace('[' , '',regex=True)
	shimmer_datas['PPG'] = shimmer_datas.PPG.str.replace(']' , '',regex=True)

	shimmer_datas['EDA'] = shimmer_datas.EDA.str.replace('[' , '',regex=True)
	shimmer_datas['EDA'] = shimmer_datas.EDA.str.replace(']' , '',regex=True)

	first_time_shimmer = shimmer_datas['timestamp'][0]

	#openface datas preparation for dataset creation
	epured_open = features[features['timestamp']>first_time_shimmer]
	epured_open = epured_open.reset_index()
	epured_open = epured_open.drop("index",axis=1)


	#synchronization of OpenFace features with Shimmer Sensor datas and construction of dataset
	
	aborted = False
	shimmer_index = -1
	open_face_index = -1
	selected = -1
	output_dataset = pd.DataFrame()

	for open_face_timestamp in epured_open['timestamp']:
		if stopConstruction.is_set():
			aborted = True
			break
		open_face_index = open_face_index + 1
		diff = 1000000
		diff_prec = 1000000000
		element_of_tuple = -1
		element_pos = -1
		tupla = False
		while diff<diff_prec:
			selected = shimmer_index
			if element_of_tuple != -1:
				tupla = True
				element_of_tuple = -1
			else:
	    			tupla = False
			shimmer_index = shimmer_index + 1
			diff_prec = diff
			first_time_shimmer = shimmer_datas['timestamp'][shimmer_index]
			try:
	    			first_time_shimmer = float(first_time_shimmer)
	    			diff = abs(float(open_face_timestamp) - first_time_shimmer)
			except ValueError:
	    			element_diff_prec = 1000000000
	    			for i in range((first_time_shimmer.count(','))+1):
	    				element_of_tuple = first_time_shimmer.rsplit(',')[i]
	    				element_of_tuple = float(element_of_tuple)
	    				element_diff = abs(float(open_face_timestamp) - element_of_tuple)
	    				if element_diff<element_diff_prec:
		        			element_pos = i
		        			diff = element_diff
		        			element_diff_prec = element_diff
		if not tupla:
			output_dataset = output_dataset.append(epured_open.loc[open_face_index,:].append(shimmer_datas.loc[selected,["PPG","EDA"]]),ignore_index=True)
		else:        
			d1 = pd.DataFrame()
			d1 = d1.append(epured_open.loc[open_face_index,:],ignore_index=True)
			dic = {}
			dic['PPG'] = float(shimmer_datas['PPG'][selected].rsplit(',')[element_pos])
			dic['EDA'] = float(shimmer_datas['EDA'][selected].rsplit(',')[element_pos])
			d2 = pd.DataFrame()
			d2 = d2.append(dic,ignore_index=True)
			d1 = pd.concat([d1,d2],axis=1)
			output_dataset = output_dataset.append(d1,ignore_index=True)
			
	output_dataset.to_csv('constructed_dataset_'+str(datetime.now()))
	if not aborted:
		constr.destroy()



constr.title('Dataset construction in progress...')
constr.resizable(False,False)
image = PhotoImage(file='./images/constructing.png')
image_label = Label(constr,image=image)
image_label.pack()

constr.iconphoto(False, PhotoImage(file='./images/constructing.png'))

app = construction(constr)

_thread.start_new_thread(dataset_construction_function, ())		#starting dataset creation thread

constr.mainloop()

stopConstruction.set()

time.sleep(1)

print("\n\n\nDataset construction terminated!")
















