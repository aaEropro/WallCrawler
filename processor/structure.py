import os


class Structure:
    compact_body = None

    errors = list()

    structure = {
        'head': {
            'dedication': False,
            'foreword': False,
            'epigraph': False,
            'prologue': False,
        },
        'body': [],
        'bottom': {
            'epilogue': False,
            'appendix': False,
            'acknowledgements': False,
            'copyrignt': False
        },
        'unrecognized': []
    }

    def s(self, dir_path):
        t = ''

        for path, directories, files in os.walk(dir_path):
            for item in files:

                if item.endswith('.txt'):
                    t = item.split('-')[0]
                    print(t)
                    if t in self.structure['head'].keys():
                        self.structure['head'][t] = True

                    elif t in self.structure['bottom'].keys():
                        self.structure['bottom'][t] = True
                        
                    elif t.isdigit():
                        self.structure['body'].append(item)
                    else:
                        print(f'WARNING: file {item} has no recognisable type.')
                        self.structure['unrecognized'].append(item)

        # print(self.structure)

        self._check_compact_body()

        return self.structure

    def _check_compact_body(self):
        self.compact_body = True
        data = sorted( [item.split('-')[0] for item in self.structure['body']] )

        if data[0] not in ['00', '01']:
            self.errors.append(f'WARNING: chapters start at {data[0]} not 01.')
            self.compact_body = False

        for index, _ in enumerate(data[1:], 1):
            if int(data[index]) - int(data[index-1]) > 1:
                self.errors.append(f'WARNING: chapter(s) skipped between {data[index-1]} and {data[index]}.')
                self.compact_body = False
            elif int(data[index]) - int(data[index-1]) == 0:
                self.errors.append(f'WARNING: duplicate chapter number {data[index-1]}, {data[index]}.')
                self.compact_body = False