import pymunk

class Box:
    def __init__(self, height: int, width :int):
        self.height = height
        self.width = width

    def create(self):
        # Make the rigid Body
        body = pymunk.Body(mass=1, moment=10)
        body.position = (1280 // 2, 720 // 2)

        # Create a Box
        box = pymunk.Poly.create_box(body, (self.height, self.width))

        return body, box