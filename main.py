import pygame
import numpy as np
import math
import random


WIDTH = 1920
HEIGHT = 1080


pygame.init()

pygame.display.set_caption("Test")
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

line = [
    [-100, 100, 100, 100, (255, 0, 0)],
    [100, 100, 100, -100, (0, 255, 0)],
    [100, -100, -100, -100, (0, 0, 255)],
    [-100, -100, -100, 100, (255, 0, 255)],
]

wallHeights = [random.randint(50, 100) for i in range(5)]

playerPos = [0, 0]

angle = 0

cameraElevation = 50
cameraLength = 100

playerHeight = cameraElevation + (cameraLength / 2)
cameraCentre = cameraElevation

playerSpeed = 150
angularVel = math.pi / 3

hFOV = math.radians(90)
vFOV = math.radians(60)

nw = (WIDTH / 2) / math.tan(hFOV / 2)
nh = (HEIGHT / 2) / math.tan(vFOV / 2)

viewRaysDirVecs = (
    (math.cos((math.pi / 2) - hFOV / 2), math.sin((math.pi / 2) - hFOV / 2)),
    (-math.cos((math.pi / 2) - hFOV / 2), math.sin((math.pi / 2) - hFOV / 2)),
)


n = WIDTH / 2

worldToScreen = np.array([[1, 0, WIDTH / 1], [0, -1, HEIGHT / 2], [0, 0, 1]])


def transformed(coords):

    return (
        coords[0] + pygame.display.get_surface().get_size()[0] / 2,
        -coords[1] + pygame.display.get_surface().get_size()[1] / 2,
    )


def secondScreenTransformed(coords):
    return (
        coords[0] + pygame.display.get_surface().get_size()[0] / 2,
        -coords[1] + pygame.display.get_surface().get_size()[1] / 2,
    )


def relativeCoords(x, y, pos, angle):
    translated = (x - pos[0], y - pos[1])

    rotated = (
        translated[0] * math.sin(angle) - translated[1] * math.cos(angle),
        translated[0] * math.cos(angle) + translated[1] * math.sin(angle),
    )
    return rotated


def perspectiveProjection(coords):

    if not coords[1]:
        return transformed((WIDTH / 2, 0))

    return transformed((nw * coords[0] / coords[1], 0))


def pointHeight(point, absoluteHeight):
    z = math.sqrt((point[0]) ** 2 + (point[1]) ** 2)

    if z == 0:
        return (HEIGHT / 2, -HEIGHT / 2)

    YUp = (nh * (absoluteHeight - (cameraElevation))) / (
        z * math.cos(math.atan2(point[0], point[1]))
    )
    YDown = (nh * cameraElevation) / (z * math.cos(math.atan2(point[0], point[1])))

    return (YUp, YDown)


def cross(v, w):
    return (v[0] * w[1]) - (v[1] * w[0])


def calculateIntersection(p1, p2, r):

    magnitude = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    wallDirVec = ((p2[0] - p1[0]), (p2[1] - p1[1]))

    denominator = cross(r, wallDirVec)
    numerator = cross(p1, r)

    if denominator == 0:
        return False

    u = numerator / denominator

    if u >= 0 and u <= 1:
        return (p1[0] + (u * wallDirVec[0]), p1[1] + (u * wallDirVec[1]))

    return False


def lerp(p1, p2, x):

    if p1[0] == p2[0]:
        return max(p1[1], p2[1])

    return p1[1] + ((x - p1[0]) * ((p2[1] - p1[1]) / (p2[0] - p1[0])))


