import pyglet
from pyglet.gl import *
import numpy as np
import time


vertex_source = """#version 330 core
    in vec2 position;
    in vec3 tex_coords;
    out vec3 texture_coords;

    uniform WindowBlock 
    {
        mat4 projection;
        mat4 view;
    } window;  

    void main()
    {
        gl_Position = window.projection * window.view * vec4(position, 1, 1);
        texture_coords = tex_coords;
    }
"""

fragment_source = """#version 330 core
        in vec3 texture_coords;
        uniform vec2 cam_coords;
        uniform sampler2D tex_water;
        uniform sampler2D tex_tes0;
        uniform sampler2D tex_tes1;
        uniform sampler2D tex_tes2;
        uniform sampler2D tex_for0;
        uniform sampler2D tex_for1;
        uniform sampler2D tex_des0;
        uniform sampler2D tex_des1;
        uniform sampler2D tex_des2;
        uniform sampler2D tex_sec0;
        uniform sampler2D tex_sec2;
        uniform sampler2D tex_pla0;
        uniform sampler2D tex_pla2;
        /*
        uniform sampler2D tex4;
        uniform sampler2D tex5;
        */
        uniform sampler2D map;
        uniform float alpha;
        uniform float time;
        out vec4 fragColor;


        #define SX 640
        #define SY 360
        #define FIX_NX 0.0015625 // 1/SX
        #define FIX_NY 0.002777777777777778 // 1/SY
        #define WAT_AMM_X 10
        #define WAT_AMM_Y 5.625
        #define TEX_AMM_X 2.5296442687747036 // SX/TAILLEIMAGE
        #define TEX1_AMM_X 2.6122448979591835
        #define TEX2_AMM_X 2.7705627705627704
        #define TEX_AMM_Y 1.4229249011857708 // SY/TAILLEIMAGE
        #define TEX1_AMM_Y 1.469387755102041
        #define TEX2_AMM_Y 1.5584415584415585
        #define MAP_SIZE_X 1248
        #define MAP_SIZE_Y 2352

        #define M_PI 3.14159265358979323846

        float rand(vec2 co){return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);}
        float rand (vec2 co, float l) {return rand(vec2(rand(co), l));}
        float rand (vec2 co, float l, float t) {return rand(vec2(rand(co, l), t));}

        float perlin(vec2 p, float dim, float time) {
            vec2 pos = floor(p * dim);
            vec2 posx = pos + vec2(1.0, 0.0);
            vec2 posy = pos + vec2(0.0, 1.0);
            vec2 posxy = pos + vec2(1.0);

            float c = rand(pos, dim, time);
            float cx = rand(posx, dim, time);
            float cy = rand(posy, dim, time);
            float cxy = rand(posxy, dim, time);

            vec2 d = fract(p * dim);
            d = -0.5 * cos(d * M_PI) + 0.5;

            float ccx = mix(c, cx, d.x);
            float cycxy = mix(cy, cxy, d.x);
            float center = mix(ccx, cycxy, d.y);

            return center * 2.0 - 1.0;
        }

        int get_map_biome(vec2 position){
            vec2 map_position = vec2((position.x*SX+(sin(position.y*SY*0.0625))*8)/(MAP_SIZE_X*8), ((position.y*SY+(cos(position.x*SX*0.0625))*8)/(MAP_SIZE_Y*8)));
            return int(round(texture(map, map_position).r*6));
        }

        void main(){
            vec2 position = cam_coords.xy+texture_coords.xy;
            int maskPixel = get_map_biome(position);
            float darkenPixel1 = perlin(position, 5, 1)*0.0625;
            //fragColor = vec4(maskPixel);
            //fragColor.a = 1.0;
            vec2 texPosition = vec2(position.x*TEX_AMM_X, position.y*TEX_AMM_Y);
            vec2 tex1Position = vec2(position.x*TEX1_AMM_X, position.y*TEX1_AMM_Y);
            vec2 tex2Position = vec2(position.x*TEX2_AMM_X, position.y*TEX2_AMM_Y);
            vec2 texCancPosition = vec2(position.x*9.552238805970148, position.y*5.373134328358209);

            //vec2 texCancPosition = vec2((position.x+(perlin(positionTimed, 5, 1)*0.05))*9.552238805970148, (position.y+(perlin(positionTimed, 5, 1)*0.05))*5.373134328358209);
            //vec2 texCanc1Position = vec2((position.x+(perlin(positionTimed, 5, 1)*0.05))*14.883720930232558, (position.y+(perlin(positionTimed, 5, 1)*0.05))*8.372093023255815);

            vec4 baseColor = vec4(0, 0, 0, 0);
            switch(maskPixel){
                case 0:
                    vec2 positionTimed = vec2(position.x+(time*0.125), position.y+(time*0.125));
                    //texPosition = vec2((position.x+cos(positionTimed.x*8)*0.025)*TEX_AMM_X, (position.y+sin(positionTimed.x*8)*0.025)*TEX_AMM_Y);
                    texPosition = vec2((position.x+(perlin(positionTimed, 5, 1))*0.025)*WAT_AMM_X, (position.y+(perlin(positionTimed, 5, 1)*0.025))*WAT_AMM_Y);
                    baseColor = texture(tex_water, texPosition);
                    break;
                case 1:
                    baseColor = texture(tex_sec0, texPosition) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_des1, tex1Position) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_sec2, tex2Position) * vec4(0.33, 0.33, 0.33, 0.33);
                    break;
                case 2:
                    baseColor = texture(tex_des0, texPosition) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_des1, tex1Position) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_des2, tex2Position) * vec4(0.33, 0.33, 0.33, 0.33);
                    break;
                case 3:
                    baseColor = texture(tex_des0, texPosition) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_tes1, tex1Position) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_tes2, tex2Position) * vec4(0.33, 0.33, 0.33, 0.33);
                    break;
                case 4:
                    baseColor = texture(tex_tes0, texPosition) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_tes1, tex1Position) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_tes2, tex2Position) * vec4(0.33, 0.33, 0.33, 0.33);
                    break;
                case 5:
                    baseColor = texture(tex_for0, texPosition) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_for1, tex1Position) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_tes2, tex2Position) * vec4(0.33, 0.33, 0.33, 0.33);
                    break;
                case 6:
                    baseColor = texture(tex_pla0, texPosition) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_des1, tex1Position) * vec4(0.33, 0.33, 0.33, 0.33) + texture(tex_pla2, tex2Position) * vec4(0.33, 0.33, 0.33, 0.33);
                    break;
            }
            fragColor = vec4(baseColor.r+darkenPixel1*baseColor.r, baseColor.g+darkenPixel1*baseColor.r, baseColor.b+darkenPixel1*baseColor.r, alpha);
        }
"""


