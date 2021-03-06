import instrument

class Weather(instrument.Instrument):
    def __init__(self, instr, date, statusType, status, statusMessage='NULL', dev=False):
        super().__init__(date,statusType, status, statusMessage, dev)
        self.instr = instr

        #override types so weather only has one type of status update
        #todo: add these for other "instrument" classes?
        self.types = {
            'weather':self.weatherStatus
        }
