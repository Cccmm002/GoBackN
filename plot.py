import argparse
import client
import csv
import numpy as np
#import matplotlib.pyplot as plt


def _search_run(server, port, window, timeout, packet_size, packets, _timeout_, cur):
    if _timeout_:
        t = client.client(server, port, window, cur, packet_size, packets)[0]
    else:
        t = client.client(server, port, int(cur), timeout, packet_size, packets)[0]
    return t


def search_timeout(left, right, cur, server, port, window, packet_size, timeout, packets):
    prev = _search_run(server, port, window, timeout, packet_size, packets, True, cur)
    while cur > 0:
        l = (left + cur)/2
        tl = _search_run(server, port, window, timeout, packet_size, packets, True, l)
        if tl < prev:
            prev = tl
            right = cur
            cur = l
        else:
            if right < 0:
                r = cur*2
            else:
                r = (cur + right)/2
            rl = _search_run(server, port, window, timeout, packet_size, packets, True, r)
            if rl < prev:
                prev = rl
                left = cur
                cur = r
            else:
                return cur


def search_window(left, right, cur, server, port, window, packet_size, timeout, packets):
    prev = _search_run(server, port, window, timeout, packet_size, packets, False, cur)
    while cur > 0:
        if right < 0:
            r = cur*2
        else:
            r = (cur + right)/2
        rl = _search_run(server, port, window, timeout, packet_size, packets, False, r)
        if rl < prev:
            prev = rl
            left = cur
            cur = r
        else:
            l = (left + cur) / 2
            tl = _search_run(server, port, window, timeout, packet_size, packets, False, l)
            if tl < prev:
                prev = tl
                right = cur
                cur = l
            else:
                return cur


if __name__ == '__main__':
    # - setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help='The address of the server')
    parser.add_argument('port', help='The port of the server')
    parser.add_argument('packet_size', help='The size of each packet')
    parser.add_argument('file', help='The file to transmit')

    args = parser.parse_args()
    _server = args.server
    _port = int(args.port)
    _packet_size = int(args.packet_size)
    _file = args.file

    _packets = client.packets_prepare(_packet_size, _file)
    _packet_len = len(_packets)

    # print('Searching for the best timeout and window size.')
    # _timeout = search_timeout(0.0, -1, 0.5, _server, _port, 64, _packet_size, 0.1, _packets)
    # print('Best timeout is found! It is {0} seconds.'.format(_timeout))
    # _window = search_window(0, -1, 64, _server, _port, 64, _packet_size, _timeout, _packets)
    # print('Best window size is found It is {0} packets'.format(int(_window)))

    windows = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    # windows = [128, 256, 512]   # for test purpose
    total_window = len(windows)
    throughputs = []
    throughputs_err = []
    lost_bytes = []
    lost_bytes_err = []
    lost_packets = []
    lost_packets_err = []
    for w in range(0, total_window):
        print('Current window size is {0}. Searching for the best timeout first.'.format(windows[w]))
        _timeout = search_timeout(0.0, -1, 0.5, _server, _port, windows[w], _packet_size, 0.1, _packets)
        tp = []
        clb = []
        clp = []
        for i in range(0, 5):
            print('Running the same configuration: #{0}'.format(i + 1))
            time, lp, lb = client.client(_server, _port, windows[w], _timeout, _packet_size, _packets)
            tp.append((_packet_len*_packet_size/1024)/time)
            clb.append(lb)
            clp.append(lp)
        throughputs.append(np.mean(tp))
        throughputs_err.append(np.std(tp))
        lost_bytes.append(np.mean(clb))
        lost_bytes_err.append(np.std(clb))
        lost_packets.append(np.mean(clp))
        lost_packets_err.append(np.std(clp))
    # plt.figure()
    # plt.errorbar(windows, throughputs, yerr=throughputs_err, fmt='o')
    # plt.errorbar(windows, lost_bytes, yerr=lost_bytes_err, fmt='o')
    # plt.errorbar(windows, lost_packets, yerr=lost_packets_err, fmt='o')
    # plt.xscale('log')
    # plt.show()
    with open(str(_packet_size) + '_result_data.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['packet_size', 'window_size', 'throughput', 'throughput_err',
                             'lost_bytes', 'lost_bytes_err', 'lost_packets', 'lost_packets_err'])
        for i in range(0, total_window):
            spamwriter.writerow([_packet_size, windows[i], throughputs[i], throughputs_err[i],
                                 lost_bytes[i], lost_bytes_err[i], lost_packets[i], lost_packets_err[i]])
