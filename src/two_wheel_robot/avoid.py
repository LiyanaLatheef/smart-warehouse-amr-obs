import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import serial
import time

class PhysicalAMR(Node):
    def __init__(self):
        super().__init__('physical_robot_avoidance')
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        # Settings from your Gazebo code
        self.safe_distance = 0.6  # Distance to trigger a turn
        
        # Open Serial to Arduino Mega
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
            time.sleep(2) 
            self.get_logger().info('--- PHYSICAL AMR READY ---')
        except Exception as e:
            self.get_logger().error(f'Serial Error: {e}')
            exit()

        self.last_action = None

    def scan_callback(self, msg):
        ranges = msg.ranges
        total = len(ranges)

        # 1. Split scan into 3 zones (matching your Gazebo logic)
        # We add a 0.2m filter to ignore the robot's own chassis
        def get_min_dist(data):
            valid = [r for r in data if 0.2 < r < 8.0]
            return min(valid) if valid else float('inf')

        front = get_min_dist(ranges[int(total*0.42): int(total*0.58)])
        left  = get_min_dist(ranges[int(total*0.58): int(total*0.75)])
        right = get_min_dist(ranges[int(total*0.25): int(total*0.42)])

        # 2. Advanced Avoidance Logic
        if front < self.safe_distance:
            # Path blocked! Decide which way to turn
            if left > right:
                current_action = 'L' # Turn Left (more space there)
            else:
                current_action = 'R' # Turn Right
        else:
            # All clear
            current_action = 'F'

        # 3. Send to Arduino
        if current_action != self.last_action:
            self.ser.write(current_action.encode())
            self.get_logger().info(f'FRONT: {front:.2f}m | ACTION: {current_action}')
            self.last_action = current_action

def main(args=None):
    rclpy.init(args=args)
    node = PhysicalAMR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Stopping...')
    finally:
        if hasattr(node, 'ser'):
            node.ser.write(b'S') # Emergency Stop
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
