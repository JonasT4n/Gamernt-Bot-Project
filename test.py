def insertion(alist):
    for i in range(len(alist)):
        tempVal = alist[i]
        indexHole = i - 1
        while indexHole >= 0 and tempVal < alist[indexHole]:
            alist[indexHole + 1] = alist[indexHole]
            indexHole -= 1
        alist[indexHole + 1] = tempVal

s = [6, 1, 5, 2]
insertion(s)
print(s)