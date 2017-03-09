def findNegativeCycles(times, i, j, cost, visited):
    if (cost + times[j][i]) < 0:
        print "Cycle", visited
        return True
    bunnies = len(times)
    for k in range(bunnies):
        if (k != j):
            if k not in visited:
                cost += times[j][k]
                visited.append(k)
                negative = findNegativeCycles(times, i, k, cost, visited)
                if negative:
                    return True
                cost -= times[j][k]
                visited.remove(k)
    return False

def findCycles(times):
    bunnies = len(times)
    for i in range(bunnies):
        for j in range(bunnies):
            if times[i][j] < 0:
                negative = findNegativeCycles(times, i, j, times[i][j], [i, j])
                if negative:
                    return True
    return False

def getLookAhead(i, times, alreadyUsed):
    lookAheadMin = 100000
    bunnies = len(times)
    for k in range(bunnies):
        if i != k:
            key = "%d,%d" % (i, k)
            if key not in alreadyUsed:
                if times[i][k] < lookAheadMin:
                    lookAheadMin = times[i][k]
            else:
                # Avoid already used edges, unless they have negative cost.
                if (times[i][k] <= 0) and (alreadyUsed[key] < bunnies) and \
                        (times[i][k] < lookAheadMin):
                    lookAheadMin = times[i][k]
    # Minimum look ahead not found, possibly because of alreadyUsed. Now, do a
    # plain minimum look ahead without using alreadyUsed.
    if lookAheadMin == 100000:
        for k in range(bunnies):
            if (i != k) and (times[i][k] < lookAheadMin):
                lookAheadMin = times[i][k]
    return lookAheadMin

def getLookBack(i, times, alreadyUsed):
    lookBackMin = 100000
    bunnies = len(times)
    for k in range(bunnies):
        if i != k:
            key = "%d,%d" % (k, i)
            if key not in alreadyUsed:
                if times[k][i] < lookBackMin:
                    lookBackMin = times[k][i]
            else:
                # Avoid already used edges, unless they have negative cost.
                if (times[k][i] <= 0) and (alreadyUsed[key] < bunnies) and \
                        (times[k][i] < lookBackMin):
                    lookBackMin = times[k][i]
    # Minimum look back not found, possibly because of alreadyUsed. Now, do a
    # plain minimum look back without using alreadyUsed.
    if lookBackMin == 100000:
        for k in range(bunnies):
            if (i != k) and (times[k][i] < lookBackMin):
                lookBackMin = times[k][i]
    return lookBackMin

def answer(times, time_limit):
    # Try both algorithms, pick the one where more bunnies can be saved.
    greedyStart = answerGreedyStart(times, time_limit)
    greedyMin = answerGreedyMin(times, time_limit)
    final = []
    if len(greedyStart) < len(greedyMin):
        final = greedyMin
    elif len(greedyMin) < len(greedyStart):
        final = greedyStart
    else:
        greedyStart1 = str(greedyStart)
        greedyMin1 = str(greedyMin)
        if greedyStart1 < greedyMin1:
            final = greedyStart
        else:
            final = greedyMin
    print final
    print "--------------------------------------------------------------------"

