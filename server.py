import socket
import argparse
from net_structure import Packet, decode


def server(port, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64*1024)
    sock.settimeout(10)  # if more than 20 seconds without any message get in, restart

    total_packets = -1

    while True:
        try:
            while True:
                pdata, paddr = sock.recvfrom(packet_size)
                prep = decode(pdata)
                if not prep.flag == 'P':
                    if total_packets > 0:
                        ppla = Packet('A', total_packets - 1, [])
                        sock.sendto(ppla.encode(), paddr)
                else:
                    pa = Packet('A', prep.pid, [])
                    sock.sendto(pa.encode(), paddr)
                    total_packets = pa.pid
                    break
            front = -1
            data_book = ''
            print('Start to receive packets.')

            while front < total_packets - 1:
                data, addr = sock.recvfrom(packet_size + 4)
                cur_pack = decode(data)
                if cur_pack.flag == 'D':
                    if cur_pack.pid == front + 1:
                        front += 1
                        data_book += cur_pack.data.decode('ascii')
                        print('{0} / {1} packets received.'.format(cur_pack.pid + 1, total_packets), end='\r'),
                    if front >= 0:
                        ack = Packet('A', front, [])
                        sock.sendto(ack.encode(), addr)
                elif cur_pack.flag == 'P':
                    sock.sendto(pa.encode(), paddr)

            print()
            print('Complete!')
            f = open('data.txt', 'w')
            f.write(data_book)
        except socket.timeout:
            print("Timed out. Maybe connection failed.")
            continue


if __name__ == '__main__':
    # - setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help='The port of the server')
    parser.add_argument('packet_size', help='The size of each packet')

    args = parser.parse_args()
    server(int(args.port), int(args.packet_size))
