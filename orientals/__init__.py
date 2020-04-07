from clesto import Module_element


class Simplex(tuple):
    def __lt__(self, other):
        '''...'''
        def lt(x, y):
            if x[0] < y[0]:
                return True
            if x[0] == y[0]:
                return lt(x[1:], y[1:])

        x = sorted(self)
        y = sorted(other)
        return lt(x, y)

    def atom(self):
        '''...'''
        if isinstance(self, int):
            self = tuple(range(self + 1))
        answer = {'-': [SADC_element({self: 1})],
                  '+': [SADC_element({self: 1})]}

        for i in range(len(self) - 1):
            minus, plus = answer['+'][i].split_boundary()
            print(minus)
            answer['-'].append(minus)
            answer['+'].append(plus)

        return Mu_element(tuple(answer['-'][::-1]),
                          tuple(answer['+'][::-1]))


class SADC_element(Module_element):
    ''' Augmented Directed Complex
    '''

    def __lt__(self, other):
        return all((v > 0 for v in (other - self).values()))

    def split(self):
        '''...'''
        m = SADC_element({k: abs(v) for k, v in self.items() if v < 0})
        p = SADC_element({k: abs(v) for k, v in self.items() if v > 0})
        return m, p

    def boundary(self):
        boundary = SADC_element()
        for spx, v in self.items():
            for i in range(len(spx)):
                boundary += SADC_element(
                    {spx[:i] + spx[i + 1:]: v * (-1)**(i % 2)})
        return boundary

    def split_boundary(self):
        return self.boundary().split()


class Mu_element:
    '''...'''

    def __init__(self, minus, plus):
        # TODO: perform input check

        self.minus = minus
        self.plus = plus

    def __eq__(self, other):
        if isinstance(other, SADC_element):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return f'Mu_element({self.minus}, {self.plus})'

    def __str__(self):
        string = ''.join((f'{str(m)} | {str(p)} \n' for m, p in
                          zip(self.minus, self.plus)))
        return string.replace(', ', ',')

    def source(self, k):
        '''...'''
        return Mu_element(self.minus[:k + 1],
                          self.plus[:k] + (self.minus[k],))

    def target(self, k):
        '''...'''
        return Mu_element(self.minus[:k] + (self.plus[k],),
                          self.plus[:k + 1])

    def compose(self, other, k):
        '''...'''
        if self.target(k) != other.source(k):
            raise TypeError(f'corresponding target & source must be equal')

        p, q = len(self.minus), len(other['-'])
        c = (self.target(k)['-'] + (SADC_element(),) * max(0, abs(q - p)),
             self.target(k).plus) + (SADC_element(),) * max(0, abs(q - p))
        a = ((self.minus + (SADC_element(),) * max(0, q - p)),
             (self.plus + (SADC_element(),) * max(0, q - p)))
        b = ((other['-'] + (SADC_element(),) * max(0, p - q)),
             (other.plus + (SADC_element(),) * max(0, p - q)))
        return Mu_element(
            (x + y - z for x, y, z in zip(a[0], b[0], c[0])),
            (x + y - z for x, y, z in zip(a[1], b[1], c[1])))
