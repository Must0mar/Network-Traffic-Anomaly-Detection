"""
This part is the back-end of the application, it is responsible for capturing and detecting the anomalies
in the network, the main tools and libraries that are used for this section of the application are:

-pyShark
-pandas
-sklearn 

The application first caputres a packet with pyShark, then it will use pandas to manupliate the raw data
into a useful piece of information tha can be inserted into the model for detection, some of the data that 
the model requires are behavioural information about the data, which can not be directly captured by pyshark
but should be caculated through some logic. 

"""
import pyshark
import time
import pandas as pd
import logging
from collections import defaultdict, deque
import hashlib
import json
from joblib import load
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import re

model = load('AnomalyDetectionModel.joblib')  

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

packet_rate = defaultdict(lambda: {'packet_count': 0, 'start_time': time.time(), 'end_time': time.time()})
failed_connections = defaultdict(lambda: {'syn_count': 0, 'syn_ack_count': 0})
port_diversity = defaultdict(set)
protocol_distribution = defaultdict(int)
time_window = 10  # seconds
connection_attempts = defaultdict(deque)

anomalies_count = 0
anomalies_by_type = defaultdict(int)
anomaly_ips_by_type = defaultdict(set)
anomalies_last_seen = {}

"""
The following methods are used to get the behavioural data from the packets.

"""

"""
The following method is used to caputre the packet rate of each source ip address

"""
def update_packet_rate(src_ip, current_time):
    packet_rate[src_ip]['packet_count'] += 1
    packet_rate[src_ip]['end_time'] = current_time
    duration = packet_rate[src_ip]['end_time'] - packet_rate[src_ip]['start_time']
    return packet_rate[src_ip]['packet_count'] / duration if duration > 0 else 0

"""
The following method is used to caputre the Synchronize and Acknowledge ratio for each source ip address 

"""
def update_syn_ack_ratio(src_ip, tcp_flags):
    if isinstance(tcp_flags, str) and 'SYN' in tcp_flags and 'ACK' not in tcp_flags:
        failed_connections[src_ip]['syn_count'] += 1
    if isinstance(tcp_flags, str) and 'SYN-ACK' in tcp_flags:
        failed_connections[src_ip]['syn_ack_count'] += 1
    syn_count = failed_connections[src_ip]['syn_count']
    syn_ack_count = failed_connections[src_ip]['syn_ack_count']
    return syn_ack_count / syn_count if syn_count > 0 else 0


"""
The following method is used to caputre the diversity of port of each source ip address

"""
def update_port_diversity_func(src_ip, dst_port):
    port_diversity[src_ip].add(dst_port)
    return len(port_diversity[src_ip])


"""
The following method is used to caputre the number of instaces of each protocol.

"""
def update_protocol_distribution_func(proto):
    if proto == 1:
        protocol_distribution['TCP'] += 1
    elif proto == 2:
        protocol_distribution['UDP'] += 1
    else:
        protocol_distribution['Other'] += 1


"""
The following method is used to caputre unsuccessful connections for each source ip address. 

"""
def update_unsuccessful_connections(src_ip, tcp_flags):
    if isinstance(tcp_flags, str) and 'SYN' in tcp_flags and 'ACK' not in tcp_flags:
        failed_connections[src_ip]['syn_count'] += 1
    if isinstance(tcp_flags, str) and 'SYN-ACK' in tcp_flags:
        failed_connections[src_ip]['syn_ack_count'] += 1
    syn_count = failed_connections[src_ip]['syn_count']
    syn_ack_count = failed_connections[src_ip]['syn_ack_count']
    failed = syn_count - syn_ack_count
    return failed / syn_count if syn_count > 0 else 0



def checkAnomaly(data):
    input_df = pd.DataFrame([data])
    for col in ['Source IP', 'Destination IP']:
        if col in input_df.columns:
            input_df = input_df.drop(columns=[col])

    categorical_columns = input_df.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        le = LabelEncoder()
        input_df[col] = le.fit_transform(input_df[col])

    predicted_output = model.predict(input_df)[0]
    return predicted_output



def save_json(counter):


    anomaly_ips_dict = {str(k): [str(ip) for ip in v] for k, v in anomaly_ips_by_type.items()}
    anomalies_last_seen_str = {str(k): datetime.fromtimestamp(ts).isoformat() for k, ts in anomalies_last_seen.items()}

    anomalies_by_type_dict = {str(k): int(v) for k, v in anomalies_by_type.items()}

    protocol_dist_dict = {str(k): int(v) for k, v in protocol_distribution.items()}

    final_data = {
        "total_packets": int(counter),
        "total_anomalies": int(anomalies_count),
        "anomalies_by_type": anomalies_by_type_dict,
        "anomaly_ips": anomaly_ips_dict,
        "protocol_distribution": protocol_dist_dict,
        "anomalies_last_seen": anomalies_last_seen_str
    }

    json_filename = "network_traffic_summary.json"
    with open(json_filename, 'w') as f:
        json.dump(final_data, f, indent=4)
