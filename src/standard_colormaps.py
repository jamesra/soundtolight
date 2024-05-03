from colormap import ColorMap

default_graph_cutoffs = (0.03, 0.2, 0.4, 0.6, .8, 1.0)
default_waterfall_cutoffs = (0.05, 0.20, 0.40, 0.60, .8, 1.0)
default_basic_cutoffs = (0.1, 0.30, 0.50, 0.70, .85, 1.0)

default_colors = ((0, 0, 0), #Red, Green, Blue weights for each range
                  (0.2, 0, 0),
                  (0, 0.2, 0),
                  (0.4, 0.4, 0),
                  (0, 0.6, 0.6),
                  (1, 1, 1))

green_colors = ((0, 0, 0), #Red, Green, Blue weights for each range
                (0, .5, 0),
                (.15, .6, .15),
                (.30, .7, .30),
                (.55, .85, .55),
                (0.95, 1, 0.95))

red_colors = ((0, 0, 0), #Red, Green, Blue weights for each range
              (1, .1,  .1),
              (1, .3,  .3),
              (1, .5,  .5),
              (0.8, .6,  .9),
              (0.9, 0.7, 1))

blue_colors = ((0, 0, 0), #Red, Green, Blue weights for each range
               (.1,  .1,  1),
               (.3,  .3,  1),
               (.5,  .5,  1),
               (.7,  .7,  1),
               (0.9, 0.9, 1))

purple_colors = ((0, 0, 0), #Red, Green, Blue weights for each range
               (0.5,  0,  0.5),
               (0.6,  .2,  0.6),
               (0.75,  .4,  0.75),
               (0.9,  .6,  0.9),
               (1, 0.8, 1))


waterfall_base_color = ((0, 0, 0), #Red, Green, Blue weights for each range
                      (.25, 0, 0),
                      (0, .25, 0),
                      (.5, .5, 0),
                      (0, .75, .75),
                      (1, 1, 1))

default_waterfall_colormap = ColorMap(waterfall_base_color, default_waterfall_cutoffs)
default_colormap = ColorMap(default_colors, default_graph_cutoffs)