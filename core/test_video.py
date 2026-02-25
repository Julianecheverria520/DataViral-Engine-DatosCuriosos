from moviepy.editor import ColorClip

clip = ColorClip(size=(720,1280), color=(255,0,0))
clip = clip.set_duration(3)
clip.write_videofile("test.mp4", fps=24)