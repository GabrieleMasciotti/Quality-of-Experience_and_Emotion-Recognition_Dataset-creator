from typing import Dict, Tuple

import pickle
import os
from serial.tools import list_ports

import sensing_core.sensing.device.shimmer_util as su
from sensing_core.sensing.device.shimmer import Shimmer3


class ShimmerGSRPlus:

    def __init__(self, sampling_rate=64) -> None:
        self._device = Shimmer3(shimmer_type=su.SHIMMER_GSRplus, debug=True)
        self.sampling_rate = sampling_rate
        
    def stream(self) -> Tuple[int, Dict]:
        if self._device.current_state == su.BT_CONNECTED:
            self._device.start_bt_streaming()
            print("Shimmer sensor data streaming started.")
        else:
            raise RuntimeError("Bluetooth is not connected.")
        while True:
            n, packets = self._device.read_data_packet_extended(calibrated=True)
            reads = {'timestamp': [], 'PPG': [], 'EDA': []}
            for pkt in packets:

                timestamp, ppg, eda = pkt[2], pkt[3], pkt[4]

                reads['timestamp'].append(timestamp)
                reads['PPG'].append(ppg)
                reads['EDA'].append(eda)

            yield n, reads
    
    def connect(self) -> bool:


	# [Gabriele Masciotti] LA SELEZIONE DELLA PORTA NON È STATA CONSIDERATA NELLO SCRIPT PER LA RACCOLTA DEI DATI SU UBUNTU (la porta è quella su cui è stato effettuato il bind durante il pairing con il sensore: /dev/rfcomm0)

        # Selection of the port
        #default_exists = os.path.exists('defaults/gsrplus_port.pkl')
        #if not default_exists:
         #   print("Vuoto!")
          #  available_ports = {}
           # print("Loading the available ports...")
            #for k, p in enumerate(list_ports.comports()):
             #   available_ports[str(k)] = p
              #  print(f"{k} - {p.device}")
            #index = input("Select the correct port for the Shimmer GSR+: ")
            #chosen_port = available_ports[index]
        #else:
         #   with open("defaults/gsrplus_port.pkl", 'rb') as f:
          #      chosen_port = pickle.load(f)

        #print(f"Selected {chosen_port.device}")
        
        # Starting connection with the chosen port
        #if self._device.connect(com_port=chosen_port.device):
        if self._device.connect("/dev/rfcomm0"):
            if not self._device.set_sampling_rate(self.sampling_rate):
                return False
            # After the connection we want to enable GSR and PPG
            if not self._device.set_enabled_sensors(su.SENSOR_GSR, su.SENSOR_INT_EXP_ADC_CH13):
                return False
            # Set the GSR measurement unit to Skin Conductance (micro Siemens)
            if not self._device.set_active_gsr_mu(su.GSR_SKIN_CONDUCTANCE):
                return False
            
            print(f"Shimmer GSR+ connected.")
            self._device.print_object_properties()

            #if not default_exists:
                #save_as_default = input("Do you want to save this port as default ([y]/n)? ") in ["", "y"]
                #if save_as_default:
                 #   with open("defaults/gsrplus_port.pkl", 'wb') as f:
                  #      pickle.dump(available_ports[index], f)
            return True
        else:
            return False
    
    def disconnect(self) -> bool:
        if not self._device.current_state == su.BT_CONNECTED:
            self._device.disconnect(reset_obj_to_init=True)
            return True
        else:
            return False
    
