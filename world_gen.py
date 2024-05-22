"""
Module contenant les classes et fonctions liées à la génération du monde.
"""

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

# Shader principale de la génération du monde
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
        uniform vec2 car_screen_pos;
        uniform float car_angle;
        uniform float time_of_day;
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

        #define HEADLIGHTRANGE 0.8862269254527579

        #define M_PI 3.14159265358979323846
        #define EPSILON 1e-10

        float rand(vec2 co){return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);}
        float rand (vec2 co, float l) {return rand(vec2(rand(co), l));}
        float rand (vec2 co, float l, float t) {return rand(vec2(rand(co, l), t));}
        float saturate(float v) { return clamp(v, 0.0,       1.0);       }
        vec2  saturate(vec2  v) { return clamp(v, vec2(0.0), vec2(1.0)); }
        vec3  saturate(vec3  v) { return clamp(v, vec3(0.0), vec3(1.0)); }
        vec4  saturate(vec4  v) { return clamp(v, vec4(0.0), vec4(1.0)); }

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
            vec2 map_position = vec2((position.x*SX+(sin(position.y*SY*0.0625))*8)/(MAP_SIZE_X*256), ((position.y*SY+(cos(position.x*SX*0.0625))*8)/(MAP_SIZE_Y*256)));
            return int(round(texture(map, map_position).r*6));
        }

        vec3 ColorTemperatureToRGB(float temperatureInKelvins)
        {
            vec3 retColor;

            temperatureInKelvins = clamp(temperatureInKelvins, 1000.0, 40000.0) / 100.0;

            if (temperatureInKelvins <= 66.0)
            {
                retColor.r = 1.0;
                retColor.g = saturate(0.39008157876901960784 * log(temperatureInKelvins) - 0.63184144378862745098);
            }
            else
            {
                float t = temperatureInKelvins - 60.0;
                retColor.r = saturate(1.29293618606274509804 * pow(t, -0.1332047592));
                retColor.g = saturate(1.12989086089529411765 * pow(t, -0.0755148492));
            }

            if (temperatureInKelvins >= 66.0)
                retColor.b = 1.0;
            else if(temperatureInKelvins <= 19.0)
                retColor.b = 0.0;
            else
                retColor.b = saturate(0.54320678911019607843 * log(temperatureInKelvins - 10.0) - 1.19625408914);

            return retColor;
        }

        float Luminance(vec3 color)
        {
            float fmin = min(min(color.r, color.g), color.b);
            float fmax = max(max(color.r, color.g), color.b);
            return (fmax + fmin) / 2.0;
        }

        vec3 HUEtoRGB(float H)
        {
            float R = abs(H * 6.0 - 3.0) - 1.0;
            float G = 2.0 - abs(H * 6.0 - 2.0);
            float B = 2.0 - abs(H * 6.0 - 4.0);
            return saturate(vec3(R,G,B));
        }

        vec3 RGBtoHCV(vec3 RGB)
        {
            // Based on work by Sam Hocevar and Emil Persson
            vec4 P = (RGB.g < RGB.b) ? vec4(RGB.bg, -1.0, 2.0/3.0) : vec4(RGB.gb, 0.0, -1.0/3.0);
            vec4 Q = (RGB.r < P.x) ? vec4(P.xyw, RGB.r) : vec4(RGB.r, P.yzx);
            float C = Q.x - min(Q.w, Q.y);
            float H = abs((Q.w - Q.y) / (6.0 * C + EPSILON) + Q.z);
            return vec3(H, C, Q.x);
        }

        vec3 RGBtoHSL(vec3 RGB)
        {
            vec3 HCV = RGBtoHCV(RGB);
            float L = HCV.z - HCV.y * 0.5;
            float S = HCV.y / (1.0 - abs(L * 2.0 - 1.0) + EPSILON);
            return vec3(HCV.x, S, L);
        }

        vec3 HSLtoRGB(in vec3 HSL)
        {
            vec3 RGB = HUEtoRGB(HSL.x);
            float C = (1.0 - abs(2.0 * HSL.z - 1.0)) * HSL.y;
            return (RGB - 0.5) * C + vec3(HSL.z);
        }

        bool point_inside_trigon(vec2 s, vec2 a, vec2 b, vec2 c)
        {
            float as_x = s.x - a.x;
            float as_y = s.y - a.y;

            bool s_ab = (b.x - a.x) * as_y - (b.y - a.y) * as_x > 0;

            if ((c.x - a.x) * as_y - (c.y - a.y) * as_x > 0 == s_ab) 
                return false;
            if ((c.x - b.x) * (s.y - b.y) - (c.y - b.y)*(s.x - b.x) > 0 != s_ab) 
                return false;
            return true;
        }

        vec2 vec_from_angle(float angle){
            return vec2(cos(angle), sin(angle));
        }

        float heat_from_time_of_day(float time_of_day){
            return 2000 + abs(sin((M_PI/720)*time_of_day))*4500;
        }

        float luminance_from_time_of_day(float time_of_day){
            if(time_of_day >= 750){
                return 0.4;
            }
            return 0.4 - sin((M_PI/720)*time_of_day)*0.4;
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
            vec3 original = vec3(baseColor.r+darkenPixel1*baseColor.r, baseColor.g+darkenPixel1*baseColor.r, baseColor.b+darkenPixel1*baseColor.r);
            vec3 colorTempRGB = ColorTemperatureToRGB(heat_from_time_of_day(time_of_day));

            float finalLuminance = Luminance(original);
            vec3 blended = mix(original, original * colorTempRGB, 1);
            vec3 resultHSL = RGBtoHSL(blended);
            vec2 direction_b = vec_from_angle(car_angle+HEADLIGHTRANGE);
            direction_b.x *= 2.25;
            direction_b.y *= 4;
            vec2 direction_c = vec_from_angle(car_angle-HEADLIGHTRANGE);
            direction_c.x *= 2.25;
            direction_c.y *= 4;
            vec2 point_b = car_screen_pos+direction_b;
            vec2 point_c = car_screen_pos+direction_c;
            if(!point_inside_trigon(texture_coords.xy, car_screen_pos, point_b, point_c)){
                finalLuminance -= luminance_from_time_of_day(time_of_day);
            }
            else{
                float distance_from_point = sqrt(pow(car_screen_pos.x-texture_coords.x, 2) + pow(car_screen_pos.y-texture_coords.y, 2));
                finalLuminance -= luminance_from_time_of_day(time_of_day)*min((distance_from_point), 1);
            }

            vec3 luminancePreservedRGB = HSLtoRGB(vec3(resultHSL.x, resultHSL.y, finalLuminance));        

            fragColor = vec4(mix(blended, luminancePreservedRGB, 0.75), alpha);
            // fragColor = vec4(baseColor.r+darkenPixel1*baseColor.r, baseColor.g+darkenPixel1*baseColor.r, baseColor.b+darkenPixel1*baseColor.r, alpha);
        }