# Start from 0, pick the least edge so that (cost-of-edge + min(cost-of-next))
# is minimised.
# Use negative edges (bunny-count + 1) times, assuming that each time a
# negative edge is used, it reduces the time_limit.
def answerGreedyStart(times, time_limit):
    bunnies = len(times)
    # If negative cycle is found, we can save all bunnies
    negative = findCycles(times)
    if negative:
        saved = range(bunnies - 2)
        return saved
    start = 0
    alreadyUsed = {}
    path = []
    costList = []
    totalCost = 0
    lookAheadMin = 0
    visited = set()
    visited.add(0)
    while True:
        minimum = 1000000
        minIndex = -1
        # In each iteration, give priority to vertices which have not been
        # visited.
        search = [x for x in range(bunnies) if x not in visited and x != start]
        search += [x for x in visited if x != start]
        for i in search:
            if i != start:
                key = "%d,%d" % (start, i)
                if (key not in alreadyUsed) or ((times[start][i] <= 0) and \
                        (alreadyUsed[key] < bunnies)):
                    lookAheadMin = getLookAhead(i, times, alreadyUsed)
                    lookCost = times[start][i] + lookAheadMin
                    if lookCost < minimum:
                        minimum = lookCost
                        minIndex = i
                    if lookCost == minimum:
                        if times[start][i] < times[start][minIndex]:
                            minIndex = i
        if minIndex == -1:
            break
        path.append([start, minIndex])
        totalCost += times[start][minIndex]
        visited.add(minIndex)
        costList.append(totalCost)
        key = "%d,%d" % (start, minIndex)
        if key in alreadyUsed:
            alreadyUsed[key] += 1
        else:
            alreadyUsed[key] = 1
        start = minIndex

    # The above creates a path where the cost may go up and down depending on
    # presence of negative edges. Iterate through the path in reverse order till
    # the cost matches the argument.
    found = False
    for i, cost in reversed(list(enumerate(costList))):
        if (cost + times[path[i][1]][bunnies - 1]) <= time_limit:
            found = True
            break
        elif cost <= time_limit:
            if path[i][1] == bunnies:
                found = True
                break
    if not found:
        return []
    pathLength = i

    # Try adding missing vertices in the path and check if we can still meet
    # the target.
    missing = [x for x in range(bunnies) if x not in visited]
    for bunny in missing:
        for i in range(1, pathLength):
            middle = path[i - 1][1]
            if bunny < middle:
                start = path[i - 1][0]
                end = path[i][1]
                oldCost = times[start][middle] + times[middle][end]
                newCost = times[start][bunny] + times[bunny][end]
                if (costList[pathLength] + newCost - oldCost) <= time_limit:
                    path[i - 1][1] = bunny
                    path[i][0] = bunny

    savedBunnies = set()
    for j in range(i + 1):
        savedBunnies.add(path[j][1])
    if 0 in savedBunnies:
        savedBunnies.remove(0)
    if (bunnies - 1) in savedBunnies:
        savedBunnies.remove(bunnies - 1)
    saved = [(x - 1) for x in savedBunnies]
    return saved

