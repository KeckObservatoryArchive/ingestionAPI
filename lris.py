import instrument

class Lris(instrument.Instrument):
    def __init__(self, instr, date, statusType, status, statusMessage='NULL'):
        super().__init__(date,statusType, status, statusMessage)
        self.instr = instr
