import random, os, re

from PIL import Image, ImageDraw, ImageFilter, ImageFont


class LoadFontsException(Exception):
    pass


class Captcha(object):
    """

     """
    fonts = None
    FONT_DIR = os.getcwd() + '/jobplus/tools/fonts/'
    ambig_charset = set(['1', 'l', 'I', 'J', '2', 'z', 'Z', '5', 's', 'S', '0', 'o', 'O', '9', 'g'])
    default_charset = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    colors = [
        (198, 40, 40), (173, 20, 87), (106, 27, 154), (69, 39, 160), (40, 53, 147),
        (21, 101, 192), (2, 119, 189), (0, 131, 143), (0, 105, 92), (46, 125, 50),
        (85, 139, 47), (158, 157, 36), (249, 168, 37), (255, 143, 0), (239, 108, 0),
        (216, 67, 21), (78, 52, 46), (66, 66, 66), (55, 71, 79),
    ]

    def __init__(self, font_dir=None, charset=None, ch_num=4, avoid_ambig_chars=True):
        """
        :param fonts(list): ttf 字体目录
        :param charset(str): 字符合集
        :param ch_num(int): 字符数量
        :param avoid_ambi_chars(boolean): 避免一些引起歧义的字符，比如 1 和 l, 2 和 z，5和s
         """

        self.load_fonts(font_dir)
        self.charset = set(charset) if charset else self.default_charset
        self.ch_num = ch_num
        self.avoid_ambig_chars = avoid_ambig_chars

        if self.avoid_ambig_chars:
            self.charset = self.charset - self.ambig_charset
        # print(self.charset)

    def random_word(self):
        return [random.choice(list(self.charset)) for i in range(self.ch_num)]

    def load_fonts(self, font_dir=None):
        fd = font_dir if font_dir else self.FONT_DIR
        # cwd = os.getcwd() 
        files = os.listdir(fd)
        ttfs = list(filter(lambda x: re.compile('^.*?\.(ttf|TTF|otf|OTF)$').match(x), files))
        if len(ttfs) == 0:
            raise LoadFontsException
        self.fonts = ttfs

    def gen_captcha(self, word=None):
        word = word if word else self.random_word()

        color = random.choice(self.colors)

        # 图片大小 180 x 70
        width = 180
        height = 50

        # 新建图像
        capt = Image.new('RGB', (width, height), 'white')
        # 设置字体
        fonts = [ImageFont.truetype(self.FONT_DIR + font, 40) for font in self.fonts]
        # 设置 draw 对象
        capt_draw = ImageDraw.Draw(capt)

        for i in range(self.ch_num):
            ch = word[i]

            char_img = Image.new('RGBA', (50, 50), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((0, 0),
                           text=ch,
                           fill=color,
                           font=random.choice(fonts))
            char_img = char_img.rotate(random.randint(-15, 15), expand=1)
            # char_img.show()
            capt.paste(color, box=(5 + 40 * i + random.randint(-2, 3), 3), mask=char_img)

        # 划几根干扰线
        for i in range(4):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            capt_draw.line(((x1, y1), (x2, y2)), fill=color, width=random.randint(1, 2))

        # 添加色点
        for i in range(random.randint(60, 80)):
            # point_color = random.choice(self.colors)
            x = random.randint(5, width - 5)
            y = random.randint(5, height - 5)
            capt_draw.point((x, y), fill=color)
            if random.randint(0, 3) > 0:
                capt_draw.point((x + 1, y), fill=color)
                capt_draw.point((x - 1, y), fill=color)
                capt_draw.point((x, y + 1), fill=color)
                capt_draw.point((x, y - 1), fill=color)

        for i in range(random.randint(100, 150)):
            x = random.randint(5, width - 5)
            y = random.randint(5, height - 5)
            capt_draw.point((x, y), fill=color)  # random.choice(self.colors))
        # capt = capt.filter(ImageFilter.FIND_EDGES)

        # capt.save('code.jpg', 'jpeg')

        return capt, ''.join(word).upper()


if __name__ == '__main__':
    # files = os.listdir()
    # print(files)
    # ttfs = list(filter(lambda x: re.compile('^.*?\.(ttf|TTF|otf|OTF)$').match(x), files))
    # print(ttfs)
    cpt = Captcha()
    im, w = cpt.gen_captcha()
    print(w)
    im.show()
