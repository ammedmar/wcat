from collections import Counter


class Module_element(Counter):
    """
    Counter with arithmetic improvements to handle (modular) integer values.

    Class constructed to model free module elements over the ring of
    (modular) integers.

    Attributes
    ----------
    default_torsion : non-negative int or string 'free'
        An int m sets R = Z/mZ whereas 'free' sets R = Z

    """

    default_torsion = 'free'

    def __init__(self, data=None, torsion=None):
        # print('initializing as Module_element')

        # check input data: dict with int values
        if data:
            if not (isinstance(data, dict) and
                    all((type(v) is int for v in data.values()))
                    ):
                raise TypeError('input must be dict with int values')

        # checking input torsion: positive int or 'free'
        if torsion is not None:
            if not (isinstance(torsion, int) and torsion > 0 or
                    torsion == 'free'
                    ):
                raise TypeError("torsion must be a positive int or 'free'")

        # setting torsion
        m = torsion if torsion else type(self).default_torsion
        setattr(self, 'torsion', m)

        # initialize element
        super(Module_element, self).__init__(data)

        self._reduce_rep()

    def __str__(self):
        if not self:
            return '0'
        else:
            answer = ''
            for key, value in self.items():
                if value < -1:
                    answer += f' - {abs(value)}{key}'
                elif value == -1:
                    answer += f' - {key}'
                elif value == 1:
                    answer += f' + {key}'
                elif value > 1:
                    answer += f' + {value}{key}'
            if answer[:2] == ' +':
                answer = answer[3:]
            if answer[:2] == ' -':
                answer = answer[1:]

            return answer

    def __add__(self, other):
        '''The sum of two free module elements.

        >>> Module_element({'a':1, 'b':2}) + Module_element({'a':1})
        Module_element({'a':2, 'b':2})

        '''
        self.compare_attributes(other)
        answer = type(self)(self).copy_attrs_from(self)
        answer.update(other)
        answer._reduce_rep()
        return answer

    def __sub__(self, other):
        '''The substraction of two free module elements.

        >>> Module_element({'a':1, 'b':2}) - Module_element({'a':1})
        Module_element({'b':2})

        '''
        self.compare_attributes(other)
        answer = type(self)(self).copy_attrs_from(self)
        answer.subtract(other)
        answer._reduce_rep()
        return answer

    def __rmul__(self, c):
        '''The scaling by c of a free module element.

        >>> 3*Module_element({'a':1, 'b':2})
        Module_element({'a':3, 'b':6})

        '''
        if not isinstance(c, int):
            raise TypeError(f'can not act by non-int of type {type(c)}')

        scaled = {k: c * v for k, v in self.items()}
        answer = type(self)(scaled).copy_attrs_from(self)
        return answer

    def __neg__(self):
        '''The additive inverse of a free module element.

        >>> -Module_element({'a':1, 'b':2})
        Module_element({'a':-1, 'b':-22})

        '''
        return self.__rmul__(-1)

    def __iadd__(self, other):
        '''The in place addition of two free module elements.

        >>> x = Module_element({'a':1, 'b':2})
        >>> x += Module_element({'a':3, 'b':6})
        Module_element({'a':4, 'b':8})

        '''
        self.compare_attributes(other)
        self.update(other)
        self._reduce_rep()
        return self

    def __isub__(self, other):
        '''The in place addition of two free module elements.

        >>> x = Module_element({'a':1, 'b':2})
        >>> x -= Module_element({'a':3, 'b':6})
        Module_element({'a':-2, 'b':-4})

        '''
        self.compare_attributes(other)
        self.subtract(other)
        self._reduce_rep()
        return self

    def _reduce_rep(self):
        '''The preferred representative of the free module element.

        It reduces all values mod n if torsion is n and removes
        key:value pairs with value = 0.

        >>> Module_element({'a':1, 'b':2, 'c':0})
        Module_element({'a':1, 'b':2})

        '''
        # print('reducing as Module_element')
        # reducing coefficients mod torsion
        if self.torsion != 'free':
            for key, value in self.items():
                self[key] = value % self.torsion

        # removing key:value pairs with value = 0
        zeros = [k for k, v in self.items() if not v]
        for key in zeros:
            del self[key]

    def set_torsion(self, m):
        '''...'''
        setattr(self, 'torsion', m)
        self._reduce_rep()
        return self

    def compare_attributes(self, other):
        '''...'''
        if self.__dict__ != other.__dict__:
            raise AttributeError('not the same attributes')

    def copy_attrs_from(self, other):
        '''...'''
        for attr, value in other.__dict__.items():
            setattr(self, attr, value)
        self._reduce_rep()
        return(self)


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
                try:
                    return not lt(x[1:], y[1:])
                except IndexError:
                    if len(x) == 1:
                        return True
                    else:
                        False

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

        over = self.target(k)
        # padding with 0s
        p, q = len(self['minus']), len(other['minus'])
        a, b, c = {}, {}, {}
        a['m'] = (self['minus'] + (SADC_element(),) * max(0, q - p))
        a['p'] = (self['plus'] + (SADC_element(),) * max(0, q - p))
        b['m'] = (other['minus'] + (SADC_element(),) * max(0, p - q))
        b['p'] = (other['plus'] + (SADC_element(),) * max(0, p - q))
        c['m'] = (over['minus'] + (SADC_element(),) * (max(p, q) - k - 1))
        c['p'] = (over['plus'] + (SADC_element(),) * (max(p, q) - k - 1))
        return Mu_element(
            (x + y - z for x, y, z in zip(a['m'], b['m'], c['m'])),
            (x + y - z for x, y, z in zip(a['p'], b['p'], c['p'])))

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
