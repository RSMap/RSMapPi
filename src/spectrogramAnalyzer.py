import numpy as np
from queue import Queue, Empty

class Analyzer:

    def __init__(self, min_block, max_block, analyze):
        self.data = Queue()
        self.min_block = min_block
        self.max_block = max_block
        self.analyze = analyze

    def data_size(self):
        return self.data.qsize()

    def add_sample(self, sample):
        self.data.put(sample)

    def get_sample(self):
        return self.data.get()

    def analyze(self):
        aux_data = []
        num_values_readed = 0
        null_values_readed = 0
        while self.analyze:
            try:
                value = self.data.get(block=False)
                num_values_readed += 1
                if value < 0.5:
                    null_values_readed += 1
                    num_values_readed += 1
                    aux_data.insert(num_values_readed, -1)
                else:
                    aux_data.insert(value)
            except Empty:
                print(str(aux_data))
                self.analyze = False


def main():
    a = Analyzer(min_block=30, max_block=80)
    print(a.data_size())
    a.add_sample(3.034)
    a.add_sample(0.4332)
    print(a.data_size())
    a.analyze()

if __name__ == '__main__':
    main()