"""


class WorldGenGroup(pyglet.graphics.Group):
    """
    Groupe de dessin pour la génération du monde.
    """
    def __init__(self, alpha, tile_offset, size_x, size_y, textures, map_texture, shaderprogram):
        """
        Initialise le groupe de dessin du monde.

        Parameters
        ----------
        alpha : float
            Transparence.
        tile_offset : int
            Décalage de la texture.
        size_x : int
            Taille en largeur.
        size_y : int
            Taille en hauteur.
        textures : tuple
            Textures des tuiles.
        map_texture : Texture
            Texture de la carte.
        shaderprogram : ShaderProgram
            Programme de shader.
        
        Returns
        -------
        None.
        """
        super().__init__()
        self.textures = textures
        self.map_texture = map_texture
        self.program = shaderprogram
        self.cam_x = 0
        self.cam_y = 0
        self.car_x = 0
        self.car_y = 0
        self.car_dir_x = 0
        self.car_dir_y = 0
        self.car_angle = 0
        self.time_of_day = 0
        self.alpha = alpha
        self.tile_offset = tile_offset
        self._SIZE_X = size_x
        self._SIZE_Y = size_y

    def pixel_to_screen(self, x, y):
        """
        Convertit les coordonnées de pixel en coordonnées d'écran.

        Parameters
        ----------
        x : int
            Coordonnée x du pixel.
        y : int
            Coordonnée y du pixel.
        
        Returns
        -------
        tuple
            Coordonnées d'écran converties.
        """
        return x/self._SIZE_X, y/self._SIZE_Y

    def pixel_pos_to_world(self, x, y):
        """
        Convertit les coordonnées de pixel en coordonnées du monde.

        Parameters
        ----------
        x : int
            Coordonnée x du pixel.
        y : int
            Coordonnée y du pixel.
        
        Returns
        -------
        tuple
            Coordonnées du monde converties.
        """
        return int((x+np.sin((y+self._SIZE_X)*0.0625)*8)/256), (-int(((y+self._SIZE_Y)+np.cos(x*0.0625)*8)/256))

    def update(self, time_of_day, cam_x, cam_y, car_x, car_y, car_angle):
        """
        Met à jour les paramètres du monde.

        Parameters
        ----------
        time_of_day : float
            Heure du jour.
        cam_x : float
            Coordonnée x de la caméra.
        cam_y : float
            Coordonnée y de la caméra.
        car_x : float
            Coordonnée x de la voiture.
        car_y : float
            Coordonnée y de la voiture.
        car_angle : float
            Angle de la voiture.
        
        Returns
        -------
        None.
        """
        self.time_of_day = time_of_day
        self.cam_x, self.cam_y = self.pixel_to_screen(cam_x, cam_y)
        self.car_x, self.car_y = self.pixel_to_screen((car_x-cam_x)+np.cos(car_angle)*16, (car_y-cam_y)+np.sin(car_angle)*16)
        self.car_angle = car_angle
        #print(self.cam_x, self.cam_y)
        #print(self.pixel_pos_to_world(cam_x, cam_y))

    def set_state(self):
        """
        Configure l'état pour le rendu.

        Returns
        -------
        None.
        """
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
        glBindTexture(self.textures[3+self.tile_offset].target, self.textures[3+self.tile_offset].id)
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
        self.program["car_screen_pos"] = [self.car_x, self.car_y]
        self.program["car_angle"] = self.car_angle
        self.program["time_of_day"] = self.time_of_day
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
        """
        Rétablit l'état après le rendu.

        Returns
        -------
        None.
        """
        self.program.stop()


class WorldGen:
    """
    Classe pour la génération du monde.
    """
    def __init__(self, scale, size_x, size_y):
        """
        Initialise la génération du monde.

        Parameters
        ----------
        scale : int
            Échelle.
        size_x : int
            Taille en largeur.
        size_y : int
            Taille en hauteur.
        
        Returns
        -------
        None.
        """
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
        self.raw_map = mape.get_image_data()
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.textures = tuple([tile.get_texture() for tile in tiles])
        self.map_texture = mape.get_texture()
        self.batch = pyglet.graphics.Batch()
        self.group = WorldGenGroup(1, 0, self._SIZE_X, self._SIZE_Y, self.textures, self.map_texture, pyglet.gl.current_context.create_program((vertex_source, 'vertex'), (fragment_source, 'fragment')))
        self.vertex_list = self.group.program.vertex_list_indexed(4, GL_TRIANGLES, (0, 1, 2, 0, 2, 3), self.batch, self.group, position=('f', (0, 0, self._SIZE_X, 0, self._SIZE_X, self._SIZE_Y, 0, self._SIZE_Y)), tex_coords=('f', self.group.textures[0].tex_coords))
