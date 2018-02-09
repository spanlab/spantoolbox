"""Use me for making a spherical ROI"""
import subprocess

if __name__ == "__main__":
    accept_coords = False
    while(not accept_coords):
        try:
            coords = raw_input("Enter TLRC coordinates (e.g. 34, 25, -5): ")
            coords = [str(int(x)) for x in coords.split(',')]
            if len(coords)==3:
                accept_coords = True
            else:
                continue
        except:
            print("Please enter 3 integers")

    accept_radius = False
    while(not accept_radius):
        try:
            radius = int(raw_input("Enter spherical radius: "))
            accept_radius = True
        except TypeError:
            print("radius must be an integer (1,2,3,4...)")

    name = raw_input("Please enter mask name: ")
    try:
        command = [
            '3dcalc',
            '-a',
            'TT_N27+tlrc',
            '-expr',
            'abs(-step(' + str(radius**2) + "-(x - " + coords[0] + ") * (x - " +  coords[0] + ") - " +
            "( y -" + coords[1] + ") * (y - " +  coords[1] + ") - " +
            "(z - " + coords[2] + ") * (z - " + coords[2] + ")))",
            "-prefix",
            name
        ]
        print command
        subprocess.call(command)
    except:
        print("Except")
    
            
        
