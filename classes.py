class Bus:
    """
        This class defines the bus object with information that goes into each bus. 
    """
    def __init__(self, bus_id, voltage_magnitude, voltage_angle, P_gen, Q_gen, P_load, Q_load, BusType, Sbase):
        """
            Initialization of variables for each object.
            As there can be times when value in input data is '-', it is fixed to None here.
        """
        self.bus_id = int(bus_id)
        self.voltage_magnitude = float(voltage_magnitude)
        self.voltage_angle = float(voltage_angle)
        self.P_gen = float(P_gen)/Sbase if P_gen != '-' else None
        self.Q_gen = float(Q_gen)/Sbase if Q_gen != '-' else None
        self.P_load = float(P_load)/Sbase if P_load != '-' else None
        self.Q_load = float(Q_load)/Sbase if Q_load != '-' else None
        if self.P_gen is not None and self.P_load is not None:
            self.P_specified = self.P_gen - self.P_load
        else:
            self.P_specified = None
        if self.Q_gen is not None and self.Q_load is not None:
            self.Q_specified = self.Q_gen - self.Q_load
        else:
            self.Q_specified = None
        self.BusType = BusType


    def __str__(self) -> str:
        return f"Bus ID: {self.bus_id}, Voltage Magnitude: {self.voltage_magnitude}, Voltage angle: {self.voltage_angle}"
    

    def update_bus_voltage(self, new_voltage_magnitude=None, new_voltage_angle=None):
        """
            Updates bus voltages and/or bus angles.
        """
        if new_voltage_magnitude is not None:
            self.voltage_magnitude = new_voltage_magnitude
        if new_voltage_angle is not None:
            self.voltage_angle = new_voltage_angle

    def update_Pi_Qi(self, P_spec=None, Q_spec=None, P_gen=None, Q_gen=None):
        """
            Updates values if it is applied.
        """
        if P_spec is not None:
            self.P_specified = P_spec
        if Q_spec is not None:
            self.Q_specified = Q_spec
        if P_gen is not None:
            self.P_gen = P_gen
        if Q_gen is not None:
            self.Q_gen = Q_gen

    def typeSwitch(self, new_BusType):
        """
            Updates BusType if it is type switched.
        """
        self.BusType = new_BusType