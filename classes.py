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
        self.voltage_magnitude = float(voltage_magnitude) if voltage_magnitude != '-' else float(1)
        self.voltage_angle = float(voltage_angle) if voltage_angle != '-' else float(0)
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

    def update_Pi_Qi(self, P_specified=None, Q_specified=None, P_gen=None, Q_gen=None):
        """
            Updates values if it is applied.
        """
        if P_specified is not None:
            self.P_specified = P_specified
        if Q_specified is not None:
            self.Q_specified = Q_specified
        if P_gen is not None:
            self.P_gen = P_gen
        if Q_gen is not None:
            self.Q_gen = Q_gen

    def typeSwitch(self, new_BusType):
        """
            Updates BusType if it is type switched.
        """
        self.BusType = new_BusType


class Line:
    def __init__(self, from_line, to_line, R_pu, X_pu, half_line_adm):
        self.from_line = int(from_line)
        self.to_line = int(to_line)
        self.R_pu = float(R_pu)
        self.X_pu = float(X_pu)
        self.half_line_adm = float(half_line_adm)
        self.P_loss = None
        self.Q_loss = None
        self.current = None


    def update(self, new_P_loss=None, new_Q_loss=None, new_current=None):
        if new_P_loss is not None:
            self.P_loss = new_P_loss
        if new_Q_loss is not None:
            self.Q_loss = new_Q_loss
        if new_current is not None:
            self.current = new_current
        