import argparse
import time
import client


def _search_run(server, port, window, timeout, packet_size, packets, _timeout_, cur):
    if _timeout_:
        t = client.client(server, port, window, cur, packet_size, packets)
    else:
        t = client.client(server, port, int(cur), timeout, packet_size, packets)
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

    print('Searching for the best timeout and window size.')
    _timeout = search_timeout(0.0, -1, 0.5, _server, _port, 64, _packet_size, 0.1, _packets)
    print('Best timeout is found! It is {0} seconds.'.format(_timeout))
    _window = search_window(0, -1, 64, _server, _port, 64, _packet_size, _timeout, _packets)
    print('Best window size is found It is {0} packets'.format(int(_window)))
