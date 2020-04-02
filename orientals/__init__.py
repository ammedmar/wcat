from clesto import Module_element


class Oriental_element:
    '''...'''

    def __init__(self, minus, plus):
        '''...'''
        self.minus = tuple(minus)
        self.plus = tuple(plus)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Oriental_element):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return f'Oriental_element({self.minus}, {self.plus})'

    def __str__(self):
        s = ''.join((', ' + str(elmt) for elmt in self.minus))
        t = ''.join((', ' + str(elmt) for elmt in self.plus))
        return '(' + s[2:] + ')\n' + '(' + t[2:] + ')'

    @classmethod
    def from_simplex(self, simplex):
        '''...'''
        if isinstance(simplex, int):
            simplex = tuple(range(simplex + 1))

        def split(elmt):
            '''...'''
            m = Module_element({k: abs(v) for k, v in elmt.items() if v < 0})
            p = Module_element({k: abs(v) for k, v in elmt.items() if v > 0})
            return m, p

        answer = {'-': [Module_element({simplex: 1})],
                  '+': [Module_element({simplex: 1})]}
        for i in range(len(simplex) - 1):
            minus, plus = split(Oriental_element.boundary(answer['+'][i]))
            answer['-'].append(minus)
            answer['+'].append(plus)

        return self(tuple(answer['-'][::-1]), tuple(answer['+'][::-1]))

    def source(self, k):
        '''...'''
        return Oriental_element(self.minus[:k + 1],
                                self.plus[:k] + (self.minus[k],))

    def target(self, k):
        '''...'''
        return Oriental_element(self.minus[:k] + (self.plus[k],),
                                self.plus[:k + 1])

    def compose(self, other, k):
        '''...'''

        # print(self.target(k), other.source(k))
        if self.target(k) != other.source(k):
            raise TypeError(f'corresponding target & source must be equal')

        p, q = len(self.minus), len(other.minus)
        c = (self.target(k).minus + (Module_element(),) * max(0, abs(q - p)),
             self.target(k).plus) + (Module_element(),) * max(0, abs(q - p))
        a = ((self.minus + (Module_element(),) * max(0, q - p)),
             (self.plus + (Module_element(),) * max(0, q - p)))
        b = ((other.minus + (Module_element(),) * max(0, p - q)),
             (other.plus + (Module_element(),) * max(0, p - q)))
        return Oriental_element(
            (x + y - z for x, y, z in zip(a[0], b[0], c[0])),
            (x + y - z for x, y, z in zip(a[1], b[1], c[1])))

    @staticmethod
    def boundary(elmt):
        boundary = Module_element()
        for spx, v in elmt.items():
            for i in range(len(spx)):
                boundary += Module_element(
                    {spx[:i] + spx[i + 1:]: v * (-1)**(i % 2)})

        return boundary
