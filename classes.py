import pandas as pd
import numpy as np

class Line:
    def __init__(self, bus_p, bus_q, impedance, half_line_charging_admittance):
        self.bus_p = bus_p
        self.bus_q = bus_q
        self.impedance = impedance
        self.half_line_charging_admittance = half_line_charging_admittance


    def build_Line_Y_bus(self) -> pd.DataFrame:
        y_pq = complex(1 / self.impedance)
        # Line_pq = pd.DataFrame(np.empty((2, 2), dtype=complex), index=[self.bus_p, self.bus_q], columns=[self.bus_p, self.bus_q])
        # Line_pq.loc[self.bus_p, self.bus_p] = complex(y_pq + self.half_line_charging_admittance)
        # Line_pq.loc[self.bus_q, self.bus_q] = complex(y_pq + self.half_line_charging_admittance)
        # Line_pq.loc[self.bus_p, self.bus_q] = complex(-y_pq)
        # Line_pq.loc[self.bus_q, self.bus_p] = complex(-y_pq)
        Line_pq = {
                f'Y{self.bus_p}{self.bus_p}' : complex(y_pq + self.half_line_charging_admittance),
                f'Y{self.bus_p}{self.bus_q}' : complex(-y_pq),
                f'Y{self.bus_q}{self.bus_p}' : complex(-y_pq),
                f'Y{self.bus_q}{self.bus_q}' : complex(y_pq + self.half_line_charging_admittance)
                }
        return Line_pq

class Y_Bus:
    def __init__(self, line_adm):
        self.line_adm = line_adm

    def build_YBUS(self, num_buses) -> pd.DataFrame:
        # Initialize an empty Y-Bus matrix with zeros
        Y_bus = pd.DataFrame(0, index=range(1, num_buses + 1), columns=range(1, num_buses + 1), dtype=complex)





        for i in range(1, num_buses + 1):
            sum_of_admittances = 0
            for j in range(num_buses):
                key1 = f'Y{i}{i}'
                key2 = f'Y{i}{j+1}'
                key3 = f'Y{j+1}{i}'

        # Fill in the diagonal elements with sums of admittances going into that specific bus.
        # for i in range(1, num_buses + 1):
        #     Y_bus.loc[i, i] = sum(self.line_adm[j][f'Y{i}{i}'] for j in range(num_buses))

        # # Fill in the off-diagonal elements with negative admittances.
        # for i in range(1, num_buses + 1):
        #     for j in range(1, num_buses + 1):
        #         if i != j:
        #             Y_bus.loc[i, j] = -self.line_adm[i-1][f'Y{i}{j}']

        
        return Y_bus

        

class Bus:
    def __init__(self, bus_id, voltage_magnitude, voltage_angle, gen_MW, gen_MVAr, load_MW, load_MVAr):
        self.bus_id = bus_id
        self.voltage_magnitude = voltage_magnitude
        self.voltage_angle = voltage_angle
        self.gen_MW = gen_MW
        self.gen_MVAr = gen_MVAr
        self.load_MW = load_MW
        self.load_MVAr = load_MVAr
        self.power = gen_MW - load_MW


    def __str__(self) -> str:
        return f"Bus ID: {self.bus_id}, Voltage Magnitude: {self.voltage_magnitude}, Voltage angle: {self.voltage_angle}"
    
    def update_voltage(self, new_voltage_magnitude, new_voltage_angle):
        self.voltage_magnitude = new_voltage_magnitude
        self.voltage_angle = new_voltage_angle


