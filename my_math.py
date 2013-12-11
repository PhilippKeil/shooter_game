def point_on_line(point, line):
        if line.x1() < line.x2() and line.x1() <= point.x() <= line.x2():
            if (line.y1() < line.y2() and line.y1() <= point.y() <= line.y2()) or\
               (line.y1() > line.y2() and line.y1 >= point.y() >= line.y2()) or\
               (line.y1() == line.y2() == point.y()):
                return True

        elif line.x1() > line.x2() and line.x1() >= point.x() >= line.x2():
            if (line.y2() < line.y1() and line.y2() <= point.y() <= line.y1()) or\
               (line.y2() > line.y1() and line.y2() >= point.y() >= line.y1()) or\
               (line.y2() == line.y1() == point.y()):
                return True

        elif line.x1() == line.x2() == point.x():
            if (line.y1() < line.y2() and line.y1() <= point.y() <= line.y2()) or\
               (line.y1() > line.y2() and line.y1() >= point.y() >= line.y2()) or\
               (line.y1() == line.y2() == point.y()):
                return True
        return False