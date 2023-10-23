class Bus:
    def __init__(self, bus_id, voltage_magnitude, voltage_angle, P_specified, Q_specified):
        self.bus_id = bus_id
        self.voltage_magnitude = voltage_magnitude
        self.voltage_angle = voltage_angle
        self.P_specified = P_specified
        self.Q_specified = Q_specified

    def __str__(self) -> str:
        return f"Bus ID: {self.bus_id}, Voltage Magnitude: {self.voltage_magnitude}, Voltage angle: {self.voltage_angle}"
    
    # def update_voltage(self, new_voltage_magnitude, new_voltage_angle):
    #     self.voltage_magnitude = new_voltage_magnitude
    #     self.voltage_angle = new_voltage_angle

    def update_bus_voltage(self, new_voltage_magnitude=None, new_voltage_angle=None):
        if new_voltage_magnitude is not None:
            self.voltage_magnitude = new_voltage_magnitude
        if new_voltage_angle is not None:
            self.voltage_angle = new_voltage_angle


