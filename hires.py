import instrument
import db_conn as DBC

class Hires(instrument.Instrument):
    def __init__(self, instr, date, statusType, status):
        super().__init__(date,statusType, status)
        self.instr = instr
        self.stagedir = ''
