import pyglet
from pyglet.gl import *

'''
fragment_source = """#version 330 core
        in vec2 texCoord;
        uniform sampler2D tex1;
        uniform sampler2D tex2;
        uniform sampler2D mask;
        out vec4 fragColor;

        void main(){
            vec4 maskPixel = texture(mask, texCoord);
            if (maskPixel.r > 0.5){
                fragColor = texture(tex1, texCoord);
            }
            else{
                fragColor = texture(tex2, texCoord);
            }
        }
"""
'''

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
        out vec4 fragColor;


        #define FIX_NX 0.003125
        #define FIX_NY 0.005555555555555556
        #define TEX_AMM_X 5
        #define TEX_AMM_Y 2.81255

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

        void main(){
            vec2 position = cam_coords.xy+texture_coords.xy;
            vec2 n_position = vec2(position.x - mod(position.x, FIX_NX), position.y - mod(position.y, FIX_NY));
            float maskPixel = perlin(n_position, 0.25, 1)+0.3333333333333334;
            //fragColor = vec4(maskPixel);
            //fragColor.a = 1.0;
            vec2 texPosition = vec2(mod(n_position.x, 1)*TEX_AMM_X, mod(n_position.y, 1)*TEX_AMM_Y);
            if(maskPixel < -0.6666666666666666){
                fragColor = texture(tex0, texPosition);
            }
            else if(maskPixel < -0.3333333333333333){
                fragColor = texture(tex1, texPosition);
            }
            else if(maskPixel < 0){
                fragColor = texture(tex2, texPosition);
            }
            else if(maskPixel < 0.3333333333333333){
                fragColor = texture(tex3, texPosition);
            }
            else if(maskPixel < 0.6666666666666666){
                fragColor = texture(tex4, texPosition);
            }
            else{
                fragColor = texture(tex5, texPosition);
            }
        }
"""


class CustomGroup(pyglet.graphics.Group):
    def __init__(self, textures, shaderprogram):
        super().__init__()
        self.textures = textures
        self.program = shaderprogram
        self.cam_x = 0
        self.cam_y = 0

    def update(self, dt):
        self.cam_x += 0.5*dt
        self.cam_y += 0.5*dt

    def set_state(self):
        self.program.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.textures[0].target, self.textures[0].id)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(self.textures[1].target, self.textures[1].id)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(self.textures[2].target, self.textures[2].id)
        glActiveTexture(GL_TEXTURE3)
        glBindTexture(self.textures[3].target, self.textures[3].id)
        glActiveTexture(GL_TEXTURE4)
        glBindTexture(self.textures[4].target, self.textures[4].id)
        glActiveTexture(GL_TEXTURE5)
        glBindTexture(self.textures[5].target, self.textures[5].id)
        self.program["cam_coords"] = [self.cam_x, self.cam_y]
        #print(self.program["cam_coords"])
        #self.program["mask"] = self.mask.id
        self.program["tex1"] = self.textures[0].id
        self.program["tex2"] = self.textures[1].id
        self.program["tex3"] = self.textures[2].id
        self.program["tex4"] = self.textures[3].id
        self.program["tex5"] = self.textures[4].id
        #self.program["tex2"] = self.tex2.id

    def unset_state(self):
        self.program.stop()


class Game(pyglet.window.Window):
    def __init__(self):
        self.SIZE_X = 320
        self.SIZE_Y = 180
        self._window_scale = 4
        self._keys = pyglet.window.key.KeyStateHandler()
        self._fps_display = pyglet.window.FPSDisplay(window=self)
        super().__init__(self.SIZE_X*self._window_scale, self.SIZE_Y*self._window_scale, caption="AAA")
        tiles = (pyglet.image.load("img/tiles/eau.png"),
                 pyglet.image.load("img/tiles/0.png"),
                 pyglet.image.load("img/tiles/1.png"),
                 pyglet.image.load("img/tiles/2.png"),
                 pyglet.image.load("img/tiles/3.png"),
                 pyglet.image.load("img/tiles/4.png"))
        self.textures = tuple([tile.get_texture() for tile in tiles])
        self.batch = pyglet.graphics.Batch()
        self.group = CustomGroup(self.textures, pyglet.gl.current_context.create_program((vertex_source, 'vertex'), (fragment_source, 'fragment')))
        self.vertex_list = self.group.program.vertex_list_indexed(4, GL_TRIANGLES, (0, 1, 2, 0, 2, 3), self.batch, self.group, position=('f', (0, 0, self.SIZE_X*self._window_scale, 0, self.SIZE_X*self._window_scale, self.SIZE_Y*self._window_scale, 0, self.SIZE_Y*self._window_scale)), tex_coords=('f', self.group.textures[0].tex_coords))
        pyglet.clock.schedule_interval(self.group.update, 1/60)

    def on_draw(self):
        self.clear()
        self.batch.draw()
        self._fps_display.draw()


if __name__ == "__main__":
    pyglet.image.Texture.default_min_filter = GL_NEAREST
    pyglet.image.Texture.default_mag_filter = GL_NEAREST
    window = Game()
    pyglet.app.run(1/200)
