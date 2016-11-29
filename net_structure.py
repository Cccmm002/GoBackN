class Packet:
    def __init__(self, flag, pid, data):
        self.flag = flag
        self.pid = pid
        self.data = data

    def encode(self):
        data_len = len(self.data)
        res = bytearray(data_len + 4)
        res[0] = ord(self.flag)
        res[3] = self.pid % 256
        fid = self.pid // 256
        res[2] = fid % 256
        res[1] = fid // 256
        for i in range(data_len):
            res[i + 4] = ord(self.data[i])
        return res


def decode(pack):
    pid = pack[1]*256*256 + pack[2]*256 + pack[3]
    if pack[0] == ord('A'):
        return Packet('A', pid, [])
    elif pack[0] == ord('P'):
        return Packet('P', pid, [])
    else:
        data_len = len(pack) - 4
        data = bytearray(data_len)
        for i in range(data_len):
            data[i] = pack[i + 4]
        return Packet('D', pid, data)
