from clesto import Module_element


class ADC_element(Module_element):
    ''' Augmented Directed Complex
    '''

    def split(self):
        '''...'''
        m = ADC_element({k: abs(v) for k, v in self.items() if v < 0})
        p = ADC_element({k: abs(v) for k, v in self.items() if v > 0})
        return m, p

    def boundary(self):
        boundary = ADC_element()
        for spx, v in self.items():
            for i in range(len(spx)):
                boundary += ADC_element(
                    {spx[:i] + spx[i + 1:]: v * (-1)**(i % 2)})

        return boundary

    def split_boundary(self):
        return self.boundary().split()

    @classmethod
    def atom(self, simplex):
        '''...'''
        if isinstance(simplex, int):
            simplex = tuple(range(simplex + 1))

        answer = {'-': [ADC_element({simplex: 1})],
                  '+': [ADC_element({simplex: 1})]}

        for i in range(len(simplex) - 1):
            minus, plus = answer['+'][i].split_boundary()
            answer['-'].append(minus)
            answer['+'].append(plus)

        return Mu_element(tuple(answer['-'][::-1]),
                          tuple(answer['+'][::-1]))

    @classmethod
    def atom(self, simplex):
        '''...'''
        if isinstance(simplex, int):
            simplex = tuple(range(simplex + 1))
        answer = {'-': [ADC_element({simplex: 1})],
                  '+': [ADC_element({simplex: 1})]}

        for i in range(len(simplex) - 1):
            minus, plus = answer['+'][i].split_boundary()
            answer['-'].append(minus)
            answer['+'].append(plus)

        return Mu_element(tuple(answer['-'][::-1]),
                          tuple(answer['+'][::-1]))


class Mu_element:
    '''...'''

    def __init__(self, minus, plus):
        # TODO: perform input check

        self.minus = minus
        self.plus = plus

    def __eq__(self, other):
        if isinstance(other, ADC_element):
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
        c = (self.target(k)['-'] + (ADC_element(),) * max(0, abs(q - p)),
             self.target(k).plus) + (ADC_element(),) * max(0, abs(q - p))
        a = ((self.minus + (ADC_element(),) * max(0, q - p)),
             (self.plus + (ADC_element(),) * max(0, q - p)))
        b = ((other['-'] + (ADC_element(),) * max(0, p - q)),
             (other.plus + (ADC_element(),) * max(0, p - q)))
        return Mu_element(
            (x + y - z for x, y, z in zip(a[0], b[0], c[0])),
            (x + y - z for x, y, z in zip(a[1], b[1], c[1])))