# Start from the edge with the minimum cost and grow on both sides till 0 and n
# is reached. Use one level of lookahead on both sides to pick the edge with the
# probable minimum path cost.
def answerGreedyMin(times, time_limit):
    bunnies = len(times)
    minimum = 1000
    head = 10
    tail = 10
    for i, row in enumerate(times):
        for j, value in enumerate(row):
            if i != j:
                if value < minimum:
                    minimum = value
                    head = i
                    tail = j
    alreadyUsed = {}
    path = []
    path.append([head, tail])
    key = "%d,%d" % (head, tail)
    alreadyUsed[key] = bunnies
    lookAheadMin = 0
    visited = set()
    visited.add(head)
    visited.add(tail)
    while True:
        minHead = 1000000
        minTail = 1000000
        nextHead = -1
        nextTail = -1
        search = [x for x in range(bunnies) if x not in visited]
        search += [x for x in visited]
        for i in search:
            if (head != 0) and (head != i):
                key = "%d,%d" % (i, head)
                if (key not in alreadyUsed) or ((times[i][head] <= 0) and \
                        (alreadyUsed[key] < bunnies)):
                    lookBackMin = getLookBack(i, times, alreadyUsed)
                    lookCost = times[i][head] + lookBackMin
                    if lookCost < minHead:
                        minHead = lookCost
                        nextHead = i
                    if lookCost == minHead:
                        if times[i][head] < times[nextHead][head]:
                            nextHead = i
            if (tail != (bunnies - 1)) and (tail != i):
                key = "%d,%d" % (tail, i)
                if (key not in alreadyUsed) or ((times[tail][i] <= 0) and \
                        (alreadyUsed[key] < bunnies)):
                    lookAheadMin = getLookAhead(i, times, alreadyUsed)
                    lookCost = times[tail][i] + lookAheadMin
                    if lookCost < minTail:
                        minTail = lookCost
                        nextTail = i
                    if lookCost == minTail:
                        if times[tail][i] < times[tail][nextTail]:
                            nextTail = i
        if (nextHead == -1) and (nextTail == -1):
            break
        if nextHead != -1:
            path.insert(0, [nextHead, head])
            visited.add(nextHead)
            key = "%d,%d" % (nextHead, head)
            if key in alreadyUsed:
                alreadyUsed[key] += 1
            else:
                alreadyUsed[key] = 1
            head = nextHead
        if nextTail != -1:
            path.append([tail, nextTail])
            visited.add(nextTail)
            key = "%d,%d" % (tail, nextTail)
            if key in alreadyUsed:
                alreadyUsed[key] += 1
            else:
                alreadyUsed[key] = 1
            tail = nextTail
    totalCost = 0
    costList = []
    for edge in path:
        totalCost += times[edge[0]][edge[1]]
        costList.append(totalCost)

    found = False
    for i, cost in reversed(list(enumerate(costList))):
        if (cost + times[path[i][1]][bunnies - 1]) <= time_limit:
            found = True
            break
        elif cost <= time_limit:
            if path[i][1] == bunnies:
                found = True
                break
    if not found:
        return []

    pathLength = i

    visitedCount = {}
    savedBunnies = set()
    savedBunnies.add(path[0][0])
    savedBunnies.add(path[0][1])
    visitedCount[path[0][0]] = 1
    visitedCount[path[0][1]] = 1
    visitedTwice = False
    for j in range(1, pathLength + 1):
        savedBunnies.add(path[j][1])
        if path[j][1] in visitedCount:
            visitedCount[path[j][1]] += 1
            visitedTwice = True
        else:
            visitedCount[path[j][1]] = 1
    # TODO Try adding missing vertices

    # Try replacing vertices which are visited twice with the vertices which
    # have not been visited once.
    if visitedTwice:
        missing = [x for x in range(bunnies) if x not in visited]
        for bunny in missing:
            for i in range(1, pathLength):
                if 2 <= visitedCount[path[i][0]]:
                    start = path[i - 1][0]
                    middle = path[i - 1][1]
                    end = path[i][1]
                    oldCost = times[start][middle] + times[middle][end]
                    newCost = times[start][bunny] + times[bunny][end]
                    if (costList[pathLength] + newCost - oldCost) <= time_limit:
                        path[i - 1][1] = bunny
                        path[i][0] = bunny
    totalCost = 0
    costList = []
    for edge in path:
        totalCost += times[edge[0]][edge[1]]
        costList.append(totalCost)

    found = False
    for i, cost in reversed(list(enumerate(costList))):
        if (cost + times[path[i][1]][bunnies - 1]) <= time_limit:
            found = True
            break
        elif cost <= time_limit:
            if path[i][1] == bunnies:
                found = True
                break
    if not found:
        return []

    pathLength = i

    savedBunnies = set()
    savedBunnies.add(path[0][1])
    for j in range(1, pathLength):
        savedBunnies.add(path[j][1])
    if 0 in savedBunnies:
        savedBunnies.remove(0)
    if (bunnies - 1) in savedBunnies:
        savedBunnies.remove(bunnies - 1)
    saved = [(x - 1) for x in savedBunnies]
    return saved

