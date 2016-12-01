import socket
import argparse
import time
import datetime
from net_structure import Packet, decode


def packets_prepare(packet_size, file_name):
    f = open(file_name, 'r')
    source = f.read()
    source_len = len(source)
    packets = []
    source_pointer = 0
    packet_id = 0
    while source_pointer < source_len:
        packets.append(Packet('D', packet_id, source[source_pointer:source_pointer + packet_size]))
        source_pointer += packet_size
        packet_id += 1
    return packets


def trysend(sock, content, server, port):
    try:
        sock.sendto(content, (server, port))
    except OSError:
        pass


def client(server, server_port, window_size, timeout, packet_size, packets):
    start_time = time.time()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64 * 1024)
    sock.settimeout(timeout)
    total_packets = len(packets)
    next_packet = 0
    window = []

    prep = Packet('P', total_packets, [])
    prep_acked = False
    while not prep_acked:
        sock.sendto(prep.encode(), (server, server_port))
        try:
            data, addr = sock.recvfrom(packet_size)
            pa = decode(data)
            if pa.flag == 'A':
                prep_acked = True
        except socket.timeout:
            continue

    print('Server ACKed. Start sending KJV Bible with packet size: {0}B, window size: {1} and timeout: {2} seconds.'
          .format(packet_size, window_size, timeout))

    packets_sent = 0
    while next_packet < total_packets or (not len(window) == 0):
        while len(window) < window_size:
            if next_packet >= total_packets:
                break
            window.append(packets[next_packet])
            # sock.sendto(packets[next_packet].encode(), (server, server_port))
            trysend(sock, packets[next_packet].encode(), server, server_port)
            packets_sent += 1
            next_packet += 1
        try:
            data, addr = sock.recvfrom(4)
            cur_pack = decode(data)
            if cur_pack.flag == 'A':
                cur_elapsed = time.time() - start_time
                print('{0} / {1} packets ACKed. Average speed: {2} KB/s'
                      .format(cur_pack.pid + 1, total_packets,
                              ((cur_pack.pid + 1) * packet_size / 1024) / (float(cur_elapsed))), end='\r'),
                i = 0
                while i < len(window):
                    if cur_pack.pid >= window[i].pid:
                        del window[i]
                    else:
                        i += 1
        except socket.timeout:
            for i in range(len(window)):
                # sock.sendto(window[i].encode(), (server, server_port))
                trysend(sock, window[i].encode(), server, server_port)
                packets_sent += 1
            continue
    print()
    time_used = float(time.time() - start_time)
    print('Complete! Time used: {0} seconds.'.format(time_used))
    sock.close()
    return time_used, packets_sent - total_packets, packet_size*(packets_sent - total_packets)


if __name__ == '__main__':
    # - setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help='The address of the server')
    parser.add_argument('port', help='The port of the server')
    parser.add_argument('packet_size', help='The size of each packet')
    parser.add_argument('window_size', help='The size of send window')
    parser.add_argument('timeout', help='The timeout for sender')

    args = parser.parse_args()
    _timeout = float(args.timeout)
    _window = int(args.window_size)
    client(args.server, int(args.port), _window, _timeout, int(args.packet_size),
           packets_prepare(int(args.packet_size), 'kjv.txt'))
