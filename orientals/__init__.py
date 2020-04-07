from clesto import Module_element


class SADC_element:
    ''' Base class modeling strong augmented directed complexes.

    Attributes: minus and plus. Both are tuples of Module elements

    '''

    def __init__(self, minus, plus):
        # TODO: perform input check

        self.minus = tuple(minus)
        self.plus = tuple(plus)

    def __eq__(self, other):
        if isinstance(other, SADC_element):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return f'SADC_element({self.minus}, {self.plus})'

    def __str__(self):
        string = ''.join((f'{str(m)} | {str(p)} \n' for m, p in
                          zip(self.minus, self.plus)))
        return string.replace(', ', ',')

    @classmethod
    def atom(self, simplex):
        '''...'''
        if isinstance(simplex, int):
            simplex = tuple(range(simplex + 1))

        answer = {'-': [Module_element({simplex: 1})],
                  '+': [Module_element({simplex: 1})]}
        for i in range(len(simplex) - 1):
            minus, plus = SADC_element.split(
                SADC_element.boundary(answer['+'][i]))
            answer['-'].append(minus)
            answer['+'].append(plus)

        return self(tuple(answer['-'][::-1]), tuple(answer['+'][::-1]))

    def source(self, k):
        '''...'''
        return SADC_element(self.minus[:k + 1],
                            self.plus[:k] + (self.minus[k],))

    def target(self, k):
        '''...'''
        return SADC_element(self.minus[:k] + (self.plus[k],),
                            self.plus[:k + 1])

    def compose(self, other, k):
        '''...'''
        if self.target(k) != other.source(k):
            raise TypeError(f'corresponding target & source must be equal')

        p, q = len(self.minus), len(other.minus)
        c = (self.target(k).minus + (Module_element(),) * max(0, abs(q - p)),
             self.target(k).plus) + (Module_element(),) * max(0, abs(q - p))
        a = ((self.minus + (Module_element(),) * max(0, q - p)),
             (self.plus + (Module_element(),) * max(0, q - p)))
        b = ((other.minus + (Module_element(),) * max(0, p - q)),
             (other.plus + (Module_element(),) * max(0, p - q)))
        return SADC_element(
            (x + y - z for x, y, z in zip(a[0], b[0], c[0])),
            (x + y - z for x, y, z in zip(a[1], b[1], c[1])))

    def decompose(self):
        top = self.minus[-1]
        boundaries = {simplex: SADC_element.split_boundary({simplex: 1})
                      for simplex in top}
        return boundaries

    @staticmethod
    def split(chain):
        '''...'''
        m = Module_element({k: abs(v) for k, v in chain.items() if v < 0})
        p = Module_element({k: abs(v) for k, v in chain.items() if v > 0})
        return m, p

    @staticmethod
    def boundary(chain):
        boundary = Module_element()
        for spx, v in chain.items():
            for i in range(len(spx)):
                boundary += Module_element(
                    {spx[:i] + spx[i + 1:]: v * (-1)**(i % 2)})

        return boundary

    @staticmethod
    def split_boundary(chain):
        p, m = SADC_element.split(SADC_element.boundary(chain))
        return set(p.keys()), set(m.keys())

    @staticmethod
    def order(chain):
        '''works well for all coeff equal to one'''
        boundaries = dict()
        for simplex in chain.keys():
            boundaries[simplex] = SADC_element.split_boundary({simplex: 1})

        return boundaries


n = 4
x = SADC_element.atom(n)
y = x.source(n - 1)
print(y)
print(SADC_element.decompose(y))
