import numpy as np
from queue import Queue, Empty

class Analyzer:
    def __init__(self, min_block, max_block, datasource):
        self.data = Queue()
        self.min_block = min_block
        self.max_block = max_block
        self.datasource = datasource

    def data_size(self):
        return self.data.qsize()

    def get_datasource_sample(self, sample):
        try:
            return self.datasource.get()
        except Empty:
            print("empty datasource")
            return None

    def add_sample(self, sample):
        self.data.put(sample)

    def get_sample(self):
        return self.data.get()

    def analyze(self):
        readed_data = Queue()
        num_values_readed = 0
        null_values_readed = 0
        while True:
            try:
                value = self.data.get(block=False)
                num_values_readed += 1
                if value < 0.5:
                    null_values_readed += 1
                    num_values_readed += 1
                    readed_data.put(-1)
                else:
                    readed_data.put(value)
            except Empty:
                print(str(readed_data))


def main():
    a = Analyzer(min_block=30, max_block=80)
    print(a.data_size())
    a.add_sample(3.034)
    a.add_sample(0.4332)
    print(a.data_size())
    a.analyze()

if __name__ == '__main__':
    main()
