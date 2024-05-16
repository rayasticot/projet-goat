from PIL import Image

index = ((255, 255, 0, 255), (128, 128, 0, 255), (200, 255, 0, 255), (150, 255, 150, 255), (0, 255, 0, 255), (200, 200, 200, 255), (255, 255, 255, 255))

table = (
    # TEMP
    (3, 3, 3, 1, 1, 0, 0, 0, 0, 0), # P
    (3, 3, 3, 2, 1, 1, 1, 1, 1, 1), # R
    (3, 3, 3, 2, 1, 1, 1, 1, 1, 1), # E
    (4, 3, 3, 2, 1, 1, 1, 1, 1, 1), # C
    (4, 4, 3, 2, 1, 1, 1, 1, 1, 1), # I
    (4, 4, 4, 2, 2, 1, 1, 1, 1, 1),
    (4, 4, 4, 4, 2, 1, 1, 1, 1, 1),
    (4, 4, 4, 4, 2, 1, 1, 1, 1, 1),
    (4, 4, 4, 4, 2, 2, 2, 1, 1, 1),
    (4, 4, 4, 4, 2, 2, 2, 1, 1, 1),
)


if __name__ == "__main__":
    temp = Image.open("map/tempmap.png")
    preci = Image.open("map/precimap.png")
    final = Image.new(mode="RGBA", size=preci.size, color=(0, 0, 0, 0))

    for x in range(temp.size[0]):
        for y in range(temp.size[1]):
            if temp.getpixel((x, y))[1] == 0:
                final.putpixel((x, y), (0, 0, 255, 255))
                continue
            if 0 < x < temp.size[0]-1 and 0 < y < temp.size[1]-1:
                if not temp.getpixel((x-1, y))[1] or not temp.getpixel((x-1, y-1))[1] or not temp.getpixel((x, y-1))[1] or not temp.getpixel((x+1, y-1))[1] or not temp.getpixel((x+1, y))[1] or not temp.getpixel((x+1, y+1))[1] or not temp.getpixel((x, y+1))[1] or not temp.getpixel((x-1, y+1))[1]:
                    final.putpixel((x, y), (255, 0, 255, 255))
                    continue
            pixel_to_put = (0, 0, 0, 0)
            temp_value = int((temp.getpixel((x, y))[0]/255)*10)
            preci_value = int((preci.getpixel((x, y))[0]/255)*10)
            pixel_to_put = index[table[preci_value][temp_value]]
            final.putpixel((x, y), pixel_to_put)

    final.save("map/biome_map.png")
