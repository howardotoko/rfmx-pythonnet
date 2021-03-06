""" This example demonstrates how to apply a measurement delay to NI-DCPower to take
    hardware timed, single point measurements over active slots in bursty waveforms 
    like LTE/NR TDD.  This example showcases the use case where the marker event of
    the RF waveform is statically placed at sample 0 and can't be moved. """

import nidcpower

# variables
resource_name = "DC_01"
channels = ""

voltage_level = 5.0
current_limit = 1.0
voltage_level_range = 6.0
current_limit_range = 1.0
sample_rate = 100e3
measurement_interval = 2e-3 # measurement time in seconds
trigger_delay = 2.0e-3 # how long to wait after recieving a trigger to take a measurement

# initialize and configure sourcing parameters
dc = nidcpower.Session(resource_name,  channels, True)

dc.source_mode = nidcpower.SourceMode.SINGLE_POINT
dc.output_function = nidcpower.OutputFunction.DC_VOLTAGE

dc.voltage_level = voltage_level
dc.current_limit = current_limit
dc.voltage_level_range = voltage_level_range
dc.current_limit_range = current_limit_range

# start sourcing power - no measurements to be taken
dc.initiate() 
dc.wait_for_event(nidcpower.Event.SOURCE_COMPLETE)
dc.abort() # instrument continues to source power after this call

# configure measurement
dc.aperture_time_units = nidcpower.ApertureTimeUnits.SECONDS
dc.aperture_time = 1.0 / sample_rate
dc.commit()
record_length = int(measurement_interval / dc.aperture_time) # gets coerced number of samples
dc.measure_record_length_is_finite = True
dc.measure_record_length = record_length

# configure trigger
dc.source_trigger_type = nidcpower.TriggerType.DIGITAL_EDGE
dc.digital_edge_source_trigger_input_terminal = "PXI_Trig2"
dc.source_delay = trigger_delay # amount of time to wait before asserting the source complete event after the source trigger is received
dc.measure_when = nidcpower.MeasureWhen.AUTOMATICALLY_AFTER_SOURCE_COMPLETE

# measure
command = ""
while command.lower() != "exit":
    dc.initiate()
    voltage_current_measurements = dc.fetch_multiple(record_length, timeout=10.0)
    dc.abort()
    voltage_measurements = [measurement.voltage for measurement in voltage_current_measurements]
    current_measurements = [measurement.current for measurement in voltage_current_measurements]
    average_voltage = sum(voltage_measurements) / len(voltage_measurements)
    average_current = sum(current_measurements) / len(current_measurements)
    print("Average Voltage = " + "{:1.3f}".format(average_voltage) + 'V')
    print("Average Current = " + "{:1.3f}".format(average_current * 1000.0) + "mA")
    command = input("Press enter to take another measurement. Enter 'exit' to close.")

# close
dc.reset()
dc.close()