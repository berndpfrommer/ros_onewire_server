#!/usr/bin/env python
#
# 2018 Bernd Pfrommer
#
# ROS node that publishes owserver sensor data
#

import rospy
import diagnostic_updater
import argparse
import numpy as np
import subprocess
import std_msgs.msg
import sensor_msgs.msg
from sensor_msgs.msg import Temperature
from sensor_msgs.msg import RelativeHumidity


class Field():
    def __init__(self, hwid, name, f, ftol, updater):
        T = 1/f # period
        w = 10  # window size (number of observations)
        freq = diagnostic_updater.FrequencyStatusParam({'min':f, 'max':f}, ftol, window_size = w)
        stamp = diagnostic_updater.TimeStampStatusParam(-3*T, 3*T)
        self.hwid = hwid
        self.name = name
        self.topic = "environmental/" + hwid.replace('.', '_') + "/" + name
        self.diagnostic = diagnostic_updater.TopicDiagnostic(self.topic, updater, freq, stamp)
    def pub(self, msg, frameid):
        msg.header      = std_msgs.msg.Header()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = frameid
        msg.variance = 0
        self.publisher.publish(msg)
        self.diagnostic.tick(msg.header.stamp)
        
        
class TemperatureField(Field):
    def __init__(self, hwid, name, f, ftol, updater):
        Field.__init__(self, hwid, name, f, ftol, updater)
        self.publisher = rospy.Publisher(self.topic, Temperature, queue_size=1)
    def publish(self, info, frameid):
        msg = sensor_msgs.msg.Temperature()
        try:
            msg.temperature = float(info)
        except ValueError:
            rospy.logwarn('got bad temperature!')
            msg.temperature = 0
        self.pub(msg, frameid)
        rospy.loginfo('sensor %16s: %-11s = %7.3fC' % (self.hwid, self.name, msg.temperature))


class RelativeHumidityField(Field):
    def __init__(self, hwid, name, f, ftol, updater):
        Field.__init__(self, hwid, name, f, ftol, updater)
        self.publisher = rospy.Publisher(self.topic, RelativeHumidity, queue_size=1)
    def publish(self, info, frameid):
        msg = sensor_msgs.msg.RelativeHumidity()
        try:
            msg.relative_humidity = float(info)
        except  ValueError:
            msg.relative_humidity = 0
        self.pub(msg, frameid)
        rospy.loginfo('sensor %16s: %-11s = %7.3f%%' % (self.hwid, self.name, msg.relative_humidity))
        
class Sensor():
    def __init__(self, hwid, fields, freq, freq_tol, updater):
        self.hwid = hwid
        self.fields = []
        for f in fields:
            if f == 'humidity':
                self.fields.append(RelativeHumidityField(hwid, f, freq, freq_tol, updater))
            elif f == 'temperature':
                self.fields.append(TemperatureField(hwid, f, freq, freq_tol, updater))
            else:
                raise Exception('bad field name: ' + str(f))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='read sensor data from one-wire server')
    args = parser.parse_args(rospy.myargv()[1:])

    rospy.init_node('onewire_sensor')
    updater  = diagnostic_updater.Updater()
    updater.setHardwareID("none")

    
    freq     = rospy.get_param('~frequency', 1/10.0)
    freq_tol = rospy.get_param('~frequency_tolerance', 0.5)
    frame_id = rospy.get_param('~frame_id', '')
    ss       = rospy.get_param('~sensors')
    sensors  = [Sensor(s['address'],s['fields'], freq, freq_tol, updater) for s in ss]
        
    rospy.loginfo('frequency: %.2f, tolerance: %.3f, frame_id: %s' %(freq, freq_tol, frame_id))
    updater.force_update()
    rate = rospy.Rate(freq)
    while not rospy.is_shutdown():
        for s in sensors:
            for f in s.fields:
                ow_topic = "/" + s.hwid + "/" + f.name
                process = subprocess.Popen(["owread", ow_topic],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                info, err = process.communicate() # returns when process complete
                if err:
                    print "ERROR: %s(%s) while running owread for %s" % (err, info, ow_topic)
                else:
                    f.publish(info, frame_id)
        updater.update()
        rate.sleep()
