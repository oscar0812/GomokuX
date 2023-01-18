from src.com.oscarrtorres.gomokux.model.point import Point


class GomokuBoard:
    def __init__(self, number_of_x_chips, number_of_y_chips, cell_width, box_height, margin_x, margin_y):
        if number_of_x_chips < 5 or number_of_y_chips < 5:
            raise Exception("Minimum number of boxes is 5")

        self.number_of_x_chips = number_of_x_chips
        self.number_of_y_chips = number_of_y_chips
        self.cell_w = cell_width
        self.margin_x = margin_x
        self.cell_h = box_height
        self.margin_y = margin_y

        self.points: list[Point] = []
        self.__generate_points__()

    # array_points will have 1 more value in each row and col since we can click on the edges
    def __generate_points__(self):
        self.points = [Point(x, y, x * self.cell_w + self.margin_x, y * self.cell_h + self.margin_y)
                       for y in range(self.number_of_x_chips) for x in range(self.number_of_y_chips)]

        max_in_a_row = 5

        # calculate neighbors
        for index, point in enumerate(self.points):
            point.set_index(index)
            in_x_boundary = point.x + (max_in_a_row - 1) < self.number_of_x_chips
            in_y_boundary = point.y + (max_in_a_row - 1) < self.number_of_y_chips

            # get 5 to right
            if in_x_boundary:
                points = [self.points[index + x] for x in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

            # get 5 to the bottom
            if in_y_boundary:
                points = [self.points[index + (i * self.number_of_y_chips)] for i in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

            # diagonal \
            if in_x_boundary and in_y_boundary:
                points = [self.points[index + (i * self.number_of_y_chips) + i] for i in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

            # diagonal /
            if point.y > (max_in_a_row - 2) and in_x_boundary:
                points = [self.points[index - (i * self.number_of_x_chips - i)] for i in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]
