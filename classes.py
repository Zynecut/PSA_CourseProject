import pandas as pd
import numpy as np

class Line:
    def __init__(self, bus_p, bus_q, impedance, half_line_charging_admittance):
        self.bus_p = bus_p
        self.bus_q = bus_q
        self.impedance = impedance
        self.half_line_charging_admittance = half_line_charging_admittance

    def build_Line_pq(self) -> pd.DataFrame:
        y_pq = complex(1 / self.impedance)
        Line_pq = pd.DataFrame(np.empty((2, 2), dtype=complex), index=[self.bus_p, self.bus_q], columns=[self.bus_p, self.bus_q])
        Line_pq.loc[self.bus_p, self.bus_p] = complex(y_pq + self.half_line_charging_admittance)
        Line_pq.loc[self.bus_q, self.bus_q] = complex(y_pq + self.half_line_charging_admittance)
        Line_pq.loc[self.bus_p, self.bus_q] = complex(-y_pq)
        Line_pq.loc[self.bus_q, self.bus_p] = complex(-y_pq)
        return Line_pq



class Bus:
    def __init__(self, bus_id, voltage_magnitude, voltage_angle):
        self.bus_id = bus_id
        self.voltage_magnitude = voltage_magnitude
        self.voltage_angle = voltage_angle

    def __str__(self) -> str:
        return f"Bus ID: {self.bus_id}, Voltage Magnitude: {self.voltage_magnitude}, Voltage angle: {self.voltage_angle}"
    
    def update_voltage(self, new_voltage_magnitude, new_voltage_angle):
        self.voltage_magnitude = new_voltage_magnitude
        self.voltage_angle = new_voltage_angle


