import pyglet
from pyglet.gl import *


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
        uniform sampler2D tex0;
        uniform sampler2D tex1;
        uniform sampler2D tex2;
        uniform sampler2D tex3;
        uniform sampler2D tex4;
        uniform sampler2D tex5;
        uniform sampler2D map;
        out vec4 fragColor;


        #define SX 640
        #define SY 360
        #define FIX_NX 0.0015625 // 1/SX
        #define FIX_NY 0.002777777777777778 // 1/SY
        #define TEX_AMM_X 10 // SX/64
        #define TEX_AMM_Y 5.625 // SY/64
        #define MAP_SIZE_X 389
        #define MAP_SIZE_Y 891

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

        float waterMask(float maskPixel, vec2 n_position){
            vec2 map_position = vec2((n_position.x*SX+(sin(n_position.y*SY*0.0625))*8)/(MAP_SIZE_X*128), ((n_position.y*SY+(cos(n_position.x*SX*0.0625))*8)/(MAP_SIZE_Y*128)));
            if(texture(map, map_position).r < 0.5){
                return -1;
            }
            return maskPixel;
        }

        void main(){
            vec2 position = cam_coords.xy+texture_coords.xy;
            vec2 n_position = vec2(position.x - mod(position.x, FIX_NX), position.y - mod(position.y, FIX_NY));
            float maskPixel = perlin(n_position, 0.015625, 1)+0.3333333333333334;
            float darkenPixel1 = perlin(n_position, 5, 1)*0.0625;
            //fragColor = vec4(maskPixel);
            //fragColor.a = 1.0;
            vec2 texPosition = vec2(mod(n_position.x, 1)*TEX_AMM_X, mod(n_position.y, 1)*TEX_AMM_Y);
            vec4 baseColor = vec4(0, 0, 0, 0);
            maskPixel = waterMask(maskPixel, n_position);
            if(maskPixel < -0.6666666666666666){
                baseColor = texture(tex0, texPosition);
            }
            else if(maskPixel < -0.3333333333333333){
                baseColor = texture(tex1, texPosition);
            }
            else if(maskPixel < 0){
                baseColor = texture(tex2, texPosition);
            }
            else if(maskPixel < 0.3333333333333333){
                baseColor = texture(tex3, texPosition);
            }
            else if(maskPixel < 0.6666666666666666){
                baseColor = texture(tex4, texPosition);
            }
            else{
                baseColor = texture(tex5, texPosition);
            }
            fragColor = vec4(baseColor.r+darkenPixel1*baseColor.r, baseColor.g+darkenPixel1*baseColor.r, baseColor.b+darkenPixel1*baseColor.r, baseColor.a);
        }
"""


class WorldGenGroup(pyglet.graphics.Group):
    def __init__(self, size_x, size_y, textures, map_texture, shaderprogram):
        super().__init__()
        self.textures = textures
        self.map_texture = map_texture
        self.program = shaderprogram
        self.cam_x = 0
        self.cam_y = 0
        self._SIZE_X = size_x
        self._SIZE_Y = size_y

    def pixel_to_screen(self, x, y):
        return x/self._SIZE_X, y/self._SIZE_Y

    def update(self, cam_x, cam_y):
        self.cam_x, self.cam_y = self.pixel_to_screen(cam_x, cam_y)

    def set_state(self):
        self.program.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.map_texture.target, self.map_texture.id)
        glTexParameteri(self.map_texture.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(self.map_texture.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(self.textures[0].target, self.textures[0].id)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(self.textures[1].target, self.textures[1].id)
        glActiveTexture(GL_TEXTURE3)
        glBindTexture(self.textures[2].target, self.textures[2].id)
        glActiveTexture(GL_TEXTURE4)
        glBindTexture(self.textures[3].target, self.textures[3].id)
        glActiveTexture(GL_TEXTURE5)
        glBindTexture(self.textures[4].target, self.textures[4].id)
        glActiveTexture(GL_TEXTURE6)
        glBindTexture(self.textures[5].target, self.textures[5].id)
        self.program["cam_coords"] = [self.cam_x, self.cam_y]
        print(self.program["cam_coords"])
        #self.program["mask"] = self.mask.id
        #self.program["map"] = self.map_texture.id
        self.program["tex0"] = self.textures[0].id
        self.program["tex1"] = self.textures[1].id
        self.program["tex2"] = self.textures[2].id
        self.program["tex3"] = self.textures[3].id
        self.program["tex4"] = self.textures[4].id
        self.program["tex5"] = self.textures[5].id
        #self.program["tex2"] = self.tex2.id

    def unset_state(self):
        self.program.stop()


class WorldGen:
    def __init__(self, scale, size_x, size_y):
        mape = pyglet.image.load("map/map_rough.png")
        tiles = (pyglet.image.load("img/tiles/eau.png"),
                 pyglet.image.load("img/tiles/0.png"),
                 pyglet.image.load("img/tiles/1.png"),
                 pyglet.image.load("img/tiles/2.png"),
                 pyglet.image.load("img/tiles/3.png"),
                 pyglet.image.load("img/tiles/4.png"))
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.textures = tuple([tile.get_texture() for tile in tiles])
        self.map_texture = mape.get_texture()
        self.batch = pyglet.graphics.Batch()
        self.group = WorldGenGroup(self._SIZE_X, self._SIZE_Y, self.textures, self.map_texture, pyglet.gl.current_context.create_program((vertex_source, 'vertex'), (fragment_source, 'fragment')))
        self.vertex_list = self.group.program.vertex_list_indexed(4, GL_TRIANGLES, (0, 1, 2, 0, 2, 3), self.batch, self.group, position=('f', (0, 0, self._SIZE_X, 0, self._SIZE_X, self._SIZE_Y, 0, self._SIZE_Y)), tex_coords=('f', self.group.textures[0].tex_coords))
