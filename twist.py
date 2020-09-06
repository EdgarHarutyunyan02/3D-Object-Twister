from math import cos, sin, pi
import os


def get_layer_count(file):
    for line in file:
        if ';LAYER_COUNT:' in line:
            return int(line.split(':')[1])
    return None


def get_layer_height(file):
    for line in file:
        if ';Layer height:' in line:
            return float(line.split(':')[1])
    return None


def twist(gcode, start_layer=0, stop_layer=0, angle=0, axis=(0, 0)):
    # Positive angle - counter clockwise,
    # Negative angle - clockwise,

    layer_height = get_layer_height(gcode)
    layer_count = get_layer_count(gcode)
    if stop_layer == 0:
        stop_layer = layer_count-1

    new_gcode = list()
    if start_layer == stop_layer or gcode == None:
        return
    if start_layer > stop_layer:
        start_layer, stop_layer = stop_layer, start_layer
    rotation_step = angle / (stop_layer - start_layer)
    current_layer = 0
    for line in gcode:
        if ";LAYER:" in line:
            # Detected layer change
            current_layer = int(line.split(':')[1])

        if current_layer > stop_layer:
            rot_angle = angle
        elif current_layer >= start_layer:
            rot_angle = (current_layer-start_layer) * \
                rotation_step
        else:
            rot_angle = 0

        if line.startswith('G'):
            # G-code command
            command = line.split(' ')[0]

            line_parsed = line.split(' ')
            params = {}
            if line_parsed[0] in ["G0", "G1"]:
                # Movement command that is intended to be changed
                for block in line_parsed:
                    try:
                        if block[0] not in ["X", "Y"]:
                            raise
                        params[block[0]] = float(block[1:])
                    except:
                        params[block[0]] = block[1:]

                # Rotating X, Y coordinates. Z remains unchaned.
                if "X" in params and "Y" in params:
                    new_x = str((
                        cos(rot_angle*pi/180) * (params['X']-axis[0]) - sin(rot_angle*pi/180)*(params['Y']-axis[1]))+axis[0])
                    new_y = str((
                        sin(rot_angle * pi / 180) * (params['X']-axis[0]) + cos(rot_angle * pi / 180) * (params['Y']-axis[1]))+axis[1])
                    params["X"] = new_x
                    params["Y"] = new_y

                new_line = " ".join(
                    f"{key}{value}" for key, value in params.items())
                # new_line = f"{command} X{new_x} Y{new_y} {params['Z'] if 'Z' in params else ''}"
                new_gcode.append(new_line)
                continue
        new_line = line
        new_gcode.append(new_line)
    return '\n'.join(new_gcode)


file = None
while(file == None):
    file_name = input("Enter file name: ")
    if file_name:
        if file_name.split('.')[-1] != 'gcode':
            print("Unsupported file: Input .gcode files")
            continue
        try:
            with open(f'{file_name}') as file:
                file_content = file.read()
                id = file_content.find(';Layer height:')
                data = file_content.splitlines()

                start_layer = int(
                    input("Enter the start layer (Default: first layer) : ") or 0)
                stop_layer = int(
                    input("Enter the stop layer (Default: last layer): ") or 0)
                twist_angle = float(
                    input("Enter the twist angle in degree (Default: 0): ") or 0)
                axis_x = float(
                    input("Enter the X coordinate of axis (Default: 0): ") or 0)
                axis_y = float(
                    input("Enter the Y coordinate of axis (Default: 0): ") or 0)
                new_gcode = twist(data, start_layer, stop_layer,
                                  twist_angle, (axis_x, axis_y))
                new_file = open(
                    f'{file_name.split(".gcode")[0]}_new.gcode', 'w')
                new_file.write(new_gcode)
                new_file.close()
                print("Successfully twisted the object.")
        except FileNotFoundError:
            print("File Not Found")
