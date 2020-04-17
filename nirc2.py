import instrument

class Nirc2(instrument.Instrument):
    def __init__(self, instr, date, statusType, status, statusMessage='NULL', dev=False):
        super().__init__(date,statusType, status, statusMessage, dev)
        self.instr = instr.upper()
