import pymunk

colors = {
            'red':    (255, 0, 0, 0),
            'orange': (255, 165, 0, 0),
            'yellow': (255, 255, 0, 0),
            'green':  (0, 255, 0, 0),
            'blue':   (0, 0, 255, 0),
            'indigo': (75, 0, 130, 0),
            'purple': (128, 0, 128, 0),
            'brown':  (223, 153, 35, 0)
        }

class Box:
    def __init__(self, size: tuple, pos: tuple, color : str):
        self.size = size
        self.pos = pos
        self.color = color.lower()

        if self.color not in colors:
            raise ValueError(f"'{self.color}' is invalid. Use ROYGBIV colors or Brown.")

    def create(self):
        # Make the rigid Body
        body = pymunk.Body(mass=0.2, moment=10)
        body.position = self.pos

        # Create a Box
        box = pymunk.Poly.create_box(body, self.size)

        box.color = colors[self.color] 
        

        return body, box