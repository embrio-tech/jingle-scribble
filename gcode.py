import warnings
from svg_to_gcode.compiler import interfaces
from svg_to_gcode.geometry import Vector


class CustomInterface(interfaces.Gcode):
    # Override the laser_off method such that it also powers off the fan.
    def laser_off(self):
        return "G0 Z0;"  # Turn off the fan + turn off the laser

    def set_laser_power(self, power):
        if power < 0 or power > 1:
            raise ValueError(f"{power} is out of bounds. Laser power must be given between 0 and 1. "
                             f"The interface will scale it correctly.")

        return "G0 Z0;" if power < 0.5 else "G0 Z5;"

    def linear_move(self, x=None, y=None, z=None):

        if self._next_speed is None:
            raise ValueError(
                "Undefined movement speed. Call set_movement_speed before executing movement commands.")

        # Don't do anything if linear move was called without passing a value.
        if x is None and y is None and z is None:
            warnings.warn("linear_move command invoked without arguments.")
            return ''

        # Todo, investigate G0 command and replace movement speeds with G1 (normal speed) and G0 (fast move)
        command = "G1" if self._next_speed > 0 else "G0"

        if self._current_speed != self._next_speed:
            self._current_speed = self._next_speed
            command += f" F{self._current_speed}" if self._current_speed > 0 else ''

        # Move if not 0 and not None
        command += f" X{x:.{self.precision}f}" if x is not None else ''
        command += f" Y{y:.{self.precision}f}" if y is not None else ''
        command += f" Z{z:.{self.precision}f}" if z is not None else ''

        if self.position is not None or (x is not None and y is not None):
            if x is None:
                x = self.position.x

            if y is None:
                y = self.position.y

            self.position = Vector(x, y)

        return command + ';'