def generatePoints(p1, p2, absoluteHeight):

    if p1[1] <= 0 and p2[1] <= 0:
        return None

    inter1 = calculateIntersection(p1, p2, viewRaysDirVecs[0])
    inter2 = calculateIntersection(p1, p2, viewRaysDirVecs[1])

    hBound1 = p1[1] * math.tan((math.pi / 2) - hFOV / 2)
    hBound2 = p2[1] * math.tan((math.pi / 2) - hFOV / 2)

    p1Copy = p1
    p2Copy = p2

    # if inter1 and inter1[1] > 0:
    #    if p1[0] > hBound1:
    #        p1 = inter1

    #    elif p2[0] > hBound2:
    #        p2 = inter1

    # if inter2 and inter2[1] > 0:
    #    if p1[0] < -hBound1:
    #        p2 = inter2

    #    elif p2[0] < -hBound2:
    #        p1 = inter2

    # if inter1 and inter1[1] <= 0 and inter2 and inter2[1] <= 0:
    #    return None

    if (p1[0] > hBound1 and p2[0] > hBound2) or (p1[0] < -hBound1 and p2[0] < -hBound2):
        return None

    if inter1 and (not inter2 or inter2[1] <= 0) and inter1[1] >= 0:

        if p1[0] <= hBound1:
            p2 = inter1

        elif p2[0] <= hBound2:
            p1 = inter1

    elif inter2 and (not inter1 or inter1[1] <= 0) and inter2[1] >= 0:
        if p1[0] >= -hBound1:
            p2 = inter2

        elif p2[0] >= -hBound2:
            p1 = inter2

    elif inter2 and inter1 and inter1[1] >= 0 and inter2[1] >= 0:
        if p1[0] < hBound1:
            p1 = inter2

        elif p1[0] > -hBound1:
            p1 = inter1

        if p2[0] < hBound2:
            p2 = inter2

        elif p2[0] > -hBound2:
            p2 = inter1

    elif inter2 and inter1 and inter1[1] <= 0 and inter2[1] <= 0:
        return None

    offset = []

    offset.append(pointHeight(p1, absoluteHeight))
    offset.append(pointHeight(p2, absoluteHeight))

    wallPoints = [None] * 4

    wallPoints[0] = (perspectiveProjection(p1)[0], transformed((0, offset[0][0]))[1])
    wallPoints[1] = (perspectiveProjection(p1)[0], transformed((0, -offset[0][1]))[1])
    wallPoints[2] = (perspectiveProjection(p2)[0], transformed((0, offset[1][0]))[1])
    wallPoints[3] = (perspectiveProjection(p2)[0], transformed((0, -offset[1][1]))[1])

    return wallPoints


getTicksLastFrame = 0

clock = pygame.time.Clock()

running = True

points = None

while running:

    WIDTH = pygame.display.get_surface().get_size()[0]
    HEIGHT = pygame.display.get_surface().get_size()[1]

    t = pygame.time.get_ticks()

    dt = (t - getTicksLastFrame) / 1000

    getTicksLastFrame = t

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False

        if i.type == pygame.MOUSEBUTTONUP:
            print(points)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        playerPos[0] += playerSpeed * math.cos(angle) * dt
        playerPos[1] += playerSpeed * math.sin(angle) * dt

    if keys[pygame.K_s]:
        playerPos[0] -= playerSpeed * math.cos(angle) * dt
        playerPos[1] -= playerSpeed * math.sin(angle) * dt

    if keys[pygame.K_d]:
        playerPos[0] += playerSpeed * math.cos(angle - (math.pi / 2)) * dt
        playerPos[1] += playerSpeed * math.sin(angle - (math.pi / 2)) * dt

    if keys[pygame.K_a]:
        playerPos[0] -= playerSpeed * math.cos(angle - (math.pi / 2)) * dt
        playerPos[1] -= playerSpeed * math.sin(angle - (math.pi / 2)) * dt

    if keys[pygame.K_LEFT]:
        angle += angularVel * dt

    if keys[pygame.K_RIGHT]:
        angle -= angularVel * dt

    size = pygame.display.get_surface().get_size()

    window.fill((0, 0, 0))

    white = (255, 255, 255)

    for i in line:
        points = generatePoints(
            relativeCoords(i[0], i[1], playerPos, angle),
            relativeCoords(i[2], i[3], playerPos, angle),
            100,
        )

        if points != None:
            pygame.draw.line(window, white, points[0], points[1])
            pygame.draw.line(window, white, points[2], points[3])
            pygame.draw.line(window, white, points[0], points[2])
            pygame.draw.line(window, white, points[1], points[3])

            stepSize = 1

            xDiff = int(points[2][0]) - int(points[0][0])

            if xDiff:
                sign = xDiff / math.fabs(xDiff)

                for j in range(
                    int(math.fabs((xDiff) / stepSize)) + 1
                ):
                    
                    currentX = int(points[0][0]) + (stepSize * j * sign)

                    upperPoint = (currentX, lerp(points[0], points[2], currentX))
                    lowerPoint = (currentX, lerp(points[1], points[3], currentX))

                    pygame.draw.line(window, i[4], upperPoint, lowerPoint, stepSize)
                    pygame.draw.line(window, (99, 98, 105), upperPoint, (currentX, 0), stepSize)
                    pygame.draw.line(window, (42, 31, 194), lowerPoint, (currentX, HEIGHT), stepSize)

    # pygame.draw.line(
    #    window,
    #    white,
    #    secondScreenTransformed(relativeCoords(i[0], i[1], playerPos, angle)),
    #    secondScreenTransformed(relativeCoords(i[2], i[3], playerPos, angle)),
    # )

    # pygame.draw.line(
    #    window,
    #    (255, 0, 0),
    #    secondScreenTransformed((0, 0)),
    #    secondScreenTransformed((0, 15)),
    # )
    # pygame.draw.circle(window, (0, 255, 0), secondScreenTransformed((0, 0)), 5)

    pygame.draw.circle(window, (71, 70, 73), transformed((0, 0)), 3)

    pygame.display.update()
    clock.tick(60)
