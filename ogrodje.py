from igra import Igra

i = Igra()

while i.running:
    i.playing = True
    i.game_loop()