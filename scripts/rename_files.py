import os


i = 0
for file in os.listdir(os.path.join('PNG')):
    destination = os.path.join('PNG', str(i) + '.png')
    source = os.path.join('PNG', file)
    os.rename(source, destination)
    i += 1