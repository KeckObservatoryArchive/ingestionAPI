import instrument

class Nirspec(instrument.Instrument):
    def __init__(self, instr, date, statusType, status, statusMessage='NULL', dev=False):
        super().__init__(date,statusType, status, statusMessage, dev)
        self.instr = instr
