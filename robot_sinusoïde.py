import pypot.dynamixel

ports = pypot.dynamixel.get_available_ports()

if not ports:
    raise IOError('no port found!')

print('ports found', ports)

print('connecting on the first available port:', ports[0])
dxl_io = pypot.dynamixel.DxlIO(ports[0])
This should open a connection through a virtual communication port to your device.

Warning

It is important to note that it will open a connection using a default baud rate. By default your motors are set up to work on the robotis default baud rate (57140) while pypot is set up to work with a 1000000 baud rate. To communicate with your motors, you must ensure that this baud rate is the same baud rate that the motors are configure to use. So, you will need to change either the configuration of your motors (see Herborist section) or change the default baud rate of your connection.

To set up a connection with another baud rate you can write:

dxl_io = pypot.dynamixel.DxlIO(port, baudrate=57600)
The communication can be closed using the close() method.

Note

The class DxlIO can also be used as a Context Manager (the close() method will automatically be called at the end). For instance:

with pypot.dynamixel.DxlIO('/dev/ttyUSB0') as dxl_io:
    ...
Finding motors
Pypot has been designed to work specifically with the Robotis range of motors. These motors use two different protocols to communicate: TTL (3 wire bus) and RS485 (4 wire Bus). The motors can be daisy chained together with other types of motors on the same bus as long as the bus communicates using the same protocol. This means that MX-28 and AX-12 can communicate on the same bus, but cannot be connected to a RX-28.

All motors work sufficiently well with a 12V supply. Some motors can use more than 12V but you must be careful not to connect an 18V supply on a bus that contains motors that can only use 12V! Connect this 12V SMPS supply (switch mode power supply) to a Robotis SMPS2Dynamixel device which regulates the voltage coming from the SMPS. Connect your controller device and a single motor to this SMPS2Dynamixel.

Open your python terminal and create your DxlIO as described in the above section Opening/Closing a communication port.

To detect the motors and find their id you can scan the bus. To avoid spending a long time searching all possible values, you can add a list of values to test:

dxl_io.scan()
>>> [4, 23, 24, 25]

dxl_io.scan([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
>>> [4]
Or, you can use the shorthand:

dxl_io.scan(range(10))
>>> [4]
This should produce a list of the ids of the motors that are connected to the bus. Each motor on the bus must have a unique id. This means that unless your motors have been configured in advance, it is better to connect them one by one to ensure they all have unique ids first.

Note

You also can modify the timeout to speed up the scanning. Be careful though, as this could result in loosing messages.

Low-level control
Now we have the id of the motors connected, we can begin to access their functions by using their id. Try to find out the present position (in degrees) of the motor by typing the following:

dxl_io.get_present_position((4, ))
>>> (67.8, )
You can also write a goal position (in degrees) to the motor using the following:

dxl_io.set_goal_position({4: 0})
The motors are handled in degrees where 0 is considered the central point of the motor turn. For the MX motors, the end points are -180° and 180°. For the AX and RX motors, these end points are -150° to 150°.

Warning

As you can see on the example above, you should always pass the id parameter as a list. This is intended as getting a value from several motors takes the same time as getting a value from a single motor (thanks to the SYNC_READ instruction). Similarly, we use dictionary with pairs of (id, value) to set value to a specific register of motors and benefit from the SYNC_WRITE instruction.

As an example of what you can do with the low-level API, we are going to apply a sinusoid on two motors (make sure that the motion will not damage your robot before running the example!). Here is a complete listing of the code needed:

import itertools
import numpy
import time

import pypot.dynamixel

AMP = 30
FREQ = 0.5

if __name__ == '__main__':
    ports = pypot.dynamixel.get_available_ports()
    print('available ports:', ports)

    if not ports:
        raise IOError('No port available.')

    port = ports[0]
    print('Using the first on the list', port)

    dxl_io = pypot.dynamixel.DxlIO(port)
    print('Connected!')

    found_ids = dxl_io.scan()
    print('Found ids:', found_ids)

    if len(found_ids) < 2:
        raise IOError('You should connect at least two motors on the bus for this test.')

    ids = found_ids[:2]

    dxl_io.enable_torque(ids)

    speed = dict(zip(ids, itertools.repeat(200)))
    dxl_io.set_moving_speed(speed)
    pos = dict(zip(ids, itertools.repeat(0)))
    dxl_io.set_goal_position(pos)


    t0 = time.time()
    while True:
        t = time.time()
        if (t - t0) > 5:
            break

        pos = AMP * numpy.sin(2 * numpy.pi * FREQ * t)
        dxl_io.set_goal_position(dict(zip(ids, itertools.repeat(pos))))

        time.sleep(0.02)
