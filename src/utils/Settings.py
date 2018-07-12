class Settings:
    def __init__(self, fname):
        self.fname = fname
        res = self.readSettings()
        for key, val in res.items():
            self.__dict__[key] = val

    def __getitem__(self, item):
        return self.__dict__[item]

    def readSettings(self):
        res = {}
        curr_line = 0
        with open(self.fname, 'rt') as fd:
            for line in fd:
                curr_line += 1
                if not line.startswith('#'):
                    line = line.strip(' \n\t\r')

                    if not len(line):
                        continue

                    if line.find('=') >= 0:
                        opt, val = line.split("=")
                        res[opt] = val
                    else:
                        raise Exception("Wrong format of settings file : '%s' near the line: %d" % (self.fname, curr_line))

        return res