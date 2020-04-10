from clesto import Module_element


class Simplex(tuple):

    @property
    def dimension(self):
        return len(self) - 1

    def __str__(self):
        '''...'''
        return super(Simplex, self).__str__().replace(', ', ',')

    def __lt__(self, other):
        '''...'''
        def lt(x, y):
            if x[0] < y[0]:
                return True
            if x[0] == y[0]:
                return not lt(x[1:], y[1:])

        x = sorted(self)
        y = sorted(other)
        return lt(x, y)

    def boundary(self):
        bdry = {0: set(), 1: set()}
        for i in range(len(self)):
            bdry[(i % 2)].add(Simplex(self[:i] + self[i + 1:]))
        return bdry

    @classmethod
    def standard(self, d):
        return self(range(d + 1))

    def atom(self):
        '''...'''
        if isinstance(self, int):
            self = tuple(range(self + 1))
        answer = {'-': [SADC_element({self: 1})],
                  '+': [SADC_element({self: 1})]}

        for i in range(len(self) - 1):
            minus, plus = answer['+'][i].split_boundary()
            answer['-'].append(minus.sort())
            answer['+'].append(plus.sort())

        return Mu_element(tuple(answer['-'][::-1]),
                          tuple(answer['+'][::-1]))


class SADC_element(Module_element):
    ''' Augmented Directed Complex
    Module_element of basis_elements
    '''

    def split(self):
        '''...'''
        m = SADC_element({k: abs(v) for k, v in self.items() if v < 0})
        p = SADC_element({k: abs(v) for k, v in self.items() if v > 0})
        return m, p

    def boundary(self):
        bdry = SADC_element()
        for belmt, v in self.items():
            for i in range(2):
                bdry += SADC_element(
                    {s: ((-1) ** i) * v for s in belmt.boundary()[i]})
        return bdry

    def split_boundary(self):
        return self.boundary().split()

    def sort(self):
        '''...'''
        sorted_data = sorted(self.items(), key=lambda pair: pair[0])
        return SADC_element(dict(sorted_data))


class Mu_element(dict):
    '''...'''

    def __init__(self, minus, plus):
        '''two tuples of SADC_element'''

        self['minus'] = minus
        self['plus'] = plus

    def __repr__(self):
        '''...'''
        return f'Mu_element({self["minus"]}, {self["plus"]})'

    def __str__(self):
        string = ''.join((f'{str(m)} | {str(p)} \n' for m, p in
                          zip(self['minus'], self['plus'])))
        return string.replace(', ', ',')

    @property
    def dimension(self):
        '''...'''
        return len(self['minus']) - 1

    def source(self, k):
        '''...'''
        return Mu_element(self['minus'][:k + 1],
                          self['plus'][:k] + (self['minus'][k],))

    def target(self, k):
        '''...'''
        return Mu_element(self['minus'][:k] +
                          (self['plus'][k],), self['plus'][:k + 1])

    def compose(self, other, k):
        '''...'''
        if self.target(k) != other.source(k):
            raise TypeError(f'corresponding target & source must be equal')

        p, q = len(self['minus']), len(other['minus'])
        c = (self.target(k)['minus'] + (SADC_element(),) * max(0, abs(q - p)),
             self.target(k)['plus']) + (SADC_element(),) * max(0, abs(q - p))
        a = ((self['minus'] + (SADC_element(),) * max(0, q - p)),
             (self['plus'] + (SADC_element(),) * max(0, q - p)))
        b = ((other['minus'] + (SADC_element(),) * max(0, p - q)),
             (other['plus'] + (SADC_element(),) * max(0, p - q)))
        return Mu_element(
            (x + y - z for x, y, z in zip(a[0], b[0], c[0])),
            (x + y - z for x, y, z in zip(a[1], b[1], c[1])))

    def decompose(self):
        '''...'''
        def decomp(bracket):
            '''A bracket is a list of the ordered elements to be decomposed.
            At each step we replace an element in the bracket by a bracket of 
            its codimension 1 decomposition w/r to its near neighbor.'''
            if min(s.dimension for s in bracket) == 1 or len(bracket) == 1:
                return bracket
            bracket = [[term] for term in bracket]
            for i in range(len(bracket) - 1):
                x, y = bracket[i], bracket[i + 1]
                max_x = sorted(x, key=lambda x_i: x_i.dimension)[-1]
                max_y = sorted(y, key=lambda y_i: y_i.dimension)[-1]
                comp_deg = min(max_x.dimension, max_y.dimension) - 1
                forward_x = (max_x.atom()['plus'][comp_deg] + SADC_element(
                    {spx: 1 for spx in filter(lambda x_i: x_i != max_x, x)}))
                backward_y = (max_y.atom()['minus'][comp_deg] + SADC_element(
                    {spx: 1 for spx in filter(lambda y_i: y_i != max_y, y)}))
                h = forward_x - backward_y
                bracket[i] = sorted(x + [k for k, v in h.items() if v < 0])
                bracket[i + 1] = sorted(y + [k for k, v in h.items() if v > 0])

            return [decomp(subbracket) for subbracket in bracket]

        bracket = list(self['minus'][-1].keys())
        return decomp(bracket)