if __name__ == "__main__":
    answer([\
            [0, 1, 1, 1, 1], \
            [1, 0, 1, 1, 1], \
            [1, 1, 0, 1, 1], \
            [1, 1, 1, 0, 1], \
            [1, 1, 1, 1, 0]], 3)
    # [0, 1]

    answer([\
            [0, 2, 2, 2, -1], \
            [9, 0, 2, 2, -1], \
            [9, 3, 0, 2, -1], \
            [9, 3, 2, 0, -1], \
            [9, 3, 2, 2, 0]], 1)
    # [1, 2]

    # Negative cycle of length 2
    answer([\
            [0, 3, 3, 3, 3, 3, 3], \
            [3, 0,-2, 3, 3, 3, 3], \
            [3, 1, 0, 3, 3, 3, 3], \
            [3, 3, 3, 0, 3, 3, 3], \
            [3, 3, 3, 3, 0, 3, 3], \
            [3, 3, 3, 3, 3, 0, 3], \
            [3, 3, 3, 3, 3, 3, 0]], 1)
    # [0, 1, 2, 3, 4]

    # Negative cycle of length 3
    answer([\
            [0, 5, 5, 5, 5, 5, 5], \
            [5, 0,-3, 5, 5, 5, 5], \
            [5, 5, 0, 1, 5, 5, 5], \
            [5, 1, 5, 0, 5, 5, 5], \
            [5, 5, 5, 5, 0, 5, 5], \
            [5, 5, 5, 0, 5, 0, 5], \
            [5, 5, 5, 5, 5, 5, 0]], 1)
    # [0, 1, 2, 3, 4]

    # Can not save any bunnies
    answer([\
            [0, 1, 2, 2, 2], \
            [9, 0, 9, 9, 9], \
            [1, 1, 0, 1, 1], \
            [1, 1, 1, 0, 1], \
            [1, 1, 1, 1, 0]], 1)
    # []

    # Lookahead useful
    answer([\
            [0, 1, 2, 2, 2], \
            [9, 0, 9, 9, 9], \
            [1, 1, 0, 1, 1], \
            [1, 1, 1, 0, 1], \
            [1, 1, 1, 1, 0]], 10)
    # [1, 2]

    answer([\
            [0, 1, 2, 2, 2], \
            [9, 0, 9, 9, 9], \
            [1, 1, 0, 1, 1], \
            [1, 1, 1, 0, 1], \
            [2, 1, 2, 2, 0]], 10)
    # [1, 2]

    # Lookahead of one is sufficient in this case.
    answer([\
            [0, 1, 2, 2, 2, 2, 2], \
            [2, 0, 1, 2, 2, 2, 2], \
            [9, 9, 0, 9, 9, 9, 9], \
            [1, 1, 1, 0, 1, 1, 1], \
            [1, 1, 1, 1, 0, 1, 1], \
            [1, 1, 1, 1, 1, 0, 1], \
            [1, 1, 1, 1, 1, 1, 0]], 8)
    # [0, 2, 3, 4]

    # Repeat visiting (0,4) helpful even if we don't have a negative cycle.
    answer([\
            [0, 1, 1, 1,-1], \
            [1, 0, 1, 1, 1], \
            [1, 1, 0, 1, 1], \
            [1, 1, 1, 0, 1], \
            [1, 1, 1, 1, 0]], 2)
    # [0, 1, 2]

    # All zeros!
    answer([\
            [0, 0, 0, 0, 0], \
            [0, 0, 0, 0, 0], \
            [0, 0, 0, 0, 0], \
            [0, 0, 0, 0, 0], \
            [0, 0, 0, 0, 0]], 0)
    # [0, 1, 2]

    # Negative cycle with a positive cost in between. Greedy negative cycle
    # search would not work in this case.
    answer([\
            [0, 2, 2, 2, 2, 2, 2], \
            [2, 0,-1, 2, 2, 2, 2], \
            [2, 2, 0,-1, 2, 2, 2], \
            [2, 2, 2, 0, 2, 2, 2], \
            [2, 2, 2, 2, 0,-1, 2], \
            [2, 2, 2, 2, 2, 0, 2], \
            [2,-1, 2, 2, 2, 2, 0]], 1)
    # [0, 1, 2, 3, 4]

    # This case starting from minimum cost edge works better than starting from
    # 0 as one circuitous path saves all bunnies. Starting from 0 with greedy
    # algorithm with one look ahead is not that helpful.
    answer([\
            [0, 2, 2,19, 2, 2, 2], \
            [9, 0, 2,19, 9, 9, 1], \
            [9, 3, 0,19, 8, 9, 9], \
            [2, 2,-9, 0, 2, 2, 2], \
            [2, 2, 2, 3, 0, 2, 2], \
            [2, 2, 2,19, 3, 0, 2], \
            [2, 2, 2,19, 2, 2, 0]], 3)
    # 0 -> 5 -> 4 -> 3 -> 2 -> 1 -> 6
    # 2 + 3 + 3 - 9 + 3 + 1 = 3
    # [0, 1, 2, 3, 4]

    # TODO
    # We could have a case where the largest negative number is not on the path
    # as it is blocked by higher positive numbers from all sides.