def extract_and_save_json(text, output_filename):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in the input text.")
    
    json_content = match.group(0).strip()

    data = json.loads(json_content)

    formatted_data = {
        "en": data["en"],
        "ku": data["ku"],
        "ar": data["ar"]
    }

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)



"""
This is the main method that will intiate every thing, the duration variable is to set the duration of each session, 
and the interface should be changed to the internet interface of the device
"""
def capture(interface="Wi-Fi", duration=3000):
    print("Running...")
    capture = pyshark.LiveCapture(interface=interface)
    sessions = {}
    start_time = time.time()
    logging.basicConfig(level=logging.ERROR, filename='packet_errors.log')
    counter = 0

    global anomalies_count, anomalies_by_type, anomaly_ips_by_type, anomalies_last_seen

    try:
        for packet in capture:
            current_time = time.time()
            if current_time - start_time > duration:
                print("Duration reached, breaking...")
                break

            counter += 1
            try:
                unsuccessful_conn = 0
                src_ip = dst_ip = flags = tcp_flags = ''
                ttl = src_port = dst_port = 0
                checksum = ''
                protocol = 0
                total_length = 0
                payload_size = 0

                if hasattr(packet, 'ip'):
                    ip_layer = packet.ip
                    src_ip = getattr(ip_layer, 'src', '0.0.0.0')
                    dst_ip = getattr(ip_layer, 'dst', '0.0.0.0')
                    total_length = safe_int(getattr(ip_layer, 'len', 0))
                    flags = getattr(ip_layer, 'flags', '')
                    ttl = safe_int(getattr(ip_layer, 'ttl', 0))
                    checksum = getattr(ip_layer, 'checksum', '')

                proto_str = str(getattr(packet, 'transport_layer', 'Unknown'))
                if proto_str == "TCP":
                    protocol = 1
                    tcp_flags = str(getattr(packet.tcp, 'flags', ''))
                    tcp_header_len = safe_int(getattr(packet.tcp, 'hdr_len', 0))
                    src_port = safe_int(getattr(packet.tcp, 'srcport', 0))
                    dst_port = safe_int(getattr(packet.tcp, 'dstport', 0))
                    payload_size = total_length - tcp_header_len
                    unsuccessful_conn = update_unsuccessful_connections(src_ip, tcp_flags)
                elif proto_str == "UDP":
                    protocol = 2
                    src_port = safe_int(getattr(packet.udp, 'srcport', 0))
                    dst_port = safe_int(getattr(packet.udp, 'dstport', 0))
                    if hasattr(packet.udp, 'payload'):
                        payload_size = len(packet.udp.payload.binary_value)
                else:
                    protocol = 0

                session_key = (src_ip, dst_ip, src_port, dst_port, protocol)
                if session_key not in sessions:
                    sessions[session_key] = {'start_time': current_time, 'packet_count': 0, 'byte_count': 0}
                sessions[session_key]['packet_count'] += 1
                sessions[session_key]['byte_count'] += total_length

                session_id = int(hashlib.sha256(f"{src_ip}-{dst_ip}-{src_port}-{dst_port}-{protocol}".encode()).hexdigest(), 16) % (10**8)

                rate = update_packet_rate(src_ip, current_time)
                syn_ack_ratio = update_syn_ack_ratio(src_ip, tcp_flags)
                port_div = update_port_diversity_func(src_ip, dst_port)
                update_protocol_distribution_func(protocol)

                packet_info = {
                    "Session ID": session_id,
                    "Source IP": src_ip,
                    "Destination IP": dst_ip,
                    "Source Port": src_port,
                    "Destination Port": dst_port,
                    "Protocol": protocol,
                    "Total Length": total_length,
                    "TTL": ttl,
                    "Checksum": checksum,
                    "Flags": flags,
                    "TCP Flags": tcp_flags,
                    "Payload Size": payload_size,
                    "Packet Rate": rate,
                    "SYN-ACK Ratio": syn_ack_ratio,
                    "Port Diversity": port_div,
                    "Retransmissions": 0,
                    "Unsuccessful Connections": unsuccessful_conn,
                    "Number of Packets": sessions[session_key]['packet_count'],
                    "Byte Count": sessions[session_key]['byte_count'],
                }

                anomaly = checkAnomaly(packet_info)
                if anomaly>0:
                    anomalies_count += 1
                    anomalies_by_type[anomaly] += 1
                    anomaly_ips_by_type[anomaly].add(src_ip)
                    anomalies_last_seen[anomaly] = current_time

                print("Anomaly Status",anomaly,"  Source IP Address:", src_ip, " Checksum:", checksum)
                save_json(counter)

            except Exception as e:
                logging.error(f"Error processing packet: {e}")
                continue

    except EOFError:
        print("No more packets or capture ended.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        capture.close()
        print("Capture closed.")
        save_json(counter)

capture()