class WorldGenGroup(pyglet.graphics.Group):
    def __init__(self, alpha, tile_offset, size_x, size_y, textures, map_texture, shaderprogram):
        super().__init__()
        self.textures = textures
        self.map_texture = map_texture
        self.program = shaderprogram
        self.cam_x = 0
        self.cam_y = 0
        self.alpha = alpha
        self.tile_offset = tile_offset
        self._SIZE_X = size_x
        self._SIZE_Y = size_y

    def pixel_to_screen(self, x, y):
        return x/self._SIZE_X, y/self._SIZE_Y

    def pixel_pos_to_world(self, x, y):
        return int((x+np.sin((y+self._SIZE_X)*0.0625)*8)/8), (-int(((y+self._SIZE_Y)+np.cos(x*0.0625)*8)/8))

    def update(self, cam_x, cam_y):
        self.cam_x, self.cam_y = self.pixel_to_screen(cam_x, cam_y)
        print(self.cam_x, self.cam_y)
        print(self.pixel_pos_to_world(cam_x, cam_y))
        self.program["time"] = time.time()%10000

    def set_state(self):
        self.program.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.map_texture.target, self.map_texture.id)
        #glTexParameteri(self.map_texture.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        #glTexParameteri(self.map_texture.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(self.textures[0+self.tile_offset].target, self.textures[0+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(self.textures[1+self.tile_offset].target, self.textures[1+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE3)
        glBindTexture(self.textures[2+self.tile_offset].target, self.textures[2+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE4)
        glBindTexture(self.textures[3].target, self.textures[3].id)
        glActiveTexture(GL_TEXTURE5)
        glBindTexture(self.textures[4+self.tile_offset].target, self.textures[4+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE6)
        glBindTexture(self.textures[5+self.tile_offset].target, self.textures[5+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE7)
        glBindTexture(self.textures[6+self.tile_offset].target, self.textures[6+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE8)
        glBindTexture(self.textures[7+self.tile_offset].target, self.textures[7+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE9)
        glBindTexture(self.textures[8+self.tile_offset].target, self.textures[8+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE10)
        glBindTexture(self.textures[9+self.tile_offset].target, self.textures[9+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE11)
        glBindTexture(self.textures[10+self.tile_offset].target, self.textures[10+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE12)
        glBindTexture(self.textures[11+self.tile_offset].target, self.textures[11+self.tile_offset].id)
        glActiveTexture(GL_TEXTURE13)
        glBindTexture(self.textures[12+self.tile_offset].target, self.textures[12+self.tile_offset].id)
        """
        glActiveTexture(GL_TEXTURE5)
        glBindTexture(self.textures[4].target, self.textures[4].id)
        glActiveTexture(GL_TEXTURE6)
        glBindTexture(self.textures[5].target, self.textures[5].id)
        """
        self.program["alpha"] = self.alpha
        self.program["cam_coords"] = [self.cam_x, self.cam_y]
        self.program["time"] = time.time()%10000
        #print(self.program["cam_coords"])
        #self.program["mask"] = self.mask.id
        #self.program["map"] = self.map_texture.id
        self.program["tex_water"] = self.textures[0+self.tile_offset].id
        self.program["tex_tes0"] = self.textures[1+self.tile_offset].id
        self.program["tex_tes1"] = self.textures[2+self.tile_offset].id
        self.program["tex_tes2"] = self.textures[3+self.tile_offset].id
        self.program["tex_for0"] = self.textures[4+self.tile_offset].id
        self.program["tex_for1"] = self.textures[5+self.tile_offset].id
        self.program["tex_des0"] = self.textures[6+self.tile_offset].id
        self.program["tex_des1"] = self.textures[7+self.tile_offset].id
        self.program["tex_des2"] = self.textures[8+self.tile_offset].id
        self.program["tex_sec0"] = self.textures[9+self.tile_offset].id
        self.program["tex_sec2"] = self.textures[10+self.tile_offset].id
        self.program["tex_pla0"] = self.textures[11+self.tile_offset].id
        self.program["tex_pla2"] = self.textures[12+self.tile_offset].id
        """
        self.program["tex4"] = self.textures[4].id
        self.program["tex5"] = self.textures[5].id
        """
        #self.program["tex2"] = self.tex2.id

    def unset_state(self):
        self.program.stop()


class WorldGen:
    def __init__(self, scale, size_x, size_y):
        mape = pyglet.image.load("map/biome_map.png")
        tiles = (pyglet.image.load("img/tiles/eau.png"),
                 pyglet.image.load("img/tiles/tes0.png"),
                 pyglet.image.load("img/tiles/tes1.png"),
                 pyglet.image.load("img/tiles/tes2.png"),
                 pyglet.image.load("img/tiles/for0.png"),
                 pyglet.image.load("img/tiles/for1.png"),
                 pyglet.image.load("img/tiles/des0.png"),
                 pyglet.image.load("img/tiles/des1.png"),
                 pyglet.image.load("img/tiles/des2.png"),
                 pyglet.image.load("img/tiles/sec0.png"),
                 pyglet.image.load("img/tiles/sec2.png"),
                 pyglet.image.load("img/tiles/pla0.png"),
                 pyglet.image.load("img/tiles/pla2.png"))
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.textures = tuple([tile.get_texture() for tile in tiles])
        self.map_texture = mape.get_texture()
        self.batch = pyglet.graphics.Batch()
        self.group = WorldGenGroup(1, 0, self._SIZE_X, self._SIZE_Y, self.textures, self.map_texture, pyglet.gl.current_context.create_program((vertex_source, 'vertex'), (fragment_source, 'fragment')))
        self.vertex_list = self.group.program.vertex_list_indexed(4, GL_TRIANGLES, (0, 1, 2, 0, 2, 3), self.batch, self.group, position=('f', (0, 0, self._SIZE_X, 0, self._SIZE_X, self._SIZE_Y, 0, self._SIZE_Y)), tex_coords=('f', self.group.textures[0].tex_coords))
