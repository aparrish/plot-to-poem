def titleindex(filename="titles"):
    with open(filename) as fh:
        return fh.read().split("\n")

def loadplots(filename="plots"):
    with open(filename) as fh:
        return fh.read().split("<EOS>")
