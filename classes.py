import pandas as pd
import numpy as np

class Line:
    def __init__(self, bus_p, bus_q, impedance, half_line_charging_admittance, real_power_line_limit):
        self.bus_p = bus_p
        self.bus_q = bus_q
        self.impedance = impedance
        self.half_line_charging_admittance = half_line_charging_admittance
        self.real_power_line_limit = real_power_line_limit


    def build_Line_Y_bus(self) -> pd.DataFrame:
        y_pq = complex(1 / self.impedance)
        Line_pq = {
                f'Y{self.bus_p}{self.bus_p}' : complex(y_pq + self.half_line_charging_admittance),
                f'Y{self.bus_p}{self.bus_q}' : complex(-y_pq),
                f'Y{self.bus_q}{self.bus_p}' : complex(-y_pq),
                f'Y{self.bus_q}{self.bus_q}' : complex(y_pq + self.half_line_charging_admittance),
                'From Bus: ' : self.bus_p,
                'To Bus: ' : self.bus_q
                }
        return Line_pq
    
    def line_P_Limit(self) -> list:
        limit = {
            'Line' : f"{self.bus_p} - {self.bus_q}",
            'Real Power Line Limit' : self.real_power_line_limit
        }
        return limit

class Y_Bus:
    def __init__(self, line_adm):
        self.line_adm = line_adm

    def build_YBUS(self, num_buses) -> pd.DataFrame:
        '''
            This function will build a YBus for any N-Bus system, taking into account the number of lines going into each bus.
        '''
        # Initialize an empty Y-Bus matrix with zeros
        Y_bus = pd.DataFrame(0, index=range(1, num_buses + 1), columns=range(1, num_buses + 1), dtype=complex)

        for i in range(1, num_buses + 1):
            for j in range(1, num_buses + 1):
                # Initialize the sum of admittances for the diagonal element (Yii)
                sum_of_admittances = 0
                if i == j:
                    # Calculate the sum of admittances for the diagonal element
                    for k in range(len(self.line_adm)):
                        if self.line_adm[k]['From Bus: '] == i or self.line_adm[k]['To Bus: '] == i:
                            key = f'Y{i}{i}'
                            if key in self.line_adm[k]:
                                sum_of_admittances += self.line_adm[k][key]
                    # Set the diagonal element
                    Y_bus.loc[i, i] = complex(sum_of_admittances)
                else:
                    # Calculate the off-diagonal elements (Yij) if i != j
                    key = f'Y{i}{j}'
                    for k in range(len(self.line_adm)):
                        if key in self.line_adm[k]:
                            Y_bus.loc[i, j] = self.line_adm[k][key]
        return Y_bus



class Bus:
    def __init__(self, bus_id, voltage_magnitude, voltage_angle, realP, reaqQ):
        self.bus_id = bus_id
        self.voltage_magnitude = voltage_magnitude
        self.voltage_angle = voltage_angle
        self.P = realP
        self.Q = reaqQ


    def __str__(self) -> str:
        return f"Bus ID: {self.bus_id}, Voltage Magnitude: {self.voltage_magnitude}, Voltage angle: {self.voltage_angle}"

    def buses(self):
        # voltage, angle, Pi, Qi
        bus = {
            'Bus ID' : self.bus_id,
            f'P_{self.bus_id}' : self.P,
            f'Q_{self.bus_id}' : self.Q,
            f'v_{self.bus_id}' : self.voltage_magnitude,
            f'delta_{self.bus_id}' : self.voltage_angle
        }
        return bus
    
    def update_voltage(self, new_voltage_magnitude, new_voltage_angle):
        self.voltage_magnitude = new_voltage_magnitude
        self.voltage_angle = new_voltage_angle

    def PV_and_PQ_buses():

        pass


