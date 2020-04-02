import numpy as np


def partial(s, i):
    return s.replace(s[i], '')


def common(a, b):
    c = []
    alpha = b[:]
    beta = a[:]
    for i in alpha:
        if i in beta:
            c.append(i)
            beta.remove(i)
    return c


def simplifie(pos, neg):
    p = pos[:]
    n = neg[:]
    c = common(pos, neg)
    for i in c:
        p.remove(i)
        n.remove(i)
    return(p, n)


def sommeFormelle(l1, l2):
    return simplifie(l1[0] + l2[0], l1[1] + l2[1])


def minus(l):
    return (l[1], l[0])


def afficheSomme(l1, l2):
    return affiche((sommeFormelle(l1, l2)[0], sommeFormelle(l1, l2)[1]))


def affiche(l):
    aff_pos = ''
    aff_neg = ''
    pos = l[0]
    neg = l[1]
    for i in range(len(pos)):
        aff_pos = aff_pos + '+' + pos[i]
    for i in range(len(neg)):
        aff_neg = aff_neg + '-' + neg[i]
    return aff_pos + aff_neg


def boundary(s):
    positif = []
    negatif = []
    for i in range(len(s)):
        if i % 2 == 0:
            positif += [partial(s, i)]
        else:
            negatif += [partial(s, i)]
    return simplifie(positif, negatif)


def listBoundary(l):
    c = ([], [])
    for i in l[0]:
        c = sommeFormelle(c, boundary(i))
    for i in l[1]:
        c = sommeFormelle(c, minus(boundary(i)))
    return c


def boundaryPlusIterated(l, n):
    if n == 1:
        return listBoundary(l)[0]
    return boundaryPlusIterated((listBoundary(l)[0], []), n - 1)


def boundaryMinusIterated(l, n):
    if n == 1:
        return listBoundary(l)[1]
    return boundaryMinusIterated((listBoundary(l)[1], []), n - 1)


def afficheBoundary(s):
    return affiche((boundary(s)[0], boundary(s)[1]))


def atom(s):
    posDel = [s]
    negDel = [s]
    l = ([s], [])
    i = 1
    while i < len(s):
        posDel = [affiche((boundaryPlusIterated(l, i), []))] + posDel
        negDel = [affiche((boundaryMinusIterated(l, i), []))] + negDel
        i += 1
    return (posDel, negDel)


def afficheAtom(s):
    print(np.array([atom(s)[1], atom(s)[0]]))


def source(n, signe, s):
    pos = []
    neg = []
    i = 0
    while i < n:
        pos.append(atom(s)[0][i])
        neg.append(atom(s)[1][i])
        i += 1
    if signe == 1:
        pos.append(atom(s)[0][n])
        neg.append(atom(s)[0][n])
    else:
        pos.append(atom(s)[1][n])
        neg.append(atom(s)[1][n])
    return (pos, neg)


def afficheSource(n, signe, s):
    print(np.array([source(n, signe, s)[1], source(n, signe, s)[0]]))


print(afficheAtom('0123'))
